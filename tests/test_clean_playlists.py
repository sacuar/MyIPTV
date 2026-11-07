import tempfile
import unittest
from pathlib import Path

from scripts.clean_playlists import clean_sources, deduplicate, parse_entries


class CleanerTests(unittest.TestCase):
    def test_bom_metadata_and_deduplication(self):
        text = (
            '\ufeff#EXTM3U\n'
            '#EXTINF:-1 tvg-id="bd1" group-title="Bangladesh",বাংলা TV\n'
            'https://example.com/bangla.m3u8\n'
            '#EXTINF:-1,Repeated\nhttps://example.com/bangla.m3u8\n'
            '#EXTINF:-1,Other\nhttps://example.com/other.m3u8\n'
        )
        parsed = parse_entries(text)
        self.assertEqual(parsed[0]["name"], "বাংলা TV")
        self.assertEqual(parsed[0]["tvg"]["id"], "bd1")
        self.assertEqual(len(deduplicate(parsed)), 2)

    def test_ignores_malformed_entries(self):
        text = (
            "#EXTM3U\n#EXTINF:-1,Bad\n#NOT-A-LINK\n"
            "#EXTINF:-1,Good\nhttps://example.com/ok\n"
            "#EXTINF:-1,Bad Other\nfile:///suspicious\n"
        )
        parsed = parse_entries(text)
        self.assertEqual([x["name"] for x in parsed], ["Good"])

    def test_clean_sources_reports_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "old.m3u"
            p.write_text(
                "#EXTM3U\n#EXTINF:-1,A\nhttps://example.com/a\n"
                "#EXTINF:-1,A duplicate\nhttps://example.com/a\n",
                encoding="utf-8",
            )
            output, report = clean_sources([p])
            self.assertEqual(len(output), 1)
            self.assertEqual(report["duplicates"], 1)
            self.assertEqual(report["unchecked"], 1)


if __name__ == "__main__":
    unittest.main()
