import io
import pytest
from unittest.mock import MagicMock, call
from rmd.engine import MigrationEngine
from rmd.models import TransferItem, MigrationStatus, ManifestRecord
from rmd.windows_drive import WinFileEvent
from rmd.verification import DriveFileMetadata
from rmd.adapters import DriveUploadResult

def test_engine_skips_placeholder_and_verified():
    source = MagicMock()
    target = MagicMock()
    store = MagicMock()
    
    # Setup source to return one placeholder and two valid files
    placeholder = WinFileEvent(record_id="p1", status=MigrationStatus.SOURCE_PLACEHOLDER, path="C:\\p1.txt", message="skipped")
    item1 = TransferItem(task_id="t1", record_id="r1", source_type="test", source_display_name="f1.txt", resource_kind="file", source_size=10, source_path="C:\\f1.txt")
    item2 = TransferItem(task_id="t1", record_id="r2", source_type="test", source_display_name="f2.txt", resource_kind="file", source_size=10, source_path="C:\\f2.txt")
    
    source.list_items.return_value = [placeholder, item1, item2]
    
    # Store: let item1 be VERIFIED_MATCH, item2 be None
    verified_record = ManifestRecord(
        task_id="t1", 
        record_id="r1", 
        source_type="test", 
        source_display_name="f1.txt", 
        source_size=10, 
        resource_kind="file", 
        status=MigrationStatus.VERIFIED_MATCH,
        record_hash=""
    )
    
    def mock_get_record(record_id):
        if record_id == "r1":
            return verified_record
        return None
    
    store.get_record.side_effect = mock_get_record
    
    # For item2, we need to mock open_stream
    source.open_stream.return_value = (io.BytesIO(b"0123456789"), {"size": 10})
    
    # Target: success upload for item2
    target.upload.return_value = DriveUploadResult(
        is_completed=True,
        target_drive_file_id="did1",
        metadata=DriveFileMetadata(
            size=10,
            md5Checksum="84d89877f0d4041efb6bf91a16f0248f2fd573e6af05c19f96bedb9f882f7882", # bad md5 for test
            sha256Checksum="84d89877f0d4041efb6bf91a16f0248f2fd573e6af05c19f96bedb9f882f7882" # real sha256 of "0123456789"
        )
    )
    
    engine = MigrationEngine(source, target, store)
    engine.run("t1")
    
    # Assertions
    # Placeholder should be saved
    assert store.save_record.call_count == 3 
    
    # target.upload called exactly once for r2
    target.upload.assert_called_once()
    assert target.upload.call_args[0][0].record_id == "r2"

    # check final record save for r2
    final_record = store.save_record.call_args_list[-1][0][0]
    assert final_record.record_id == "r2"
    assert final_record.status == MigrationStatus.VERIFIED_MATCH
