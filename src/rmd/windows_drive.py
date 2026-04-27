import io
import hashlib
from typing import Iterator, Tuple, Dict, List
from dataclasses import dataclass
from .models import TransferItem, MigrationStatus
from .adapters import SourceAdapter

@dataclass
class WinFileEvent:
    record_id: str
    status: MigrationStatus
    path: str
    message: str = ""

class MockWindowsICloudAdapter(SourceAdapter):
    def __init__(self, mock_fs: Dict[str, dict]):
        self.mock_fs = mock_fs

    def list_items(self) -> Iterator[TransferItem | WinFileEvent]:
        for path, meta in self.mock_fs.items():
            record_id = f"win_icloud_{hashlib.sha1(path.encode('utf-8')).hexdigest()}"

            # URD-REQ-010: Only process downloaded files on Windows
            if not meta.get("downloaded", True):
                yield WinFileEvent(
                    record_id=record_id,
                    status=MigrationStatus.SOURCE_PLACEHOLDER,
                    path=path,
                    message="File not downloaded. Please keep it on this device via File Explorer."
                )
                continue

            yield TransferItem(
                task_id="current_task",
                record_id=record_id,
                source_type="icloud_drive",
                source_display_name=path.split('\\')[-1],
                resource_kind="file",
                source_size=meta.get("size", 0),
                source_path=path
            )

    def open_stream(self, record_id: str) -> Tuple[io.BytesIO, Dict]:
        # Mock logic
        return io.BytesIO(b"data"), {"size": 4}
