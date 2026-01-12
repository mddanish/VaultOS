import unittest
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestImports(unittest.TestCase):
    def test_docker_manager_import(self):
        try:
            from docker_manager import DockerManager
        except ImportError as e:
            self.fail(f"Failed to import DockerManager: {e}")

    def test_ui_modals_import(self):
        try:
            from ui.modals import CreateContainerModal
        except ImportError as e:
            self.fail(f"Failed to import modals: {e}")

    def test_main_import(self):
        try:
            import main
        except ImportError as e:
            self.fail(f"Failed to import main: {e}")

if __name__ == '__main__':
    unittest.main()
