import io
import pytest
from rmd.drive import MockGoogleDriveAdapter
from rmd.models import TransferItem

def test_multipart_upload_small_file():
    adapter = MockGoogleDriveAdapter()
    item = TransferItem(
        task_id="t1", record_id="r1", source_type="icloud",
        source_display_name="small.txt", resource_kind="file", source_size=10
    )
    stream = io.BytesIO(b"0123456789")

    result = adapter.upload(item, stream)
    assert result.is_completed is True
    assert result.metadata.size == 10

def test_resumable_upload_large_file():
    # TDD-TEST-009: resumable upload session 持久化 (Mock logic)
    adapter = MockGoogleDriveAdapter()

    # 6MB file
    size = 6 * 1024 * 1024
    item = TransferItem(
        task_id="t1", record_id="r1", source_type="icloud",
        source_display_name="large.bin", resource_kind="file", source_size=size
    )
    stream = io.BytesIO(b"0" * size)

    # Init
    result1 = adapter.upload(item, stream)
    assert result1.is_completed is False
    session_uri = result1.error
    assert session_uri.startswith("https://mock.upload.drive/")

    # Resume / Chunk 1 (Simulate partial upload failure)
    stream.seek(0)
    stream.truncate(size // 2)
    stream.seek(0)
    result2 = adapter.upload(item, stream, session_uri=session_uri)
    assert result2.is_completed is False
    assert result2.confirmed_offset == size // 2

    # Complete
    stream = io.BytesIO(b"0" * size) # Restore full stream
    result3 = adapter.upload(item, stream, session_uri=session_uri)
    assert result3.is_completed is True
    assert result3.confirmed_offset == size
    assert result3.metadata.size == size

def test_upload_rate_limit():
    # TDD-TEST-016: 限流退避
    adapter = MockGoogleDriveAdapter()
    adapter.fail_next_upload_with = "RATE_LIMIT"

    item = TransferItem(
        task_id="t1", record_id="r1", source_type="icloud",
        source_display_name="test.txt", resource_kind="file", source_size=10
    )
    stream = io.BytesIO(b"0123456789")

    result = adapter.upload(item, stream)
    assert result.error == "UPLOAD_PAUSED_RATE_LIMIT"

def test_upload_quota():
    # TDD-TEST-017: 配额暂停
    adapter = MockGoogleDriveAdapter()
    adapter.fail_next_upload_with = "QUOTA"

    item = TransferItem(
        task_id="t1", record_id="r1", source_type="icloud",
        source_display_name="test.txt", resource_kind="file", source_size=10
    )
    stream = io.BytesIO(b"0123456789")

    result = adapter.upload(item, stream)
    assert result.error == "UPLOAD_PAUSED_QUOTA"
