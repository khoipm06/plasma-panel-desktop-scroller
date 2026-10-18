# Panel Desktop Scroller

A lightweight KDE Plasma 6 widget that enables switching virtual desktops by scrolling anywhere on the panel.

## Features

- **Full-Panel Scrolling**: Scroll anywhere on the panel to switch virtual desktops smoothly.
- **Native Wayland & X11 DBus**: Uses native Qt6/Plasma 6 DBus calls (`org.kde.KWin`) directly in compositor memory with zero subshell or external process overhead.
- **Configurable Behavior**:
  - Invert scroll direction.
  - Adjustable sensitivity threshold to prevent accidental triggering on trackpads or sensitive mouse wheels.
  - Configurable cooldown timer between switches.
- **Zero Visual Clutter**: Invisible during normal desktop usage; reveals an icon during Plasma Edit Mode for easy repositioning or removal.
- **Multi-Panel Support**: Seamlessly supports multiple panels across multi-monitor setups.

## Requirements

- **KDE Plasma 6.0+**
- **Qt 6**

## Installation

### Method 1: Using `kpackagetool6` (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/khoipm06/plasma-panel-desktop-scroller.git
   cd plasma-panel-desktop-scroller
   ```

2. Build and install the package:
   ```bash
   ./scripts/package.sh
   kpackagetool6 -i build/com.github.khoipm06.panelscroller.plasmoid
   ```

   To upgrade an existing installation:
   ```bash
   kpackagetool6 -u build/com.github.khoipm06.panelscroller.plasmoid
   ```

3. Restart Plasma Shell to load the new widget:
   ```bash
   systemctl --user restart plasma-plasmashell
   ```

### Method 2: Manual Installation

Copy the repository contents directly into your user plasmoids directory:

```bash
mkdir -p ~/.local/share/plasma/plasmoids/com.github.khoipm06.panelscroller
cp -r contents metadata.json ~/.local/share/plasma/plasmoids/com.github.khoipm06.panelscroller/
systemctl --user restart plasma-plasmashell
```

## Usage & Configuration

1. Right-click on your panel and select **Enter Edit Mode** (or press `Meta+Alt+D`).
2. Click **Add Widgets...** and search for **Panel Desktop Scroller**.
3. Drag the widget onto your panel.
4. To configure sensitivity or scroll direction, right-click the widget icon while in Edit Mode and choose **Configure Panel Desktop Scroller...**.
5. Once positioned, exit Edit Mode. The icon will hide automatically, and scrolling anywhere on that panel will switch virtual desktops.

## License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.
