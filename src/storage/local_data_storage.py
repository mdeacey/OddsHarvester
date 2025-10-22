import csv
import json
import logging
import os
from typing import Any, Dict, List, Optional

from .storage_format import StorageFormat
from src.utils.match_fingerprint import MatchFingerprint


class LocalDataStorage:
    """
    A class to handle the storage of scraped data locally in either JSON or CSV format.
    """

    def __init__(
        self, default_file_path: str = "scraped_data.csv", default_storage_format: StorageFormat = StorageFormat.CSV
    ):
        """
        Initialize LocalDataStorage.

        Args:
            default_file_path (str): Default file path to use if none is provided in `save_data`.
            default_storage_format (StorageFormat): Default file format to use if none is provided in StorageFormat.CSV.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_file_path = default_file_path
        self.default_storage_format = default_storage_format

    def save_data(
        self, data: dict | list[dict], file_path: str | None = None, storage_format: StorageFormat | None = None
    ):
        """
        Save scraped data to a local CSV file.

        Args:
            data (Union[Dict, List[Dict]]): The data to save, either as a dictionary or a list of dictionaries.
            file_path (str, optional): The file path to save the data. Defaults to `self.default_file_path`.
            storage_format (StorageFormat, optional): The format to save the data in ("csv" or "json").
            Defaults to `self.default_storage_format`.

        Raises:
            ValueError: If the data is not in the correct format (dict or list of dicts).
            Exception: If an error occurs during file operations.
        """
        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError("Data must be a dictionary or a list of dictionaries.")

        target_file_path = file_path or self.default_file_path
        format_to_use = storage_format.lower() if storage_format else self.default_storage_format.value

        if format_to_use not in [f.value for f in StorageFormat]:
            raise ValueError(
                f"Invalid storage format. Supported formats are: {', '.join(f.value for f in StorageFormat)}."
            )

        if not target_file_path.endswith(f".{format_to_use}"):
            target_file_path = f"{target_file_path}.{format_to_use}"

        # Always use duplicate detection logic
        return self.save_incremental_data(data, target_file_path, StorageFormat(format_to_use))

    def _save_as_csv(self, data: list[dict], file_path: str):
        """Save data in CSV format."""
        try:
            with open(file_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())

                # Write header only if the file is newly created
                if os.path.getsize(file_path) == 0:
                    writer.writeheader()

                writer.writerows(data)

            self.logger.info(f"Successfully saved {len(data)} record(s) to {file_path}")

        except Exception as e:
            self.logger.error(f"Error saving data to {file_path}: {e!s}", exc_info=True)
            raise

    def _save_as_json(self, data: list[dict], file_path: str):
        """Save data in JSON format."""
        try:
            # Load existing data if the file already exists
            existing_data = []

            if os.path.exists(file_path):
                with open(file_path, encoding="utf-8") as file:
                    try:
                        existing_data = json.load(file)
                    except json.JSONDecodeError:
                        self.logger.warning(f"File {file_path} exists but is empty or invalid JSON.")

            combined_data = existing_data + data

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(combined_data, file, indent=4)

            self.logger.info(f"Successfully saved {len(data)} record(s) to {file_path}")

        except Exception as e:
            self.logger.error(f"Error saving data to {file_path}: {e!s}", exc_info=True)
            raise

    def _ensure_directory_exists(self, file_path: str):
        """Ensures the directory for the given file path exists. If it doesn't exist, creates it."""
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def save_incremental_data(self, data: List[Dict[str, Any]], file_path: str, storage_format: StorageFormat,
                             change_results: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save data with incremental logic to avoid duplicates.

        Args:
            data (List[Dict[str, Any]]): Data to save
            file_path (str): Target file path
            storage_format (StorageFormat): Storage format to use
            change_results (Optional[Dict[str, Any]]): Change detection results

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if storage_format == StorageFormat.JSON or storage_format == StorageFormat.JSON.value:
                return self._save_incremental_json(data, file_path, change_results)
            elif storage_format == StorageFormat.CSV or storage_format == StorageFormat.CSV.value:
                return self._save_incremental_csv(data, file_path, change_results)
            else:
                raise ValueError(f"Unsupported storage format: {storage_format}")
        except Exception as e:
            self.logger.error(f"Error in incremental save: {e}")
            return False

    def _save_incremental_json(self, data: List[Dict[str, Any]], file_path: str,
                              change_results: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save data incrementally in JSON format.

        Updates existing records instead of just appending to avoid duplicates.
        """
        try:
            self._ensure_directory_exists(file_path)

            # Load existing data
            existing_data = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                    except json.JSONDecodeError:
                        self.logger.warning(f"File {file_path} is empty or invalid JSON, starting fresh.")
                        existing_data = []

            # Create index of existing records by identity fingerprint
            fingerprint_generator = MatchFingerprint(self.logger)
            existing_index = {}

            for i, record in enumerate(existing_data):
                try:
                    identity_fp = fingerprint_generator.generate_identity_fingerprint(record)
                    existing_index[identity_fp] = i
                except Exception as e:
                    self.logger.warning(f"Error generating fingerprint for existing record: {e}")

            # Update or add new records
            for record in data:
                try:
                    identity_fp = fingerprint_generator.generate_identity_fingerprint(record)

                    if identity_fp in existing_index:
                        # Update existing record
                        existing_index[identity_fp] = len(existing_data)
                        existing_data.append(record)
                        self.logger.debug(f"Updated existing record: {identity_fp[:16]}...")
                    else:
                        # Add new record
                        existing_data.append(record)
                        self.logger.debug(f"Added new record: {identity_fp[:16]}...")

                except Exception as e:
                    self.logger.warning(f"Error processing record for incremental save: {e}")
                    # Fall back to just appending
                    existing_data.append(record)

            # Write updated data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4)

            self.logger.info(f"Successfully saved {len(data)} records incrementally to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving incremental JSON data to {file_path}: {e}")
            return False

    def _save_incremental_csv(self, data: List[Dict[str, Any]], file_path: str,
                             change_results: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save data incrementally in CSV format.

        For CSV, we use a simpler approach: read existing data, filter out duplicates, then append.
        """
        try:
            self._ensure_directory_exists(file_path)

            # Load existing data if file exists
            existing_data = []
            fieldnames = None

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    existing_data = list(reader)

            # Generate fingerprints for existing records
            fingerprint_generator = MatchFingerprint(self.logger)
            existing_fingerprints = set()

            for record in existing_data:
                try:
                    fp = fingerprint_generator.generate_identity_fingerprint(record)
                    existing_fingerprints.add(fp)
                except Exception as e:
                    self.logger.warning(f"Error generating fingerprint for existing CSV record: {e}")

            # Filter out duplicate records from new data
            new_unique_data = []
            duplicates_count = 0

            for record in data:
                try:
                    fp = fingerprint_generator.generate_identity_fingerprint(record)
                    if fp not in existing_fingerprints:
                        new_unique_data.append(record)
                        existing_fingerprints.add(fp)  # Add to set to catch duplicates within new data
                    else:
                        duplicates_count += 1
                except Exception as e:
                    self.logger.warning(f"Error processing CSV record: {e}")
                    new_unique_data.append(record)  # Include record if fingerprinting fails

            if duplicates_count > 0:
                self.logger.info(f"Filtered out {duplicates_count} duplicate records from CSV save")

            # Determine fieldnames
            if new_unique_data:
                if fieldnames:
                    # Merge fieldnames from existing and new data
                    new_fieldnames = set(fieldnames)
                    for record in new_unique_data:
                        new_fieldnames.update(record.keys())
                    fieldnames = sorted(list(new_fieldnames))
                else:
                    # Use fieldnames from new data
                    all_keys = set()
                    for record in new_unique_data:
                        all_keys.update(record.keys())
                    fieldnames = sorted(list(all_keys))

            # Append new unique data
            with open(file_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # Write header only if file is newly created
                if os.path.getsize(file_path) == 0:
                    writer.writeheader()

                writer.writerows(new_unique_data)

            self.logger.info(f"Successfully saved {len(new_unique_data)} new records to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving incremental CSV data to {file_path}: {e}")
            return False
