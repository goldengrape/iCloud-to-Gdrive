import hashlib
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from .models import MigrationStatus

@dataclass
class SourceDigest:
    md5: str
    sha256: str
    size: int

@dataclass
class DriveFileMetadata:
    size: int
    md5Checksum: Optional[str] = None
    sha1Checksum: Optional[str] = None
    sha256Checksum: Optional[str] = None
    headRevisionId: Optional[str] = None

class VerificationEngine:
    @staticmethod
    def calculate_digest_from_stream(stream, chunk_size: int = 8192) -> SourceDigest:
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        size = 0

        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
            size += len(chunk)

        return SourceDigest(
            md5=md5_hash.hexdigest(),
            sha256=sha256_hash.hexdigest(),
            size=size
        )

    @staticmethod
    def verify(source: SourceDigest, target: DriveFileMetadata) -> MigrationStatus:
        if source.size != target.size:
            return MigrationStatus.VERIFIED_SIZE_MISMATCH

        if target.sha256Checksum:
            if source.sha256.lower() == target.sha256Checksum.lower():
                return MigrationStatus.VERIFIED_MATCH
            return MigrationStatus.VERIFIED_HASH_MISMATCH

        if target.md5Checksum:
            if source.md5.lower() == target.md5Checksum.lower():
                return MigrationStatus.VERIFIED_MATCH
            return MigrationStatus.VERIFIED_HASH_MISMATCH

        # If neither hash is available, it's a weak verification (just size match)
        return MigrationStatus.VERIFIED_WEAK
