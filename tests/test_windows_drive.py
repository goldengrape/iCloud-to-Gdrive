import pytest
from rmd.windows_drive import MockWindowsICloudAdapter, WinFileEvent
from rmd.models import TransferItem, MigrationStatus

def test_windows_icloud_undownloaded_file():
    # TDD-TEST-004: Windows 未下载文件处理
    mock_fs = {
        "C:\\Users\\test\\iCloudDrive\\ready.txt": {"size": 100, "downloaded": True},
        "C:\\Users\\test\\iCloudDrive\\cloud_only.txt": {"size": 0, "downloaded": False}
    }

    adapter = MockWindowsICloudAdapter(mock_fs)
    items = list(adapter.list_items())

    assert len(items) == 2

    ready = next(i for i in items if isinstance(i, TransferItem))
    assert ready.source_display_name == "ready.txt"

    cloud_only = next(i for i in items if isinstance(i, WinFileEvent))
    assert cloud_only.status == MigrationStatus.SOURCE_PLACEHOLDER
    assert "Please keep it on this device" in cloud_only.message
