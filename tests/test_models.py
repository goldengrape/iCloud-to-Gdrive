from rmd.models import MigrationStatus, TransferItem, ManifestRecord, PlatformCapabilities, DriveUploadSession

def test_migration_status_enum():
    assert MigrationStatus.VERIFIED_MATCH == "VERIFIED_MATCH"
    assert MigrationStatus.FAILED_UNKNOWN == "FAILED_UNKNOWN"

def test_transfer_item_creation():
    item = TransferItem(
        task_id="task_1",
        record_id="rec_1",
        source_type="icloud_drive",
        source_display_name="test.txt",
        resource_kind="file",
        source_size=1024
    )
    assert item.record_id == "rec_1"
    assert item.source_size == 1024

def test_manifest_record_creation():
    # TDD-TEST-015: manifest 字段完整
    record = ManifestRecord(
        task_id="task_1",
        record_id="rec_1",
        source_type="icloud_drive",
        source_display_name="test.txt",
        source_size=1024,
        resource_kind="file",
        status=MigrationStatus.VERIFIED_MATCH,
        record_hash="abcdef123"
    )
    assert record.status == MigrationStatus.VERIFIED_MATCH
    assert record.record_hash == "abcdef123"
