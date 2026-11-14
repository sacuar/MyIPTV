"""Ensure the approved BANG IPTV icon is present and packagable."""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import bang_iptv_v4 as app


class IconTests(unittest.TestCase):
    def test_icon_exists_in_project_and_is_valid_image(self):
        from PIL import Image
        p = app.resource_path("assets/iptv_icon.png")
        self.assertTrue(p.is_file(), p)
        with Image.open(p) as img:
            self.assertEqual(img.format, "PNG")
            self.assertEqual(img.size, (192, 192))

    def test_icon_resource_resolves_after_pyinstaller_unpack(self):
        with TemporaryDirectory() as path:
            with patch.object(sys, "_MEIPASS", path, create=True):
                self.assertEqual(
                    app.resource_path("assets/iptv_icon.png"),
                    Path(path) / "assets" / "iptv_icon.png",
                )

    def test_windows_ico_can_be_generated_with_multiple_sizes(self):
        from PIL import Image
        from scripts.build_iptv_icon import build
        with TemporaryDirectory() as path:
            dest = build(destination=Path(path) / "BANG_IPTV.ico")
            with Image.open(dest) as icon:
                self.assertEqual(icon.format, "ICO")
                self.assertIn((16, 16), icon.ico.sizes())
                self.assertIn((256, 256), icon.ico.sizes())

    def test_window_and_header_icon_configuration_is_present(self):
        source = Path(app.__file__).read_text(encoding="utf-8")
        self.assertIn("root.iconphoto(True, root._bang_icon)", source)
        self.assertIn("self._header_icon = ImageTk.PhotoImage(small_icon)", source)


if __name__ == "__main__":
    unittest.main()
