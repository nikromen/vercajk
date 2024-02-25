import { type TrayItem } from "types/service/systemtray";
import PanelButton from "../PanelButton";
import options from "options";

const systemtray = await Service.import("systemtray");
const { ignore } = options.bar.systray;

const SysTrayItem = (item: TrayItem) =>
    Widget.EventBox({
        class_name: "tray-item",
        child: Widget.Icon({ icon: item.bind("icon") }),
        tooltip_markup: item.bind("tooltip_markup"),
        setup: (self) => {
            const { menu } = item;
            if (!menu) {
                return;
            }

            const id = menu.connect("popped-up", () => {
                self.toggleClassName("active");
                menu.connect("notify::visible", () => {
                    self.toggleClassName("active", menu.visible);
                });
                menu.disconnect(id!);
            });

            self.connect("destroy", () => menu.disconnect(id));
        },

        on_primary_click: (_, event) => item.activate(event),
        on_secondary_click: (_, event) => item.openMenu(event),
    });

export default () => {
    const box = Widget.Box().bind("children", systemtray, "items", (i) =>
        i.filter(({ id }) => !ignore.value.includes(id)).map(SysTrayItem),
    );
    if (systemtray.items.length === 0) {
        return null;
    }
    return PanelButton({ child: box });
};
