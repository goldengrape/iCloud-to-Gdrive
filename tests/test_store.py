import os
import json
from rmd.store import TaskStore, ManifestWriter
from rmd.models import ManifestRecord, MigrationStatus, DriveUploadSession

def test_task_store():
    store = TaskStore()
    record = ManifestRecord(
        task_id="task1",
        record_id="rec1",
        source_type="icloud_drive",
        source_display_name="test.txt",
        source_size=100,
        resource_kind="file",
        status=MigrationStatus.PENDING,
        record_hash=""
    )
    store.save_record(record)

    loaded = store.get_record("rec1")
    assert loaded is not None
    assert loaded.record_id == "rec1"
    assert loaded.status == MigrationStatus.PENDING

    session = DriveUploadSession(
        record_id="rec1",
        upload_session_uri="http://example.com",
        target_parent_folder_id="folder1",
        confirmed_offset=0,
        session_created_at="2023-01-01T00:00:00Z",
        last_checked_at="2023-01-01T00:00:00Z"
    )
    store.save_upload_session(session)
    loaded_session = store.get_upload_session("rec1")
    assert loaded_session is not None
    assert loaded_session.upload_session_uri == "http://example.com"

def test_manifest_writer(tmp_path):
    record1 = ManifestRecord(
        task_id="task1",
        record_id="rec1",
        source_type="icloud_drive",
        source_display_name="test.txt",
        source_size=100,
        resource_kind="file",
        status=MigrationStatus.VERIFIED_MATCH,
        record_hash=""
    )

    json_path = tmp_path / "manifest.json"
    csv_path = tmp_path / "manifest.csv"

    manifest_hash = ManifestWriter.finalize([record1], str(json_path), str(csv_path))

    assert json_path.exists()
    assert csv_path.exists()

    with open(json_path, 'r') as f:
        data = json.load(f)
        assert data["metadata"]["record_count"] == 1
        assert data["metadata"]["manifest_sha256"] == manifest_hash
        assert data["records"][0]["record_hash"] != "" # Hash was computed
