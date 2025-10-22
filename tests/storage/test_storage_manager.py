from unittest.mock import MagicMock, patch

import pytest

from src.storage.storage_format import StorageFormat
from src.storage.storage_manager import store_data
from src.storage.storage_type import StorageType


@pytest.fixture
def sample_data():
    return [{"id": 1, "value": 100}, {"id": 2, "value": 200}]


@pytest.fixture
def mock_storage():
    return MagicMock()


def test_store_data_local_storage(sample_data, mock_storage):
    with patch("src.storage.storage_type.StorageType.get_storage_instance", return_value=mock_storage):
        result = store_data(StorageType.LOCAL.value, sample_data, StorageFormat.JSON, "test.json")

        # Should use save_incremental_data if available
        if hasattr(mock_storage, 'save_incremental_data'):
            mock_storage.save_incremental_data.assert_called_once_with(
                data=sample_data, file_path="test.json", storage_format=StorageFormat.JSON, change_results=None
            )
        else:
            mock_storage.save_data.assert_called_once_with(
                data=sample_data, file_path="test.json", storage_format=StorageFormat.JSON
            )
        assert result is True


def test_store_data_remote_storage(sample_data, mock_storage):
    with patch("src.storage.storage_type.StorageType.get_storage_instance", return_value=mock_storage):
        result = store_data(StorageType.REMOTE.value, sample_data, StorageFormat.JSON, "test.json")

        mock_storage.process_and_upload.assert_called_once_with(data=sample_data, file_path="test.json")
        assert result is True


def test_store_data_invalid_storage(sample_data):
    with patch("src.storage.storage_manager.logger") as mock_logger:
        result = store_data("INVALID_STORAGE", sample_data, StorageFormat.JSON, "test.json")

        mock_logger.error.assert_called_once()
        assert result is False


def test_store_data_exception_handling(sample_data, mock_storage):
    mock_storage.save_incremental_data.side_effect = Exception("Storage error")

    with (
        patch("src.storage.storage_type.StorageType.get_storage_instance", return_value=mock_storage),
        patch("src.storage.storage_manager.logger") as mock_logger,
    ):
        result = store_data(StorageType.LOCAL.value, sample_data, StorageFormat.JSON, "test.json")

        mock_logger.error.assert_called_once()
        assert result is False


def test_store_data_with_change_results(sample_data, mock_storage):
    """Test storing data with change detection results."""
    change_results = {"match_0": {"state": "UNCHANGED"}}

    # Mock storage with incremental capability
    mock_storage.save_incremental_data = MagicMock(return_value=True)
    mock_storage.hasattr = MagicMock(return_value=True)

    with patch("src.storage.storage_type.StorageType.get_storage_instance", return_value=mock_storage):
        result = store_data(
            StorageType.LOCAL.value,
            sample_data,
            StorageFormat.JSON,
            "test.json",
            change_results=change_results
        )

        mock_storage.save_incremental_data.assert_called_once_with(
            data=sample_data,
            file_path="test.json",
            storage_format=StorageFormat.JSON,
            change_results=change_results
        )
        assert result is True


def test_store_data_local_storage_fallback_to_regular_save(sample_data, mock_storage):
    """Test fallback to regular save_data when incremental is not available."""
    # Storage without incremental capability
    mock_storage.save_data = MagicMock(return_value=True)
    del mock_storage.save_incremental_data  # Remove incremental method

    with patch("src.storage.storage_type.StorageType.get_storage_instance", return_value=mock_storage):
        result = store_data(StorageType.LOCAL.value, sample_data, StorageFormat.JSON, "test.json")

        mock_storage.save_data.assert_called_once_with(
            data=sample_data, file_path="test.json", storage_format=StorageFormat.JSON
        )
        assert result is True
