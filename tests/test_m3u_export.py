import unittest

from m3u_export import serialize_m3u


class M3uExportTests(unittest.TestCase):
    def test_writes_standard_header_and_channel_entries(self):
        channels = [
            {"name": "Channel One", "url": "https://example.com/one.m3u8"},
            {"name": "বাংলা টিভি", "url": "https://example.com/two.m3u8"},
        ]
        self.assertEqual(
            serialize_m3u(channels),
            "#EXTM3U\n"
            "#EXTINF:-1,Channel One\nhttps://example.com/one.m3u8\n"
            "#EXTINF:-1,বাংলা টিভি\nhttps://example.com/two.m3u8\n",
        )

    def test_ignores_missing_or_multiline_urls(self):
        channels = [
            {"name": "Missing"},
            {"name": "Multiline", "url": "https://a.example\n#EXTINF:-1,Injected"},
            {"name": "Valid", "url": "https://example.com/live"},
        ]
        self.assertEqual(
            serialize_m3u(channels),
            "#EXTM3U\n#EXTINF:-1,Valid\nhttps://example.com/live\n",
        )

    def test_normalizes_multiline_names(self):
        self.assertEqual(
            serialize_m3u([{"name": "BBC\nNews", "url": "rtsp://example.com/live"}]),
            "#EXTM3U\n#EXTINF:-1,BBC News\nrtsp://example.com/live\n",
        )

    def test_empty_playlist_still_has_header(self):
        self.assertEqual(serialize_m3u([]), "#EXTM3U\n")


if __name__ == "__main__":
    unittest.main()
