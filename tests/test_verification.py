import io
from rmd.verification import VerificationEngine, SourceDigest, DriveFileMetadata
from rmd.models import MigrationStatus

def test_calculate_digest():
    data = b"Hello, World!"
    stream = io.BytesIO(data)
    digest = VerificationEngine.calculate_digest_from_stream(stream)

    assert digest.size == 13
    assert digest.md5 == "65a8e27d8879283831b664bd8b7f0ad4"
    assert digest.sha256 == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

def test_verify_sha256_priority():
    # TDD-TEST-010: SHA-256 优先校验
    source = SourceDigest(md5="md5_val", sha256="sha256_val", size=100)
    target = DriveFileMetadata(size=100, md5Checksum="wrong_md5", sha256Checksum="sha256_val")
    assert VerificationEngine.verify(source, target) == MigrationStatus.VERIFIED_MATCH

def test_verify_md5_fallback():
    # TDD-TEST-011: MD5 降级校验
    source = SourceDigest(md5="md5_val", sha256="sha256_val", size=100)
    target = DriveFileMetadata(size=100, md5Checksum="md5_val", sha256Checksum=None)
    assert VerificationEngine.verify(source, target) == MigrationStatus.VERIFIED_MATCH

def test_verify_weak():
    # TDD-TEST-012: checksum 不可用弱校验
    source = SourceDigest(md5="md5_val", sha256="sha256_val", size=100)
    target = DriveFileMetadata(size=100, md5Checksum=None, sha256Checksum=None)
    assert VerificationEngine.verify(source, target) == MigrationStatus.VERIFIED_WEAK

def test_verify_size_mismatch():
    source = SourceDigest(md5="md5_val", sha256="sha256_val", size=100)
    target = DriveFileMetadata(size=101, md5Checksum="md5_val", sha256Checksum="sha256_val")
    assert VerificationEngine.verify(source, target) == MigrationStatus.VERIFIED_SIZE_MISMATCH

def test_verify_hash_mismatch():
    source = SourceDigest(md5="md5_val", sha256="sha256_val", size=100)
    target = DriveFileMetadata(size=100, md5Checksum="wrong", sha256Checksum="wrong")
    assert VerificationEngine.verify(source, target) == MigrationStatus.VERIFIED_HASH_MISMATCH
