import PanelButton from "../PanelButton";
import icons from "lib/icons";
import GLib from "gi://GLib";

const hyprland = await Service.import("hyprland");
const HIS = GLib.getenv("HYPRLAND_INSTANCE_SIGNATURE");
const keyboardMap = {
    "Czech (QWERTY)": "CS",
    "English (US)": "US",
};

const getKeyboardLayout = () => {
    const devices = Utils.exec(`hyprctl --instance ${HIS} devices -j`);
    const keyboards = JSON.parse(devices).keyboards;
    let result = " ";
    for (const keyboard of keyboards) {
        if (keyboard.main) {
            if (keyboard.active_keymap in keyboardMap) {
                result += keyboardMap[keyboard.active_keymap];
            } else {
                result += keyboard.active_keymap;
            }
            break;
        }
    }

    return result;
};

const layout = Utils.watch(
    getKeyboardLayout(),
    hyprland,
    "keyboard-layout",
    () => getKeyboardLayout(),
);

const KeyboardWidget = () =>
    Widget.Box({
        children: [
            Widget.Icon(icons.ui.keyboard),
            Widget.Label({
                label: layout,
            }),
        ],
    });


export default () => {
    return PanelButton({
        class_name: "keyboard",
        on_primary_click: () => {
            Utils.execAsync(`${Utils.HOME}/.config/hypr/scripts/keyboard_layout.sh`);
        },
        child: KeyboardWidget(),
    });
}
