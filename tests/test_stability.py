"""Regression tests for stability fixes: incomplete refreshes and safe URL checks.

Tests exercise the real controller logic without a display or network connection.
"""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import bang_iptv_v4 as app
from stream_reliability import HealthBook


class FakeResponse:
    def __init__(self, chunks, *, status=200):
        self.chunks = chunks
        self.status_code = status
        self.headers = {"ETag": "a1"}
        self.closed = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")

    def iter_content(self, chunk_size):
        yield from self.chunks

    def close(self):
        self.closed = True


class StabilityTests(unittest.TestCase):
    def test_failed_background_refresh_preserves_every_previous_channel(self):
        controller = app.IPTVPro.__new__(app.IPTVPro)
        controller.loading_gen = 5
        old = [{"name": "Channel A", "url": "https://a.example"}]
        controller.channels = old
        controller.loading_label = MagicMock()
        controller.source_status = MagicMock()
        controller.status = MagicMock()
        controller.finish_load(
            gen=5,
            chans=[{"name": "Channel B", "url": "https://b.example"}],
            silent=True,
            errors=["Network error"],
            name="World",
        )
        self.assertIs(controller.channels, old)
        controller.source_status.config.assert_called_once()
        self.assertIn("existing channel list", controller.status.config.call_args.kwargs["text"])

    def test_remote_playlist_is_read_incrementally_and_response_closed(self):
        response = FakeResponse([b"#EXTM3U\n", b"#EXTINF:-1,Channel\nhttps://example.org/live\n"])
        controller = app.IPTVPro.__new__(app.IPTVPro)
        controller.http_cache = {}
        with patch.object(app, "requests", SimpleNamespace(get=lambda *args, **kwargs: response)):
            text, changed = controller.fetch_text("https://source.example/list.m3u", False)
        self.assertTrue(changed)
        self.assertIn("#EXTM3U", text)
        self.assertTrue(response.closed)
        self.assertEqual(controller.http_cache["https://source.example/list.m3u"]["etag"], "a1")

    def test_oversized_download_is_rejected_and_does_not_corrupt_cache(self):
        response = FakeResponse([b"x" * (8 * 1024 * 1024 + 1)])
        controller = app.IPTVPro.__new__(app.IPTVPro)
        controller.http_cache = {}
        with patch.object(app, "requests", SimpleNamespace(get=lambda *args, **kwargs: response)):
            with self.assertRaisesRegex(ValueError, "8 MB"):
                controller.fetch_text("https://source.example/huge.m3u", False)
        self.assertTrue(response.closed)
        self.assertEqual(controller.http_cache, {})

    def test_manual_recheck_never_calls_temporary_timeout_dead(self):
        controller = app.IPTVPro.__new__(app.IPTVPro)
        target = {"name": "Channel", "url": "https://example.com/stream", "_i": 12, "opts": []}
        controller.selected_channel = lambda: target
        controller.call_ui = lambda callback, result: callback(result)
        controller.health = HealthBook()
        controller.tree = MagicMock()
        controller.tree.exists.return_value = False
        controller.status = MagicMock()
        controller.display_channels = MagicMock()
        probes = iter([False, None])
        class ImmediateThread:
            def __init__(self, *, target, daemon):
                self.target = target
            def start(self):
                self.target()
        with patch.object(app, "check_stream", side_effect=lambda *a: next(probes)):
            with patch.object(app.threading, "Thread", ImmediateThread):
                controller.recheck_selected()
        self.assertIsNone(target["working"])
        self.assertIn("not verified", controller.status.config.call_args.kwargs["text"])


if __name__ == "__main__":
    unittest.main()
