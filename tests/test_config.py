import unittest
from config import get_desktop_label, OS_DESKTOP_MAP

class TestConfig(unittest.TestCase):
    def test_get_desktop_label(self):
        self.assertEqual(get_desktop_label("xfce"), "XFCE")
        self.assertEqual(get_desktop_label("kde"), "KDE Plasma")
        self.assertEqual(get_desktop_label("unknown"), "Unknown")
        self.assertEqual(get_desktop_label(""), "Unknown")

    def test_os_options_structure(self):
        # Verify OS options are list of tuples
        from config import OS_OPTIONS
        self.assertTrue(isinstance(OS_OPTIONS, list))
        for item in OS_OPTIONS:
            self.assertTrue(isinstance(item, tuple))
            self.assertEqual(len(item), 2)

    def test_desktop_map_validity(self):
        # Ensure all mapped desktops have labels
        for os_key, desktops in OS_DESKTOP_MAP.items():
            for desktop in desktops:
                label = get_desktop_label(desktop)
                self.assertNotEqual(label, "Unknown", f"Desktop '{desktop}' in {os_key} has no label")

if __name__ == '__main__':
    unittest.main()
