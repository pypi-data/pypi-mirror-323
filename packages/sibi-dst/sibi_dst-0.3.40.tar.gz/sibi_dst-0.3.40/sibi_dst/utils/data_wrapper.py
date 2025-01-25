import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Type, Any, Dict, Optional, Union
from threading import Lock
import fsspec
import pandas as pd
from IPython.display import display
from tqdm import tqdm

from sibi_dst.utils import Logger, DateUtils
from sibi_dst.utils import ParquetSaver


class DataWrapper:
    """
    Utility class for handling file-based operations, including processing and saving data
    in Parquet format, while managing a hierarchy of conditions such as overwrite, history
    threshold, and missing file detection.

    This class aims to simplify the process of managing large datasets stored in a filesystem.
    It allows for controlled updates to data files based on parameters set by the user, with
    support for different filesystem types and options.

    It also provides features like logging actions, managing processing threads, generating
    update plans, checking file age, and dynamically creating date ranges for data operations.

    The design supports flexible integration with user-defined classes (dataclasses) to define
    custom loading and processing behavior.

    :ivar dataclass: The user-defined class for data processing.
    :type dataclass: Type
    :ivar date_field: The name of the date field in the user-defined class.
    :type date_field: str
    :ivar data_path: Base path for the dataset storage.
    :type data_path: str
    :ivar parquet_filename: File name for the Parquet file.
    :type parquet_filename: str
    :ivar start_date: Start date for processing.
    :type start_date: datetime.date
    :ivar end_date: End date for processing.
    :type end_date: datetime.date
    :ivar fs: File system object for managing files.
    :type fs: Optional[fsspec.AbstractFileSystem]
    :ivar filesystem_type: Type of the filesystem (e.g., "file", "s3").
    :type filesystem_type: str
    :ivar filesystem_options: Additional options for initializing the filesystem.
    :type filesystem_options: Optional[Dict]
    :ivar verbose: Flag to enable verbose logging.
    :type verbose: bool
    :ivar class_params: Parameters to initialize the dataclass.
    :type class_params: Optional[Dict]
    :ivar load_params: Additional parameters for loading functions.
    :type load_params: Optional[Dict]
    :ivar reverse_order: Flag to reverse the order of date range generation.
    :type reverse_order: bool
    :ivar overwrite: Whether to overwrite all files during processing.
    :type overwrite: bool
    :ivar ignore_missing: Whether to ignore missing files.
    :type ignore_missing: bool
    :ivar logger: Logger instance for logging information.
    :type logger: Optional[Logger]
    :ivar max_age_minutes: Maximum file age threshold in minutes.
    :type max_age_minutes: int
    :ivar history_days_threshold: Number of days for the history threshold.
    :type history_days_threshold: int
    :ivar show_progress: Flag to enable progress display.
    :type show_progress: bool
    :ivar timeout: Timeout in seconds for processing tasks with threads.
    :type timeout: Optional[int]
    """
    DEFAULT_MAX_AGE_MINUTES = 1440
    DEFAULT_HISTORY_DAYS_THRESHOLD = 30

    def __init__(self,
                 dataclass: Type,
                 date_field: str,
                 data_path: str,
                 parquet_filename: str,
                 start_date: Any,
                 end_date: Any,
                 fs: Optional[fsspec.AbstractFileSystem] = None,
                 filesystem_type: str = "file",
                 filesystem_options: Optional[Dict] = None,
                 verbose: bool = False,
                 class_params: Optional[Dict] = None,
                 load_params: Optional[Dict] = None,
                 reverse_order: bool = False,
                 overwrite: bool = False,
                 ignore_missing: bool = False,
                 logger: Logger = None,
                 max_age_minutes: int = DEFAULT_MAX_AGE_MINUTES,
                 history_days_threshold: int = DEFAULT_HISTORY_DAYS_THRESHOLD,
                 show_progress: bool = False,
                 timeout: float = 60):
        self.dataclass = dataclass
        self.date_field = date_field
        self.data_path = self.ensure_forward_slash(data_path)
        self.parquet_filename = parquet_filename
        self.filesystem_type = filesystem_type
        self.filesystem_options = filesystem_options or {}
        self.fs = fs
        self.verbose = verbose
        self.class_params = class_params or {}
        self.load_params = load_params or {}
        self.reverse_order = reverse_order
        self.overwrite = overwrite
        self.ignore_missing = ignore_missing
        self.logger = logger or Logger.default_logger(logger_name=self.dataclass.__name__)
        self.max_age_minutes = max_age_minutes
        self.history_days_threshold = history_days_threshold
        self.show_progress = show_progress
        self.timeout = timeout

        self.start_date = self.convert_to_date(start_date)
        self.end_date = self.convert_to_date(end_date)
        self._lock = Lock()
        self.processed_dates = []
        self.date_utils = DateUtils(logger=self.logger)
        if self.fs is None:
            with self._lock:
                if self.fs is None:
                    self.fs = fsspec.filesystem(self.filesystem_type, **self.filesystem_options)

    @staticmethod
    def convert_to_date(date: Union[datetime.date, str]) -> datetime.date:
        if isinstance(date, datetime.date):
            return date
        try:
            return pd.to_datetime(date).date()
        except ValueError as e:
            raise ValueError(f"Error converting {date} to datetime: {e}")

    @staticmethod
    def ensure_forward_slash(path: str) -> str:
        return path if path.endswith('/') else path + '/'

    def generate_date_range(self):
        """Generate a range of dates between start_date and end_date."""
        date_range = pd.date_range(self.start_date, self.end_date, freq='D')
        if self.reverse_order:
            date_range = date_range[::-1]
        for date in date_range:
            yield date.date()

    def process(self, max_retries: int = 3):
        """
        Processes update tasks by generating an update plan, filtering required updates, and distributing
        the workload across threads based on priority levels.

        This method operates by assessing required updates through generated conditions,
        grouping them by priority levels, and processing them in parallel threads.
        Each thread handles the updates for a specific priority level, ensuring a streamlined approach
        to handling the updates efficiently.

        :param max_retries: Maximum number of retries for a task after a timeout. Defaults to 3.
        :raises TimeoutError: If a thread processing a priority level exceeds the allowed timeout duration.
        :return: None
        """
        update_plan_table = self.generate_update_plan_with_conditions()

        # Filter out rows that do not require updates (priority 0 means skip)
        with self._lock:
            update_plan_table = update_plan_table[
                (update_plan_table["update_required"] == True) & (update_plan_table["update_priority"] != 0)
                ]
        # Display the update plan table to the user if requested
        if len(update_plan_table.index) == 0:
            return
        if self.show_progress:
            display(update_plan_table)
        # Group by priority
        with self._lock:
            priorities = sorted(update_plan_table["update_priority"].unique())

        # We will process each priority level in its own thread.
        # Each thread will handle all dates associated with that priority.
        def process_priority(priority):
            # Extract dates for the current priority
            dates_to_process = update_plan_table[
                update_plan_table["update_priority"] == priority
                ]["date"].tolist()

            # If show_progress is True, wrap in a progress bar
            date_iterator = dates_to_process
            if self.show_progress:
                date_iterator = tqdm(date_iterator,
                                     desc=f"Processing priority {priority}:{self.dataclass.__name__}",
                                     unit="date")

            # Process each date for this priority
            for current_date in date_iterator:
                self.process_date(current_date)

        # Launch a separate thread for each priority
        with ThreadPoolExecutor(max_workers=len(priorities)) as executor:
            futures = {executor.submit(process_priority, p): p for p in priorities}
            retries = {p: 0 for p in priorities}  # Track retry counts for each priority

            while futures:
                for future in list(futures.keys()):
                    try:
                        future.result(timeout=self.timeout)
                        del futures[future]  # Remove completed future
                    except TimeoutError:
                        priority = futures[future]
                        retries[priority] += 1

                        if retries[priority] <= max_retries:
                            self.logger.warning(
                                f"Thread for priority {priority} timed out. Retrying ({retries[priority]}/{max_retries})..."
                            )
                            new_future = executor.submit(process_priority, priority)
                            futures[new_future] = priority
                        else:
                            self.logger.error(
                                f"Thread for priority {priority} timed out. Max retries ({max_retries}) exceeded. Skipping."
                            )
                        del futures[future]  # Remove the timed-out future
                    except Exception as e:
                        self.logger.error(f"Error processing priority {futures[future]}: {e}")
                        del futures[future]  # Remove the failed future

    def process_date(self, date: datetime.date):
        """
        Processes data for a given date and saves it as a Parquet file.

        This method processes data for the specified date by loading the data
        corresponding to that day, saving it into a structured storage format
        (Parquet), and logging relevant information such as processing time
        and errors that may occur during the process. It uses provided
        dataclass and parameters to operate and ensures the data is stored
        in a structured folder hierarchy.

        :param date: The specific date for which data processing and saving should occur
        :type date: datetime.date
        :return: None
        """
        folder = f'{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/'
        full_parquet_filename = f"{folder}{self.parquet_filename}"

        start_time = datetime.datetime.now()
        self.logger.info(f"Processing date: {date}")
        self.logger.info(f"Processing {full_parquet_filename}...")

        data_object = self.dataclass(**self.class_params)
        df = data_object.load_period(dt_field=self.date_field, start=date, end=date)

        if len(df.index) == 0:
            self.logger.error("No data found for the specified date.")
            return

        with self._lock:
            parquet_saver = ParquetSaver(df, parquet_storage_path=folder, logger=self.logger, fs=self.fs)
            parquet_saver.save_to_parquet(self.parquet_filename, clear_existing=True)

            end_time = datetime.datetime.now()
            duration_seconds = (end_time - start_time).total_seconds()
            self.logger.info(
                f"Data saved to {full_parquet_filename}. Processing time: {duration_seconds:.2f} seconds"
            )

            self.processed_dates.append(date)
        self.logger.info(f"Finished processing date: {date}")

    def generate_update_plan_with_conditions(self):
        """
        Generates an update plan for data files based on specific conditions. The function evaluates the need for updating or
        overwriting data files for a given date range. Conditions include file existence, whether the file falls within a
        specified historical threshold, and the necessity to overwrite or handle missing files. A priority map is utilized to
        assign priority levels to update categories.

        :raises FileNotFoundError: If any file is referenced that does not exist and the ``ignore_missing`` property is set to False.
        :raises AttributeError: If any required attribute like ``fs``, ``dataclass``, or others are not properly set or initialized.

        :return: A Pandas DataFrame representing the update plan, where each row contains information about a date, the conditions
            evaluated for that date, and the determined update priority.
        :rtype: pandas.DataFrame
        """
        rows = []

        today = datetime.date.today()
        history_start_date = today - datetime.timedelta(days=self.history_days_threshold)
        priority_map = {
            "file is recent":0,
            "overwrite": 1,
            "history_days": 2,
            "missing_files": 3
        }
        date_range = self.generate_date_range()
        if self.show_progress:
            date_range = tqdm(date_range, desc=f"Evaluating update plan:{self.dataclass.__name__}", unit="date")

        for current_date in date_range:
            folder = f'{self.data_path}{current_date.year}/{current_date.month:02d}/{current_date.day:02d}/'
            full_parquet_filename = f"{folder}{self.parquet_filename}"

            file_exists = self.fs.exists(full_parquet_filename)
            within_history = history_start_date <= current_date <= today
            missing_file = not file_exists and not self.ignore_missing
            category = None
            update_required = False

            # Hierarchy 1: Overwrite
            if self.overwrite:
                category = "overwrite"
                update_required = True
            elif missing_file and current_date < today:
                category = "missing_files"
                update_required = True

            elif within_history:
                if file_exists:
                    if self.date_utils.is_file_older_than(
                        full_parquet_filename,
                        max_age_minutes=self.max_age_minutes,
                        fs=self.fs,
                        ignore_missing=self.ignore_missing,
                        verbose=self.verbose
                    ):
                        category = "history_days"
                        update_required = True
                    else:
                        category = "file is recent"
                        update_required = False
                else:
                    category = "missing_files"
                    update_required = True
            else:
                category = "No Update Required"
                update_required = False

            # Collect condition descriptions for the update plan table
            row = {
                "date": current_date,
                "file_exists": file_exists,
                "within_history": within_history,
                "missing_file": missing_file,
                "update_required": update_required,
                "update_category": category,
                "datawrapper class": self.dataclass.__name__,
                "update_priority": priority_map.get(category, 0)
            }
            rows.append(row)

        update_plan_table = pd.DataFrame(rows)
        return update_plan_table

# # wrapper.process()
# # wrapper = DataWrapper(
# #    dataclass=YourDataClass,
# #    date_field="created_at",
# #    data_path="s3://your-bucket-name/path/to/data",
# #    parquet_filename="data.parquet",
# #    start_date="2022-01-01",
# #    end_date="2022-12-31",
# #    filesystem_type="s3",
# #    filesystem_options={
# #        "key": "your_aws_access_key",
# #        "secret": "your_aws_secret_key",
# #        "client_kwargs": {"endpoint_url": "https://s3.amazonaws.com"}
# #    },
# #    verbose=True
# #)
# #wrapper.process()
