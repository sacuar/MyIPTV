import tempfile
import unittest
from pathlib import Path

from m3u_export import save_m3u, serialize_m3u


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
            {"name": "Directive", "url": "#EXTINF:-1,Fake"},
            {"name": "Valid", "url": "https://example.com/live"},
        ]
        self.assertEqual(
            serialize_m3u(channels),
            "#EXTM3U\n#EXTINF:-1,Valid\nhttps://example.com/live\n",
        )

    def test_metadata_preserved_and_sanitized(self):
        content = serialize_m3u([{
            "name": "BBC\nNews", "url": "https://example.com/live",
            "tvg": {"id": "bbc.news", "name": 'BBC "One"'},
            "logo": "https://example.com/logo.png", "category": "UK\nNews",
            "language": {"name": "English"},
        }])
        self.assertIn('tvg-id="bbc.news"', content)
        self.assertIn('tvg-name="BBC &quot;One&quot;"', content)
        self.assertIn('group-title="UK News"', content)
        self.assertIn('tvg-logo="https://example.com/logo.png"', content)
        self.assertIn('tvg-language="English"', content)
        self.assertIn(',BBC News\nhttps://example.com/live\n', content)

    def test_empty_playlist_still_has_header(self):
        self.assertEqual(serialize_m3u([]), "#EXTM3U\n")

    def test_save_utf8_and_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "channels.m3u"
            target.write_text("old", encoding="utf-8")
            save_m3u(target, [{"name": "বাংলা", "url": "https://example.com/a"}])
            self.assertIn("বাংলা", target.read_text(encoding="utf-8"))
            self.assertEqual(list(Path(tmp).iterdir()), [target])


if __name__ == "__main__":
    unittest.main()
