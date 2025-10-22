import logging
from typing import Any, Dict, List, Optional

from src.storage.storage_format import StorageFormat
from src.storage.storage_type import StorageType

logger = logging.getLogger("StorageManager")


def store_data(storage_type: StorageType, data: list, storage_format: StorageFormat, file_path: str,
              change_results: Optional[Dict[str, Any]] = None) -> bool:
    """
    Handles storing data in the chosen storage type with duplicate detection.

    Args:
        storage_type (StorageType): Type of storage (local or remote)
        data (list): Data to store
        storage_format (StorageFormat): Storage format (JSON or CSV)
        file_path (str): Target file path
        change_results (Optional[Dict[str, Any]]): Change detection results

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        storage_enum = StorageType(storage_type)
        storage = storage_enum.get_storage_instance()

        if storage_type == StorageType.REMOTE.value:
            storage.process_and_upload(data=data, file_path=file_path)
        else:
            if hasattr(storage, 'save_incremental_data'):
                success = storage.save_incremental_data(
                    data=data,
                    file_path=file_path,
                    storage_format=storage_format,
                    change_results=change_results
                )
                if success:
                    logger.info(f"Successfully stored {len(data)} records with duplicate detection.")
                    return True
            else:
                storage.save_data(data=data, file_path=file_path, storage_format=storage_format)
                logger.info(f"Successfully stored {len(data)} records.")
                return True

        return True

    except Exception as e:
        logger.error(f"Error during data storage: {e!s}")
        return False
