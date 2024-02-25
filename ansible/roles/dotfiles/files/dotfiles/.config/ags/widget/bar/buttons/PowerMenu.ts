import icons from "lib/icons"
import PanelButton from "../PanelButton"
import options from "options"
import { wlogout_action } from "lib/utils"

const { monochrome } = options.bar.powermenu

export default () => PanelButton({
    window: "powermenu",
    on_clicked: wlogout_action,
    child: Widget.Icon(icons.powermenu.shutdown),
    setup: self => self.hook(monochrome, () => {
        self.toggleClassName("colored", !monochrome.value)
        self.toggleClassName("box")
    }),
})
