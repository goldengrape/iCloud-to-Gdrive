import pytest
from rmd.macos_drive import MockMacICloudDriveAdapter, ICloudFileEvent
from rmd.models import TransferItem, MigrationStatus

def test_macos_icloud_drive_placeholder():
    # TDD-TEST-003: macOS iCloud Drive 占位文件状态
    mock_fs = {
        "/Users/test/Library/Mobile Documents/com~apple~CloudDocs/test.txt": {"size": 100, "data": b"123"},
        "/Users/test/Library/Mobile Documents/com~apple~CloudDocs/.test.txt.iCloud": {"size": 0, "placeholder": True},
        "/Users/test/Library/Mobile Documents/com~apple~CloudDocs/secret.txt": {"size": 100, "unreadable": True}
    }

    adapter = MockMacICloudDriveAdapter(mock_fs)
    items = list(adapter.list_items())

    assert len(items) == 3

    normal_file = next(i for i in items if isinstance(i, TransferItem) and i.source_display_name == "test.txt")
    assert normal_file.source_size == 100

    placeholder = next(i for i in items if isinstance(i, ICloudFileEvent) and i.path.endswith(".iCloud"))
    assert placeholder.status == MigrationStatus.SOURCE_PLACEHOLDER

    unreadable = next(i for i in items if isinstance(i, ICloudFileEvent) and i.path.endswith("secret.txt"))
    assert unreadable.status == MigrationStatus.FAILED_SOURCE_READ
