import json
from pathlib import Path
from typing import List

from .utils import get_md5_hash


class Tracker:
    def __init__(self, obj, fields: List[str], output_dir: Path, output_filename: str = 'cache.json'):
        self.obj = obj
        self.fields = fields

        self.output_dir = output_dir
        self.output_filename = output_filename

    def save_changes(self) -> Path:
        tracked_data = self.get_tracking_data()
        tracker_file = self._get_tracker_file()

        with open(tracker_file, 'w') as tracker_fp:
            json.dump(tracked_data, tracker_fp)

        return tracker_file

    def is_changed(self) -> bool:
        tracking_data = self.get_tracking_data()
        tracked_data = self.get_tracked_data()

        return tracked_data != tracking_data

    def get_changes(self) -> dict:
        tracking_data = self.get_tracking_data()
        tracked_data = self.get_tracked_data()

        changes = {}

        for field, current in tracking_data.items():
            previous = tracked_data.get(field, {'hash': None, 'content': None})

            if previous['hash'] != current['hash']:
                changes[field] = {
                    'previous': previous['content'],
                    'current': current['content']
                }

        return changes

    def get_tracked_data(self) -> dict:
        if not self.tracked_exists():
            return {}

        try:
            tracker_file = self._get_tracker_file()

            with open(tracker_file, 'r') as tracker_fp:
                return json.load(tracker_fp)
        except json.JSONDecodeError:
            tracker_file.unlink()

            return {}

    def tracked_exists(self) -> bool:
        tracker_file = self._get_tracker_file()

        return tracker_file.exists()

    def get_tracking_data(self) -> dict:
        cache = {}

        for field in self.fields:
            value = getattr(self.obj, field)

            cache[field] = {
                'hash': get_md5_hash(value),
                'content': value
            }

        return cache

    def _get_tracker_file(self) -> Path:
        return Path(self.output_dir, self.output_filename)
