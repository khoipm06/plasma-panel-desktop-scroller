import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami
import org.kde.plasma.workspace.dbus as DBus

PlasmoidItem {
    id: root

    readonly property bool inEditMode: Plasmoid.containment?.corona?.editMode ?? false
    readonly property bool invertScroll: Plasmoid.configuration?.invertScroll ?? false
    readonly property int scrollThreshold: Plasmoid.configuration?.scrollThreshold ?? 60
    readonly property int cooldownMs: Plasmoid.configuration?.cooldownMs ?? 280

    preferredRepresentation: fullRepresentation

    Layout.fillWidth: false
    Layout.fillHeight: false
    Layout.preferredWidth: root.inEditMode ? Kirigami.Units.gridUnit * 1.5 : 0
    Layout.preferredHeight: root.inEditMode ? Kirigami.Units.gridUnit * 1.5 : 0

    Kirigami.Icon {
        anchors.centerIn: parent
        width: Kirigami.Units.iconSizes.smallMedium
        height: width
        source: "preferences-desktop-virtual-desktops"
        visible: root.inEditMode
    }

    property bool canSwitch: true

    Timer {
        id: cooldownTimer
        interval: root.cooldownMs
        repeat: false
        onTriggered: {
            root.canSwitch = true;
            wheelHandler.wheelDelta = 0;
        }
    }

    Timer {
        id: accumulationResetTimer
        interval: 400
        repeat: false
        onTriggered: {
            wheelHandler.wheelDelta = 0;
        }
    }

    function findTopItem(item) {
        let curr = item;
        while (curr && curr.parent) {
            curr = curr.parent;
        }
        return curr;
    }

    function initOverlay() {
        let top = findTopItem(root);
        if (top && fullPanelOverlay.parent !== top) {
            fullPanelOverlay.parent = top;
            fullPanelOverlay.x = 0;
            fullPanelOverlay.y = 0;
            fullPanelOverlay.width = Qt.binding(() => top ? top.width : 0);
            fullPanelOverlay.height = Qt.binding(() => top ? top.height : 0);
        }
    }

    Component.onCompleted: {
        Qt.callLater(initOverlay);
    }

    onParentChanged: {
        Qt.callLater(initOverlay);
    }

    Component.onDestruction: {
        if (fullPanelOverlay) {
            fullPanelOverlay.parent = null;
        }
    }

    Item {
        id: fullPanelOverlay
        z: 999999
        visible: !root.inEditMode
        enabled: !root.inEditMode

        WheelHandler {
            id: wheelHandler
            orientation: Qt.Vertical | Qt.Horizontal
            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
            enabled: !root.inEditMode
            property int wheelDelta: 0

            onWheel: (event) => {
                if (!root.canSwitch) {
                    return;
                }

                const rawDelta = Math.abs(event.angleDelta.y) >= Math.abs(event.angleDelta.x)
                    ? event.angleDelta.y
                    : -event.angleDelta.x;
                const delta = root.invertScroll ? -rawDelta : rawDelta;
                wheelDelta += delta;

                if (wheelDelta >= root.scrollThreshold) {
                    root.canSwitch = false;
                    wheelDelta = 0;
                    accumulationResetTimer.stop();
                    cooldownTimer.restart();
                    root.switchDesktop(false);
                } else if (wheelDelta <= -root.scrollThreshold) {
                    root.canSwitch = false;
                    wheelDelta = 0;
                    accumulationResetTimer.stop();
                    cooldownTimer.restart();
                    root.switchDesktop(true);
                } else {
                    accumulationResetTimer.restart();
                }
            }
        }
    }

    function switchDesktop(forward) {
        DBus.SessionBus.asyncCall({
            service: "org.kde.KWin",
            path: "/KWin",
            iface: "org.kde.KWin",
            member: forward ? "nextDesktop" : "previousDesktop"
        });
    }
}
