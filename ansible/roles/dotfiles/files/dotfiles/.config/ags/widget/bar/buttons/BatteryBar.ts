import icons from "lib/icons";
import options from "options";
import PanelButton from "../PanelButton";

const battery = await Service.import("battery");
const { bar, percentage, low } = options.bar.battery;

const Indicator = () =>
    Widget.Icon({
        setup: (self) =>
            self.hook(battery, () => {
                self.icon =
                    battery.charging || battery.charged
                        ? icons.battery.charging
                        : battery.icon_name;
            }),
    });

const PercentLabel = () =>
    Widget.Revealer({
        transition: "slide_right",
        click_through: true,
        reveal_child: percentage.bind(),
        child: Widget.Label({
            label: battery.bind("percent").as((p) => `${p}%`),
        }),
    });

const Regular = () =>
    Widget.Box({
        class_name: "regular",
        children: [Indicator(), PercentLabel()],
    });

export default () =>
    PanelButton({
        class_name: "battery-bar",
        hexpand: false,
        on_clicked: () => {
            percentage.value = !percentage.value;
        },
        visible: battery.bind("available"),
        child: Widget.Box({
            expand: true,
            visible: battery.bind("available"),
            child: Regular(),
        }),
        setup: (self) =>
            self
                .hook(bar, (w) =>
                    w.toggleClassName("bar-hidden", bar.value === "hidden"),
                )
                .hook(battery, (w) => {
                    w.toggleClassName(
                        "charging",
                        battery.charging || battery.charged,
                    );
                    w.toggleClassName("low", battery.percent < low.value);
                }),
    });
