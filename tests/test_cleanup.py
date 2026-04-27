import pytest
from rmd.cleanup import CleanupAdvisor
from rmd.models import ManifestRecord, MigrationStatus
from rmd.verification import DriveFileMetadata

def test_cleanup_advisor_reverification():
    # TDD-TEST-018: 清理列表目标复核

    records = [
        # Match still exists and valid
        ManifestRecord(
            task_id="t1", record_id="r1", source_type="icloud", source_display_name="valid.txt",
            source_size=10, resource_kind="file", status=MigrationStatus.VERIFIED_MATCH, record_hash="",
            target_drive_file_id="fid_1", target_size=10, target_sha256="hash1"
        ),
        # Target deleted
        ManifestRecord(
            task_id="t1", record_id="r2", source_type="icloud", source_display_name="deleted.txt",
            source_size=10, resource_kind="file", status=MigrationStatus.VERIFIED_MATCH, record_hash="",
            target_drive_file_id="fid_2", target_size=10, target_sha256="hash2"
        ),
        # Target size changed
        ManifestRecord(
            task_id="t1", record_id="r3", source_type="icloud", source_display_name="changed_size.txt",
            source_size=10, resource_kind="file", status=MigrationStatus.VERIFIED_MATCH, record_hash="",
            target_drive_file_id="fid_3", target_size=10, target_sha256="hash3"
        ),
        # Status not match (should be ignored entirely)
        ManifestRecord(
            task_id="t1", record_id="r4", source_type="icloud", source_display_name="failed.txt",
            source_size=10, resource_kind="file", status=MigrationStatus.FAILED_UPLOAD, record_hash="",
            target_drive_file_id=None, target_size=0, target_sha256=None
        )
    ]

    mock_drive_state = {
        "fid_1": DriveFileMetadata(size=10, sha256Checksum="hash1"),
        "fid_3": DriveFileMetadata(size=11, sha256Checksum="hash3_new"), # size changed
    }

    def mock_target_checker(file_id: str) -> DriveFileMetadata | None:
        return mock_drive_state.get(file_id)

    advisor = CleanupAdvisor(mock_target_checker)
    candidates, warnings = advisor.list_verified_items(records)

    assert len(candidates) == 1
    assert len(warnings) == 2

    r1_cand = next(c for c in candidates if c.record_id == "r1")
    assert r1_cand.is_verified_still_exists is True

    r2_cand = next(c for c in warnings if c.record_id == "r2")
    assert r2_cand.is_verified_still_exists is False
    assert "no longer exists" in r2_cand.message

    r3_cand = next(c for c in warnings if c.record_id == "r3")
    assert r3_cand.is_verified_still_exists is False
    assert "size changed" in r3_cand.message
