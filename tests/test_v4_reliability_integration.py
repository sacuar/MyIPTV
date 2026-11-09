"""Offline integration tests for v4 stream replacement and UI preservation."""
import unittest

import bang_iptv_v4 as app
from stream_reliability import HealthBook


def channel(name, url, tvg_id="news.bd", quality=0):
    return {
        "name": name, "url": url, "tvg_id": tvg_id,
        "norm": app.norm_name(name), "quality": quality,
        "opts": [], "alts": [], "category": "News",
    }


class V4ReliabilityIntegrationTests(unittest.TestCase):
    def test_repair_prefers_known_reliable_playback_over_advertised_4k(self):
        history = HealthBook()
        original = channel("News (720p)", "https://dead.example/live")
        reliable = channel("News (720p)", "https://good.example/live", quality=720)
        untested = channel("News (2160p)", "https://unknown.example/live", quality=2160)
        history.record(reliable["url"], True, playback=True, now=100)
        history.record(reliable["url"], True, playback=True, now=101)
        finder = app.Repairer(history)
        finder.add([original, reliable, untested])
        result = finder.find_working(
            original, checker=lambda _url, _opts: True,
            preference="High quality",
        )
        self.assertEqual(result["url"], reliable["url"])

    def test_repair_does_not_use_unrelated_channel(self):
        original = channel("News 24", "https://dead.example/live", tvg_id="news24")
        unrelated = channel("News 25", "https://other.example/live", tvg_id="news25")
        finder = app.Repairer()
        finder.add([original, unrelated])
        self.assertIsNone(finder.find_working(
            original, checker=lambda _url, _opts: True))

    def test_only_conclusive_missing_replies_mark_offline(self):
        finder = app.Repairer()
        target = channel("News", "https://dead.example/live")
        candidate = channel("News (HD)", "https://candidate.example/live")
        finder.add([target, candidate])
        self.assertIsNone(finder.find_working(
            target, checker=lambda _url, _opts: None))
        self.assertIsNone(finder.find_working(
            target, checker=lambda _url, _opts: False))

    def test_v4_ui_and_background_safety_hooks_remain_present(self):
        from pathlib import Path
        source = Path(app.__file__).read_text(encoding="utf-8")
        for hook in (
            "self.channel_scrollbar = sb",
            "self.load_source(self.settings.get(\"last_source\")",
            "self.val_queue = deque(",
            "max_workers=8, thread_name_prefix",
            "self.root.after(350, self.flush_validation, gen)",
            "self.root.after(5 * 60000, self.recheck_loop)",
            "self._queue_auto_repair(ch)",
            "self.connection_retry_remaining -= 1",
            "self.quality_var = tk.StringVar",
        ):
            with self.subTest(hook=hook):
                self.assertIn(hook, source)

    def test_local_m3u_can_be_saved_and_loaded_on_next_launch(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as folder:
            playlist = Path(folder) / "all.m3u8"
            playlist.write_text(
                "#EXTM3U\n#EXTINF:-1,Bangla TV\nhttps://example.com/stream.m3u8\n",
                encoding="utf-8",
            )
            player = app.IPTVPro.__new__(app.IPTVPro)
            player.settings = {"last_local_file": str(playlist), "custom_sources": []}
            sources = player.all_sources()
            self.assertIn("📂 Local M3U file", sources)
            self.assertEqual(sources["📂 Local M3U file"]["urls"], [str(playlist)])
            with patch.object(app, "requests", None):
                result, changed = player.fetch_text(str(playlist), False)
            self.assertTrue(changed)
            self.assertIn("Bangla TV", result)
            self.assertIn("#EXTM3U", result)

    def test_persisted_quality_preference_default(self):
        self.assertEqual(app.DEFAULT_SETTINGS["quality_preference"], "Balanced")
        self.assertEqual(app.DEFAULT_SETTINGS["status_filter"], "Hide dead")


if __name__ == "__main__":
    unittest.main()
