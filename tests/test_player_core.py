import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from player_core import Channel, filtered_channels, load_channels, parse_m3u, read_playlist


SAMPLE = '''\ufeff#EXTM3U
#EXTINF:-1 tvg-id="bd.1" group-title="News, Bangladesh" tvg-logo="https://example.com/img.png",বাংলা News
https://example.com/one.m3u8
#EXTINF:-1 group-title="Sports",Sports HD
https://example.com/two.m3u8
#EXTINF:-1,Duplicate
https://example.com/one.m3u8
#EXTINF:-1,Not a stream
file:///private/file.m3u8
#EXTINF:-1,Still valid
rtsp://example.com/live
'''


class PlayerCoreTests(unittest.TestCase):
    def test_real_world_m3u_parsing_and_metadata(self):
        rows = parse_m3u(SAMPLE)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0].name, "বাংলা News")
        self.assertEqual(rows[0].group, "News, Bangladesh")
        self.assertEqual(rows[0].tvg_id, "bd.1")
        self.assertEqual(rows[0].logo, "https://example.com/img.png")

    def test_duplicate_urls_keeps_first_metadata(self):
        rows = parse_m3u(SAMPLE)
        self.assertEqual([r.name for r in rows], ["বাংলা News", "Sports HD", "Still valid"])
        self.assertEqual(len(parse_m3u(SAMPLE, deduplicate=False)), 4)

    def test_malformed_urls_ignored_without_crash(self):
        data = (
            "#EXTM3U\n#EXTINF:-1,Bad\nhttp://[oops\n"
            "#EXTINF:-1,Header injection\nhttps://example.com/a b\n"
            "#EXTINF:-1,Valid\nhttps://example.com/yes\n"
        )
        rows = parse_m3u(data)
        self.assertEqual([r.name for r in rows], ["Valid"])

    def test_search_filter_and_favorites(self):
        rows = parse_m3u(SAMPLE)
        self.assertEqual(len(filtered_channels(rows, query="বাংলা")), 1)
        self.assertEqual(len(filtered_channels(rows, group="Sports")), 1)
        self.assertEqual(len(filtered_channels(rows, favorites={"https://example.com/one.m3u8"})), 1)
        self.assertEqual(len(filtered_channels(rows, query="does not exist")), 0)

    def test_local_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "list.m3u"
            file.write_text(SAMPLE, encoding="utf-8")
            rows = load_channels(file)
            self.assertEqual(len(rows), 3)

    def test_empty_playlist_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "list.m3u"
            file.write_text("#EXTM3U\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No valid channels"):
                load_channels(file)

    def test_invalid_source_rejected(self):
        with self.assertRaises(ValueError):
            read_playlist("")
        with self.assertRaises(ValueError):
            read_playlist("ftp://example.com/list.m3u")

    def test_file_too_large_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "big.m3u"
            with patch("player_core.MAX_PLAYLIST_BYTES", 12):
                file.write_text("#EXTM3U\n#EXTINF:-1,x", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "too large"):
                    read_playlist(file)

    def test_url_read_with_bounded_request(self):
        class DummyResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, limit):
                self.limit = limit
                return b'#EXTM3U\n#EXTINF:-1,One\nhttps://example.com/1\n'

        with patch("player_core.urlopen", return_value=DummyResponse()):
            rows = load_channels("https://example.com/list.m3u")
            self.assertEqual(rows[0].name, "One")


if __name__ == "__main__":
    unittest.main()
