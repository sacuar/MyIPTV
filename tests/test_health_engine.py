import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from health_engine import (
    CheckResult, HealthMonitor, check_stream, hidden_status,
)
from player_core import Channel


class Response:
    status = 200

    def __init__(self, data, content_type="application/vnd.apple.mpegurl"):
        self.data = data
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, count):
        return self.data[:count]


class HealthEngineTests(unittest.TestCase):
    def test_hls_manifest_good(self):
        with patch("health_engine.urlopen", return_value=Response(
            b"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1000\nstream.m3u8\n"
        )):
            self.assertEqual(check_stream("https://example.com/live.m3u8").status, "online")

    def test_fake_html_is_not_good(self):
        with patch("health_engine.urlopen", return_value=Response(
            b"<html>Forbidden</html>", "text/html"
        )):
            self.assertEqual(check_stream("https://example.com/live.m3u8").status, "unknown")

    def test_http_missing(self):
        with patch("health_engine.urlopen", side_effect=HTTPError(
            "https://example.com/no.m3u8", 404, "Not Found", {}, None
        )):
            self.assertEqual(check_stream("https://example.com/no.m3u8").status, "missing")

    def test_http_403_is_blocked_not_missing(self):
        with patch("health_engine.urlopen", side_effect=HTTPError(
            "https://example.com/private.m3u8", 403, "Forbidden", {}, None
        )):
            self.assertEqual(check_stream("https://example.com/private.m3u8").status, "blocked")

    def test_timeout_is_unknown(self):
        with patch("health_engine.urlopen", side_effect=URLError("timeout")):
            self.assertEqual(check_stream("https://example.com/live.m3u8").status, "unknown")

    def test_non_http_unsupported(self):
        self.assertEqual(check_stream("rtsp://example.com/live").status, "unsupported")

    def test_missing_requires_two_checks(self):
        m = HealthMonitor()
        url = "https://example.com/dead"
        self.assertEqual(m.record(url, "missing", now=10), "suspect")
        self.assertFalse(hidden_status(m.status(url)))
        self.assertEqual(m.record(url, "missing", now=30), "offline")
        self.assertTrue(hidden_status(m.status(url)))
        self.assertEqual(m.record(url, "online", now=50), "online")
        self.assertFalse(hidden_status(m.status(url)))

    def test_intermittent_failures_do_not_hide(self):
        m = HealthMonitor()
        u = "https://example.com/possibly-live"
        m.record(u, "missing", now=1)
        m.record(u, "unknown", now=2)
        self.assertEqual(m.record(u, "missing", now=3), "suspect")
        self.assertFalse(hidden_status(m.status(u)))

    def test_playback_failed_then_recovered(self):
        m = HealthMonitor()
        u = "https://example.com/failing"
        self.assertEqual(m.record(u, "playback_failed", now=20), "failed")
        self.assertTrue(hidden_status(m.status(u)))
        self.assertEqual(m.record(u, "online", now=21), "online")

    def test_choose_prefers_visible_and_respects_cooldown(self):
        m = HealthMonitor()
        channels = [
            Channel("first", "https://example.com/1"),
            Channel("second", "https://example.com/2"),
            Channel("third", "https://example.com/3"),
        ]
        m.record(channels[1].url, "online", now=100)
        urls = m.choose(channels, now=101, preferred=[channels[2].url], limit=2)
        self.assertEqual(urls, [channels[2].url, channels[0].url])
        self.assertEqual(
            m.choose(channels, now=401, preferred=[channels[1].url], limit=1),
            [channels[1].url],
        )

    def test_suspect_retry_and_force(self):
        m = HealthMonitor()
        c = Channel("one", "https://example.com/1")
        m.record(c.url, "missing", now=10)
        self.assertEqual(m.choose([c], now=12), [])
        self.assertEqual(m.choose([c], now=26), [c.url])
        self.assertEqual(m.choose([c], now=12, force=True), [c.url])

    def test_counts(self):
        m = HealthMonitor()
        channels = [Channel("One", "https://example.com/a"),
                    Channel("Two", "https://example.com/b")]
        m.record(channels[0].url, CheckResult("online", "Ok"), now=2)
        self.assertEqual(m.counts(channels)["online"], 1)
        self.assertEqual(m.counts(channels)["unchecked"], 1)


if __name__ == "__main__":
    unittest.main()
