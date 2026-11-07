import tempfile
import unittest
from pathlib import Path

from playlist_service import (
    channel_status, export_channels, load_playlist, select_channels, validate_source,
)


class FakeParser:
    def __init__(self, timeout):
        self.timeout = timeout

    def parse_m3u(self, source, check_live):
        self.checked = check_live

    def get_list(self):
        return [
            {"name": "বাংলা TV", "category": "News", "url": "https://a.test/live", "status": "GOOD"},
            {"name": "বাংলা TV", "category": "News", "url": "https://a.test/live", "status": "GOOD"},
            {"name": "Music", "category": "Music", "url": "https://b.test/live", "status": "BAD"},
            {"name": "Unknown", "category": "Music", "url": "https://c.test/live"},
            {"name": "Invalid", "url": ""},
        ]


class PlaylistServiceTests(unittest.TestCase):
    def test_http_source_and_local_file(self):
        self.assertEqual(validate_source("https://example.com/a.m3u"), "https://example.com/a.m3u")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "playlist.m3u"
            source.write_text("#EXTM3U", encoding="utf-8")
            self.assertEqual(validate_source(str(source)), str(source))

    def test_invalid_sources(self):
        for source in ("", "ftp://example.com/a.m3u", "https://", "no-such-file.m3u"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                validate_source(source)

    def test_load_and_classification(self):
        result = load_playlist("https://example.com/list.m3u", parser_factory=FakeParser)
        self.assertEqual(len(result.channels), 4)
        self.assertEqual(result.counts["GOOD"], 2)
        self.assertEqual(result.counts["BAD"], 1)
        self.assertEqual(result.counts["UNKNOWN"], 1)
        self.assertEqual(result.duplicates, 1)

    def test_filter_unicode_and_category(self):
        result = load_playlist("https://example.com/list.m3u", parser_factory=FakeParser)
        self.assertEqual(len(select_channels(result, status="GOOD", category="News", query="বাংলা")), 2)
        self.assertEqual(len(select_channels(result, query="missing")), 0)

    def test_working_only_deduplicated(self):
        result = load_playlist("https://example.com/list.m3u", parser_factory=FakeParser)
        chosen = export_channels(result)
        self.assertEqual([ch["url"] for ch in chosen], ["https://a.test/live"])
        self.assertEqual(len(export_channels(result, deduplicate=False)), 2)

    def test_unchecked_must_not_be_called_bad(self):
        result = load_playlist("https://example.com/list.m3u", check_live=False, parser_factory=FakeParser)
        self.assertEqual(channel_status(result.channels[0], result.checked), "UNCHECKED")
        with self.assertRaises(ValueError):
            export_channels(result)
        self.assertEqual(len(export_channels(result, only_working=False)), 3)


if __name__ == "__main__":
    unittest.main()
