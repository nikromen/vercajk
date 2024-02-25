import Gdk from "gi://Gdk";

import BatteryBar from "./buttons/BatteryBar";
import ColorPicker from "./buttons/ColorPicker";
import Date from "./buttons/Date";
import Media from "./buttons/Media";
import PowerMenu from "./buttons/PowerMenu";
import SysTray from "./buttons/SysTray";
import SystemIndicators from "./buttons/SystemIndicators";
import Workspaces from "./buttons/Workspaces";
import ScreenRecord from "./buttons/ScreenRecord";
import Messages from "./buttons/Messages";
import Keyboard from "./buttons/Keyboard";
import options from "options";

const hyprland = await Service.import("hyprland");
const { start, center, end } = options.bar.layout;
const { transparent, position } = options.bar;

export type BarWidget = keyof typeof widget;

const widget = {
    battery: BatteryBar,
    colorpicker: ColorPicker,
    date: Date,
    media: Media,
    powermenu: PowerMenu,
    systray: SysTray,
    system: SystemIndicators,
    workspaces: Workspaces,
    screenrecord: ScreenRecord,
    messages: Messages,
    keyboard: Keyboard,
    expander: () => Widget.Box({ expand: true }),
};

const processWidgets = (widgets: BarWidget[], monitor: number) => {
    let hyprlandMonitorNumber = monitor;
    const monitorModel = Gdk.Display.get_default()
        ?.get_monitor(monitor)
        ?.get_model();
    if (monitorModel) {
        for (const monitor of hyprland.monitors) {
            if (monitor.model === monitorModel) {
                hyprlandMonitorNumber = monitor.id;
            }
        }
    }

    return widgets.map((w) =>
        w === "workspaces" ? widget[w](hyprlandMonitorNumber) : widget[w](),
    );
};

export default (monitor: number) =>
    Widget.Window({
        monitor,
        class_name: "bar",
        name: `bar${monitor}`,
        exclusivity: "exclusive",
        anchor: position.bind().as((pos) => [pos, "right", "left"]),
        child: Widget.CenterBox({
            css: "min-width: 2px; min-height: 2px;",
            startWidget: Widget.Box({
                hexpand: true,
                children: start.bind().as((s) => processWidgets(s, monitor)),
            }),
            centerWidget: Widget.Box({
                hpack: "center",
                children: center.bind().as((c) => processWidgets(c, monitor)),
            }),
            endWidget: Widget.Box({
                hexpand: true,
                children: end.bind().as((e) => processWidgets(e, monitor)),
            }),
        }),
        setup: (self) =>
            self.hook(transparent, () => {
                self.toggleClassName("transparent", transparent.value);
            }),
    });
