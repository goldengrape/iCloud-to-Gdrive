from typing import Optional, Tuple
from dataclasses import dataclass
from .models import MigrationStatus
from .verification import SourceDigest, DriveFileMetadata, VerificationEngine

class ConflictResolver:
    @staticmethod
    def check_conflict(source: SourceDigest, target: DriveFileMetadata) -> MigrationStatus:
        # TDD-TEST-013: 目标同名一致跳过, TDD-TEST-014: 目标同名冲突
        verification_result = VerificationEngine.verify(source, target)

        if verification_result == MigrationStatus.VERIFIED_MATCH:
            return MigrationStatus.SKIPPED_ALREADY_EXISTS

        return MigrationStatus.CONFLICT_TARGET_EXISTS

    @staticmethod
    def resolve(conflict_status: MigrationStatus, user_choice: str) -> str:
        """
        user_choice: 'skip', 'rename', 'overwrite'
        Returns action to take: 'skip', 'rename', 'overwrite'
        """
        if conflict_status != MigrationStatus.CONFLICT_TARGET_EXISTS:
            return "skip"

        if user_choice in ['skip', 'rename', 'overwrite']:
            return user_choice

        return "skip" # Default safe action
