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

import os
from pathlib import Path

FILE_ATTRIBUTE_OFFLINE = 0x1000
FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000

class RealWindowsICloudAdapter(SourceAdapter):
    def __init__(self, root_dir: str = r"~\iCloudDrive"):
        self.root_dir = Path(os.path.expanduser(root_dir)).resolve()
        self._path_map = {}

    def _is_offline(self, filepath: Path) -> bool:
        if filepath.suffix == '.iCloud':
            return True
        try:
            attrs = os.stat(filepath).st_file_attributes
            if (attrs & FILE_ATTRIBUTE_OFFLINE) or (attrs & FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS):
                return True
        except (AttributeError, OSError):
            pass # AttributeError on non-Windows/old Python; OSError if file inaccessible
        return False

    def list_items(self) -> Iterator[TransferItem | WinFileEvent]:
        if not self.root_dir.exists() or not self.root_dir.is_dir():
            return

        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                filepath = Path(root) / file
                
                record_id = f"win_icloud_{hashlib.sha1(str(filepath).encode('utf-8')).hexdigest()}"
                self._path_map[record_id] = filepath

                if self._is_offline(filepath):
                    yield WinFileEvent(
                        record_id=record_id,
                        status=MigrationStatus.SOURCE_PLACEHOLDER,
                        path=str(filepath),
                        message="File not downloaded. Please keep it on this device via File Explorer."
                    )
                    continue

                try:
                    size = os.path.getsize(filepath)
                except OSError:
                    continue # Skip if inaccessible

                yield TransferItem(
                    task_id="current_task",
                    record_id=record_id,
                    source_type="icloud_drive",
                    source_display_name=filepath.name,
                    resource_kind="file",
                    source_size=size,
                    source_path=str(filepath)
                )

    def open_stream(self, record_id: str) -> Tuple[io.BufferedReader, Dict]:
        filepath = self._path_map.get(record_id)
        if not filepath or not filepath.exists():
            raise FileNotFoundError(f"Record {record_id} not found or no longer exists")
        
        f = open(filepath, "rb")
        return f, {"size": os.path.getsize(filepath)}
