import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: root

    property alias cfg_invertScroll: invertScrollCheckBox.checked
    property alias cfg_scrollThreshold: scrollThresholdSpinBox.value
    property alias cfg_cooldownMs: cooldownSpinBox.value

    Kirigami.FormLayout {
        CheckBox {
            id: invertScrollCheckBox
            Kirigami.FormData.label: i18n("Scroll direction:")
            text: i18n("Invert scroll direction")
        }

        SpinBox {
            id: scrollThresholdSpinBox
            Kirigami.FormData.label: i18n("Sensitivity threshold:")
            from: 10
            to: 360
            stepSize: 10
            value: 60
            editable: true
            textFromValue: function(value, locale) {
                return i18n("%1 delta units", value);
            }
            valueFromText: function(text, locale) {
                return parseInt(text.replace(/[^0-9]/g, "")) || 60;
            }
        }

        SpinBox {
            id: cooldownSpinBox
            Kirigami.FormData.label: i18n("Switch cooldown:")
            from: 50
            to: 2000
            stepSize: 20
            value: 280
            editable: true
            textFromValue: function(value, locale) {
                return i18n("%1 ms", value);
            }
            valueFromText: function(text, locale) {
                return parseInt(text.replace(/[^0-9]/g, "")) || 280;
            }
        }
    }
}
