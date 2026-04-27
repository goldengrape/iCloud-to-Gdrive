import io
import hashlib
from typing import Iterator, Tuple, Dict
from dataclasses import dataclass
from .models import TransferItem, MigrationStatus
from .adapters import SourceAdapter

@dataclass
class ICloudFileEvent:
    record_id: str
    status: MigrationStatus
    path: str

class MockMacICloudDriveAdapter(SourceAdapter):
    def __init__(self, mock_fs: Dict[str, dict]):
        self.mock_fs = mock_fs

    def list_items(self) -> Iterator[TransferItem | ICloudFileEvent]:
        for path, meta in self.mock_fs.items():
            record_id = f"mac_icloud_{hashlib.sha1(path.encode('utf-8')).hexdigest()}"

            if path.endswith(".iCloud"):
                # URD-REQ-010: Placeholder files
                yield ICloudFileEvent(
                    record_id=record_id,
                    status=MigrationStatus.SOURCE_PLACEHOLDER,
                    path=path
                )
                continue

            # URD-REQ-010: Permissions/Unreadable
            if meta.get("unreadable"):
                yield ICloudFileEvent(
                    record_id=record_id,
                    status=MigrationStatus.FAILED_SOURCE_READ,
                    path=path
                )
                continue

            yield TransferItem(
                task_id="current_task",
                record_id=record_id,
                source_type="icloud_drive",
                source_display_name=path.split('/')[-1],
                resource_kind=meta.get("kind", "file"),
                source_size=meta.get("size", 0),
                source_path=path
            )

    def open_stream(self, record_id: str) -> Tuple[io.BytesIO, Dict]:
        for path, meta in self.mock_fs.items():
            if f"mac_icloud_{hashlib.sha1(path.encode('utf-8')).hexdigest()}" == record_id:
                if meta.get("data"):
                    return io.BytesIO(meta["data"]), {"size": len(meta["data"])}
                return io.BytesIO(b""), {"size": 0}
        raise FileNotFoundError(f"Record {record_id} not found")
