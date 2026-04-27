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

import os
import io
from pathlib import Path
from unittest.mock import patch, MagicMock
from rmd.windows_drive import RealWindowsICloudAdapter

def test_real_windows_icloud_adapter_normal_file(tmp_path):
    # TDD-TEST-004: Windows 正常文件处理
    root_dir = tmp_path / "iCloudDrive"
    root_dir.mkdir()
    
    test_file = root_dir / "ready.txt"
    test_file.write_text("hello")

    adapter = RealWindowsICloudAdapter(root_dir=str(root_dir))
    items = list(adapter.list_items())

    assert len(items) == 1
    assert isinstance(items[0], TransferItem)
    assert items[0].source_display_name == "ready.txt"
    assert items[0].source_size == 5

    # Test open_stream
    stream, meta = adapter.open_stream(items[0].record_id)
    assert meta["size"] == 5
    assert stream.read() == b"hello"
    stream.close()

def test_real_windows_icloud_adapter_icloud_extension(tmp_path):
    root_dir = tmp_path / "iCloudDrive"
    root_dir.mkdir()
    
    test_file = root_dir / "cloud_only.txt.iCloud"
    test_file.write_text("placeholder")

    adapter = RealWindowsICloudAdapter(root_dir=str(root_dir))
    items = list(adapter.list_items())

    assert len(items) == 1
    assert isinstance(items[0], WinFileEvent)
    assert items[0].status == MigrationStatus.SOURCE_PLACEHOLDER

def test_real_windows_icloud_adapter_offline_attribute(tmp_path):
    root_dir = tmp_path / "iCloudDrive"
    root_dir.mkdir()
    
    test_file = root_dir / "cloud_only.txt"
    test_file.write_text("placeholder")

    adapter = RealWindowsICloudAdapter(root_dir=str(root_dir))
    
    orig_stat = os.stat
    def mocked_stat(path, *args, **kwargs):
        if str(path).endswith("cloud_only.txt"):
            res = MagicMock()
            res.st_file_attributes = 0x1000
            res.st_mode = 33188 # regular file
            return res
        return orig_stat(path, *args, **kwargs)

    with patch('rmd.windows_drive.os.stat', side_effect=mocked_stat):
        items = list(adapter.list_items())

    assert len(items) == 1
    assert isinstance(items[0], WinFileEvent)
    assert items[0].status == MigrationStatus.SOURCE_PLACEHOLDER
