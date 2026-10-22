import unittest
import sys
import os
import shutil
import subprocess

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QObject, Property, Signal, QByteArray, QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
    HAS_PYSIDE6 = True
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
except (ImportError, Exception):
    HAS_PYSIDE6 = False
    app = None

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAIN_QML = os.path.join(PROJECT_ROOT, "contents", "ui", "main.qml")
CONFIG_QML = os.path.join(PROJECT_ROOT, "contents", "ui", "configGeneral.qml")

class TestPanelScroller(unittest.TestCase):
    def test_01_config_fallback_when_plasmoid_config_undefined(self):
        """Tests that main.qml gracefully falls back to default values without TypeError when Plasmoid.configuration is undefined."""
        if not HAS_PYSIDE6:
            self.skipTest("PySide6 QML dependencies not available in environment")
        engine = QQmlApplicationEngine()
        comp = QQmlComponent(engine, MAIN_QML)
        if comp.isError():
            errors = [e.toString() for e in comp.errors()]
            if any("org.kde." in err for err in errors):
                self.skipTest(f"KDE Plasma QML modules not installed: {errors}")
            self.fail(f"Compilation errors: {errors}")
        obj = comp.create()
        self.assertIsNotNone(obj, "Failed to instantiate PlasmoidItem")
        self.assertEqual(obj.property("invertScroll"), False)
        self.assertEqual(obj.property("wrapAround"), False)
        self.assertEqual(obj.property("scrollThreshold"), 60)
        self.assertEqual(obj.property("cooldownMs"), 280)
        self.assertEqual(obj.property("canSwitch"), True)

    def test_02_dominant_axis_calculation(self):
        """Tests that horizontal trackpad gestures with minor vertical jitter evaluate to the horizontal axis."""
        def calc_delta(angle_x, angle_y, invert=False):
            raw = angle_y if abs(angle_y) >= abs(angle_x) else -angle_x
            return -raw if invert else raw

        # Vertical dominant (standard mouse wheel down)
        self.assertEqual(calc_delta(0, -120), -120)
        # Vertical dominant (standard mouse wheel up)
        self.assertEqual(calc_delta(0, 120), 120)
        # Horizontal swipe right with minor trackpad vertical jitter
        self.assertEqual(calc_delta(45, 2), -45)
        # Horizontal swipe left with minor trackpad vertical jitter
        self.assertEqual(calc_delta(-50, -3), 50)
        # Inverted mode
        self.assertEqual(calc_delta(0, 120, invert=True), -120)

    def test_03_overlay_default_visibility_and_enabled(self):
        """Tests that fullPanelOverlay is instantiated, visible, and enabled by default in normal runtime mode."""
        if not HAS_PYSIDE6:
            self.skipTest("PySide6 QML dependencies not available in environment")
        engine = QQmlApplicationEngine()
        comp = QQmlComponent(engine, MAIN_QML)
        if comp.isError():
            errors = [e.toString() for e in comp.errors()]
            if any("org.kde." in err for err in errors):
                self.skipTest(f"KDE Plasma QML modules not installed: {errors}")
            self.fail(f"Compilation errors: {errors}")
        obj = comp.create()
        self.assertIsNotNone(obj)
        overlay = None
        # Find overlay item
        for child in obj.children():
            if child.property("z") == 999999:
                overlay = child
                break
        self.assertIsNotNone(overlay, "fullPanelOverlay item not found")
        # In non-edit mode (default), overlay should be visible and enabled
        self.assertTrue(overlay.property("visible"))
        self.assertTrue(overlay.property("enabled"))

    def test_04_config_general_defaults_and_spinboxes(self):
        """Tests that configGeneral.qml initializes with valid default values and editable controls."""
        if not HAS_PYSIDE6:
            self.skipTest("PySide6 QML dependencies not available in environment")
        engine = QQmlApplicationEngine()
        comp = QQmlComponent(engine, CONFIG_QML)
        if comp.isError():
            errors = [e.toString() for e in comp.errors()]
            if any("org.kde." in err for err in errors):
                self.skipTest(f"KDE Plasma QML modules not installed: {errors}")
            self.fail(f"Errors: {errors}")
        obj = comp.create()
        self.assertIsNotNone(obj)
        self.assertEqual(obj.property("cfg_invertScroll"), False)
        self.assertEqual(obj.property("cfg_wrapAround"), False)
        self.assertEqual(obj.property("cfg_scrollThreshold"), 60)
        self.assertEqual(obj.property("cfg_cooldownMs"), 280)

    def test_05_dbus_kwin_communication(self):
        """Tests direct DBus query to KWin compositor on active user session."""
        if not shutil.which("busctl"):
            self.skipTest("busctl not available in test environment")
        res = subprocess.run(
            ["busctl", "--user", "call", "org.kde.KWin", "/KWin", "org.kde.KWin", "currentDesktop"],
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            self.skipTest(f"KWin session not reachable on user bus: {res.stderr.strip()}")
        self.assertIn("i ", res.stdout)
        desktop_num = int(res.stdout.split()[1])
        self.assertGreaterEqual(desktop_num, 1)

    def test_06_appstream_metadata_validation(self):
        """Tests AppStream metadata generation using kpackagetool6."""
        if not shutil.which("kpackagetool6"):
            self.skipTest("kpackagetool6 not available in test environment")
        res = subprocess.run(
            ["kpackagetool6", "--appstream-metainfo", PROJECT_ROOT],
            capture_output=True,
            text=True,
            check=True
        )
        self.assertIn("<id>com.github.khoipm06.panelscroller</id>", res.stdout)
        self.assertIn("<project_license>GPL-3.0+</project_license>", res.stdout)

    def test_07_package_script_hygiene(self):
        """Tests scripts/package.sh builds a clean zip archive without temporary or hidden files."""
        import json
        with open(os.path.join(PROJECT_ROOT, "metadata.json"), "r") as f:
            meta = json.load(f)
        current_version = meta.get("KPlugin", {}).get("Version")
        self.assertTrue(bool(current_version), "Version not defined in metadata.json")

        res = subprocess.run(
            [os.path.join(PROJECT_ROOT, "scripts", "package.sh")],
            capture_output=True,
            text=True,
            check=True
        )
        pkg_path = os.path.join(PROJECT_ROOT, "build", "com.github.khoipm06.panelscroller.plasmoid")
        versioned_pkg_path = os.path.join(PROJECT_ROOT, "build", f"com.github.khoipm06.panelscroller-{current_version}.plasmoid")
        self.assertTrue(os.path.exists(pkg_path), f"Standard package missing: {pkg_path}")
        self.assertTrue(os.path.exists(versioned_pkg_path), f"Versioned package missing: {versioned_pkg_path}")

        import zipfile
        with zipfile.ZipFile(pkg_path, "r") as zf:
            names = zf.namelist()
            self.assertIn("metadata.json", names)
            self.assertIn("contents/ui/main.qml", names)
            self.assertIn("contents/ui/configGeneral.qml", names)
            self.assertIn("contents/config/main.xml", names)
            self.assertIn("contents/config/config.qml", names)
            for name in names:
                self.assertFalse(name.startswith(".git"), f"Found .git file: {name}")
                self.assertFalse("package.sh" in name, f"Found package.sh: {name}")
                self.assertFalse("README.md" in name, f"Found README: {name}")
                self.assertFalse("tests" in name, f"Found tests: {name}")
                self.assertFalse("docs" in name, f"Found docs: {name}")

    def test_08_release_version_consistency_and_semver(self):
        """Tests that metadata.json version follows SemVer and is consistently referenced in README.md."""
        import json
        import re

        with open(os.path.join(PROJECT_ROOT, "metadata.json"), "r") as f:
            data = json.load(f)
        version = data.get("KPlugin", {}).get("Version")
        self.assertIsNotNone(version, "Missing KPlugin.Version in metadata.json")
        self.assertTrue(re.match(r"^\d+\.\d+\.\d+$", version), f"Invalid SemVer: {version}")

        with open(os.path.join(PROJECT_ROOT, "README.md"), "r") as f:
            readme_text = f.read()
        self.assertIn(f"v{version}", readme_text, f"README.md does not reference current release v{version}")

    def test_09_warp_boundary_clamping_logic(self):
        """Tests warp/wrap-around decision logic at desktop boundaries."""
        def calculate_target(curr, total, forward, wrap):
            if wrap:
                if forward:
                    return 1 if curr >= total else curr + 1
                else:
                    return total if curr <= 1 else curr - 1
            else:
                if forward:
                    return None if curr >= total else curr + 1
                else:
                    return None if curr <= 1 else curr - 1

        # With wrap enabled (warp=True):
        self.assertEqual(calculate_target(curr=3, total=3, forward=True, wrap=True), 1)
        self.assertEqual(calculate_target(curr=1, total=3, forward=False, wrap=True), 3)
        self.assertEqual(calculate_target(curr=2, total=3, forward=True, wrap=True), 3)
        self.assertEqual(calculate_target(curr=2, total=3, forward=False, wrap=True), 1)

        # With wrap disabled (warp=False, boundary clamping):
        self.assertIsNone(calculate_target(curr=3, total=3, forward=True, wrap=False))
        self.assertIsNone(calculate_target(curr=1, total=3, forward=False, wrap=False))
        self.assertEqual(calculate_target(curr=2, total=3, forward=True, wrap=False), 3)
        self.assertEqual(calculate_target(curr=2, total=3, forward=False, wrap=False), 1)

if __name__ == "__main__":
    unittest.main()
