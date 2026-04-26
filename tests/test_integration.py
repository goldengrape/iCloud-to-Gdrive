import pytest
from datetime import datetime, timezone
from rmd.models import TransferItem, ManifestRecord, MigrationStatus
from rmd.adapters import FakeSourceAdapter, FakeTargetAdapter
from rmd.verification import VerificationEngine, SourceDigest
from rmd.store import TaskStore, ManifestWriter

def test_full_migration_flow(tmp_path):
    # TDD-TEST-002: 本地传输路径 (Mocked to simulate local-only logic)
    task_id = "test_task_1"

    # 1. Setup Data
    item1 = TransferItem(
        task_id=task_id, record_id="rec_1", source_type="icloud_drive",
        source_display_name="file1.txt", resource_kind="file", source_size=5
    )
    data1 = b"hello"

    source = FakeSourceAdapter([(item1, data1)])
    target = FakeTargetAdapter()
    store = TaskStore()

    # 2. Process
    for item in source.list_items():
        # Initialize Record
        record = ManifestRecord(
            task_id=item.task_id, record_id=item.record_id, source_type=item.source_type,
            source_display_name=item.source_display_name, source_size=item.source_size,
            resource_kind=item.resource_kind, status=MigrationStatus.PENDING, record_hash="",
            started_at=datetime.now(timezone.utc).isoformat()
        )
        store.save_record(record)

        # Stream & Hash
        stream, _ = source.open_stream(item.record_id)
        digest = VerificationEngine.calculate_digest_from_stream(stream)
        record.source_md5 = digest.md5
        record.source_sha256 = digest.sha256

        # Rewind stream for upload
        stream.seek(0)

        # Upload
        record.status = MigrationStatus.TRANSFERRING
        store.save_record(record)

        upload_result = target.upload(item, stream)

        if upload_result.is_completed:
            record.target_drive_file_id = upload_result.target_drive_file_id
            record.target_size = upload_result.metadata.size
            record.target_md5 = upload_result.metadata.md5Checksum
            record.target_sha256 = upload_result.metadata.sha256Checksum
            record.uploaded_at = datetime.now(timezone.utc).isoformat()

            # Verify
            verify_status = VerificationEngine.verify(digest, upload_result.metadata)
            record.status = verify_status
            record.verified_at = datetime.now(timezone.utc).isoformat()

            store.save_record(record)

    # 3. Assert State
    records = store.list_records(task_id)
    assert len(records) == 1
    assert records[0].status == MigrationStatus.VERIFIED_MATCH
    assert records[0].target_drive_file_id is not None

    # 4. Finalize Manifest
    json_path = tmp_path / "manifest.json"
    csv_path = tmp_path / "manifest.csv"
    manifest_hash = ManifestWriter.finalize(records, str(json_path), str(csv_path))

    assert json_path.exists()
