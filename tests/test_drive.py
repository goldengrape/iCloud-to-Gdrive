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
    session_uri = result1.session_uri
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

from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
import httplib2
from rmd.drive import RealGoogleDriveAdapter, DriveError

@patch('rmd.drive.build')
def test_real_drive_adapter_upload_success(mock_build):
    mock_auth = MagicMock()
    mock_auth.get_credentials.return_value.valid = True

    # Setup mocks
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_files = mock_service.files.return_value
    # mock list for folder search (return empty to trigger creation)
    mock_files.list.return_value.execute.return_value = {'files': []}
    # mock create for folder
    mock_files.create.return_value.execute.return_value = {'id': 'folder_id_123'}
    
    # mock create for file upload
    mock_request = MagicMock()
    mock_files.create.return_value = mock_request
    
    # mock next_chunk sequence
    mock_request.next_chunk.side_effect = [
        (MagicMock(resumable_progress=5), None),
        (MagicMock(resumable_progress=10), {'id': 'file_id_456', 'size': '10', 'md5Checksum': 'md5', 'sha256Checksum': 'sha256', 'headRevisionId': 'rev1'})
    ]

    adapter = RealGoogleDriveAdapter(mock_auth, folder_name="Test-Folder")
    item = TransferItem(task_id="t1", record_id="r1", source_type="icloud", source_display_name="test.txt", resource_kind="file", source_size=10)
    stream = io.BytesIO(b"0123456789")

    result = adapter.upload(item, stream)

    assert result.is_completed is True
    assert result.target_drive_file_id == 'file_id_456'
    assert result.metadata.size == 10
    assert result.metadata.md5Checksum == 'md5'

@patch('rmd.drive.build')
def test_real_drive_adapter_upload_rate_limit(mock_build):
    mock_auth = MagicMock()
    mock_auth.get_credentials.return_value.valid = True

    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_files = mock_service.files.return_value
    mock_files.list.return_value.execute.return_value = {'files': [{'id': 'folder_id_123'}]}
    
    mock_request = MagicMock()
    mock_files.create.return_value = mock_request
    mock_request.resumable_uri = 'https://resumable.uri/123'
    
    # mock next_chunk throwing rate limit
    resp = httplib2.Response({'status': '429'})
    error = HttpError(resp, b'Rate Limit Exceeded')
    mock_request.next_chunk.side_effect = error

    adapter = RealGoogleDriveAdapter(mock_auth)
    item = TransferItem(task_id="t1", record_id="r1", source_type="icloud", source_display_name="test.txt", resource_kind="file", source_size=10)
    stream = io.BytesIO(b"0123456789")

    result = adapter.upload(item, stream)

    assert result.is_completed is False
    assert result.error == "UPLOAD_PAUSED_RATE_LIMIT"
    assert result.session_uri == 'https://resumable.uri/123'
