import pytest
from rmd.conflict import ConflictResolver
from rmd.models import MigrationStatus
from rmd.verification import SourceDigest, DriveFileMetadata

def test_conflict_resolver_match():
    # TDD-TEST-013: 目标同名一致跳过
    source = SourceDigest(md5="123", sha256="456", size=10)
    target = DriveFileMetadata(size=10, md5Checksum="123", sha256Checksum="456")

    status = ConflictResolver.check_conflict(source, target)
    assert status == MigrationStatus.SKIPPED_ALREADY_EXISTS

def test_conflict_resolver_conflict():
    # TDD-TEST-014: 目标同名冲突
    source = SourceDigest(md5="123", sha256="456", size=10)
    target = DriveFileMetadata(size=10, md5Checksum="wrong", sha256Checksum="wrong")

    status = ConflictResolver.check_conflict(source, target)
    assert status == MigrationStatus.CONFLICT_TARGET_EXISTS

def test_conflict_resolver_size_mismatch():
    source = SourceDigest(md5="123", sha256="456", size=10)
    target = DriveFileMetadata(size=11, md5Checksum="123", sha256Checksum="456")

    status = ConflictResolver.check_conflict(source, target)
    assert status == MigrationStatus.CONFLICT_TARGET_EXISTS

def test_conflict_resolver_user_choice():
    assert ConflictResolver.resolve(MigrationStatus.CONFLICT_TARGET_EXISTS, "rename") == "rename"
    assert ConflictResolver.resolve(MigrationStatus.CONFLICT_TARGET_EXISTS, "overwrite") == "overwrite"
    assert ConflictResolver.resolve(MigrationStatus.CONFLICT_TARGET_EXISTS, "skip") == "skip"
    assert ConflictResolver.resolve(MigrationStatus.SKIPPED_ALREADY_EXISTS, "overwrite") == "skip" # Safe default if not conflict
