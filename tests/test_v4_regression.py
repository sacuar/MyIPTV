"""Focused offline regression tests for the richer BANG IPTV v4 application."""
import hashlib
import unittest
from unittest.mock import patch

import bang_iptv_v4 as app


class FakeResponse:
    def __init__(self, status_code, payload=b"", content_type="application/vnd.apple.mpegurl"):
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}
        self.payload = payload

    def iter_content(self, chunk_size):
        yield self.payload

    def close(self):
        pass


class V4RegressionTests(unittest.TestCase):
    def test_parse_merge_deduplicate_and_natural_sort(self):
        text = (
            '#EXTM3U\n'
            '#EXTINF:-1 tvg-id="News.bd" group-title="News",News 10\nhttps://a.test/10.m3u8\n'
            '#EXTINF:-1 group-title="News",News 2\nhttps://a.test/2.m3u8\n'
        )
        rows = app.merge_playlists([app.parse_m3u(text), app.parse_m3u(text)])
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            [row["name"] for row in app.sort_channels(rows, "Name (A→Z)")],
            ["News 2", "News 10"],
        )
        rows[0]["working"] = False
        self.assertEqual(len(app.filter_channels(rows, status="Hide dead")), 1)

    def test_network_timeout_and_access_denied_are_inconclusive(self):
        if app.requests is None:
            self.skipTest("requests not available")
        with patch.object(app.requests, "get", side_effect=TimeoutError("timeout")):
            self.assertIsNone(app.check_stream("https://example.org/live"))
        with patch.object(app.requests, "get", return_value=FakeResponse(403)):
            self.assertIsNone(app.check_stream("https://example.org/live"))
        with patch.object(app.requests, "get", return_value=FakeResponse(404)):
            self.assertIs(app.check_stream("https://example.org/live"), False)

    def test_valid_hls_is_detected(self):
        if app.requests is None:
            self.skipTest("requests not available")
        response = FakeResponse(200, b"#EXTM3U\n#EXT-X-TARGETDURATION:6\n")
        with patch.object(app.requests, "get", return_value=response):
            self.assertIs(app.check_stream("https://example.org/live.m3u8"), True)

    def test_missing_requests_does_not_claim_stream_is_working(self):
        with patch.object(app, "requests", None):
            self.assertIsNone(app.check_stream("https://example.org/live"))

    def test_settings_and_link_privacy_defaults(self):
        self.assertEqual(app.DEFAULT_SETTINGS["status_filter"], "Hide dead")
        self.assertIn(app.DEFAULT_SETTINGS["last_source"], app.IPTV_SOURCES)
        self.assertEqual(
            app.PASSWORD_HASH,
            hashlib.sha256("".join(chr(v) for v in (51, 50, 49)).encode()).hexdigest(),
        )
        self.assertNotIn("bang_iptv_data", str(app.APP_DIR))

    def test_source_contains_scrollbar_and_startup_autoload(self):
        from pathlib import Path
        source = Path(app.__file__).read_text(encoding="utf-8")
        self.assertIn('self.channel_scrollbar = sb', source)
        self.assertIn('self.load_source(self.settings.get("last_source")', source)
        self.assertIn("self.root.after(5 * 60000, self.recheck_loop)", source)


if __name__ == "__main__":
    unittest.main()
