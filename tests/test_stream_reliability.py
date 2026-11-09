import unittest
from stream_reliability import (
    HealthBook, canonical_name, same_channel, ordered_alternatives, confirm_probe,
)


class ReliabilityTests(unittest.TestCase):
    def test_only_identical_channel_ids_or_names_match(self):
        a = {"tvg_id": "News.bd", "name": "News BD (720p)", "url": "https://dead.test"}
        b = {"tvg_id": "news.bd", "name": "News BD (1080p)", "url": "https://cdn.test/hd"}
        c = {"tvg_id": "news.other", "name": "News BD (1080p)", "url": "https://cdn.test/other"}
        d = {"name": "News 24", "url": "https://cdn.test/24"}
        self.assertTrue(same_channel(a, b))
        self.assertFalse(same_channel(a, c))
        self.assertFalse(same_channel(a, d))
        self.assertEqual(canonical_name(" News BD (720p) "), "news bd")

    def test_requires_two_explicit_failures_and_recovers(self):
        h = HealthBook()
        self.assertIsNone(h.record("https://a.test", False, now=100))
        self.assertIs(h.record("https://a.test", False, now=110), False)
        self.assertIsNone(h.record("https://a.test", None, now=111))
        self.assertIs(h.record("https://a.test", True, now=120, playback=True), True)
        self.assertEqual(h.entries["https://a.test"]["played"], 1)

    def test_old_failures_expire_and_missing_is_not_permanent(self):
        h = HealthBook()
        url = "https://a.test"
        h.record(url, False, now=100)
        self.assertIsNone(h.record(url, False, now=8000))
        h.record(url, False, now=8001)
        self.assertIs(h.status(url, now=8200), False)
        self.assertIsNone(h.status(url, now=11000))

    def test_playback_history_outweighs_unverified_resolution(self):
        h = HealthBook()
        known = {"name": "Channel (720p)", "url": "https://known.test/stream", "quality": 720}
        unknown = {"name": "Channel (2160p)", "url": "https://new.test/stream", "quality": 2160}
        for sec in range(10):
            h.record(known["url"], True, playback=True, now=100+sec)
        self.assertGreater(h.score(known, preference="High quality"), h.score(unknown, preference="High quality"))

    def test_ranking_does_not_return_different_broadcaster(self):
        h = HealthBook()
        channel = {"name": "News 8", "url": "https://broken.test"}
        candidates = [
            {"name": "News 9", "url": "https://wrong.test"},
            {"name": "News 8 (1080p)", "url": "https://hd.test", "quality": 1080},
            {"name": "News 8 (720p)", "url": "https://sd.test", "quality": 720},
        ]
        chosen = ordered_alternatives(channel, candidates, h, preference="High quality")
        self.assertEqual([c["url"] for c in chosen], ["https://hd.test", "https://sd.test"])

    def test_tristate_second_probe(self):
        self.assertIsNone(confirm_probe(lambda *_: None, "https://a.test"))
        self.assertIs(confirm_probe(lambda *_: True, "https://a.test"), True)
        result = iter([False, None])
        self.assertIsNone(confirm_probe(lambda *_: next(result), "https://a.test"))
        result = iter([False, False])
        self.assertIs(confirm_probe(lambda *_: next(result), "https://a.test"), False)

    def test_cache_is_bounded(self):
        h = HealthBook()
        for idx in range(40):
            h.record(f"https://a.test/{idx}", True, now=idx)
        self.assertEqual(len(h.snapshot(limit=10)), 10)


if __name__ == "__main__":
    unittest.main()
