import unittest
from dataclasses import dataclass

from channel_recovery import (
    normalized_name, matching_alternatives, first_reachable_replacement,
    apply_replacements,
)
from link_access import verify_link_pin
from player_core import Channel


@dataclass
class Result:
    status: str


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.original = Channel(
            "Bangla News (720p)", "https://old.example/live.m3u8",
            group="News", tvg_id="BanglaNews.bd",
        )
        self.alternatives = [
            Channel("Unrelated Channel", "https://free.example/wrong",
                    tvg_id="SomeOther.id"),
            Channel("Bangla News (1080p)", "https://free.example/replacement.m3u8",
                    tvg_id="BanglaNews.bd"),
            Channel("Bangla News", "http://free.example/fallback",
                    tvg_id=""),
            Channel("Bangla News", "https://old.example/live.m3u8",
                    tvg_id="BanglaNews.bd"),
        ]

    def test_quality_suffix_ignored_but_identity_preserved(self):
        self.assertEqual(normalized_name("  বাংলা TV (720p) "), "বাংলা tv")
        self.assertNotEqual(normalized_name("News 18"), normalized_name("News 24"))

    def test_prefers_tvg_id_and_avoids_dead_url(self):
        matches = matching_alternatives(self.original, self.alternatives)
        self.assertEqual(matches[0].url, "https://free.example/replacement.m3u8")
        self.assertTrue(all(item.url != self.original.url for item in matches))
        self.assertNotIn(self.alternatives[0], matches)

    def test_can_find_name_when_tvg_id_missing(self):
        source = Channel("Bangla News (720p)", "https://old.example/live.m3u8")
        self.assertEqual(
            matching_alternatives(source, self.alternatives)[0].url,
            "https://free.example/replacement.m3u8"
        )

    def test_only_verified_alternative_is_used(self):
        def probe(url):
            return Result("online" if url.endswith("fallback") else "unknown")
        found = first_reachable_replacement(self.original, self.alternatives, probe)
        self.assertEqual(found.url, "http://free.example/fallback")
        self.assertIsNone(first_reachable_replacement(
            self.original, self.alternatives, lambda url: Result("missing")))

    def test_refresh_keeps_repaired_url(self):
        output = apply_replacements(
            [self.original, Channel("Duplicate", "https://old.example/live.m3u8")],
            {"https://old.example/live.m3u8": "https://free.example/fixed.m3u8"}
        )
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0].url, "https://free.example/fixed.m3u8")
        self.assertEqual(output[0].name, self.original.name)

    def test_replacement_cycle_does_not_loop_forever(self):
        a, b = "https://a.example", "https://b.example"
        output = apply_replacements([Channel("A", a)], {a: b, b: a})
        self.assertEqual(output[0].url, b)

    def test_link_pin_is_not_advertised_by_validation(self):
        self.assertTrue(verify_link_pin("".join(map(chr, (51, 50, 49)))))
        self.assertFalse(verify_link_pin("123"))
        self.assertFalse(verify_link_pin(""))
        self.assertFalse(verify_link_pin(None))


if __name__ == "__main__":
    unittest.main()
