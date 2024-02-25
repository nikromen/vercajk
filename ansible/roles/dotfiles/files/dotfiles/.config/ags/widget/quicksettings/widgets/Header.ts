import icons from "lib/icons";
import options from "options";

const { image, size } = options.quicksettings.avatar;

const Avatar = () =>
    Widget.Box({
        class_name: "avatar",
        css: Utils.merge(
            [image.bind(), size.bind()],
            (img, size) => `
        min-width: ${size}px;
        min-height: ${size}px;
        background-image: url('${img}');
        background-size: cover;
    `,
        ),
    });

const WLogoutButton = () =>
    Widget.Button({
        vpack: "center",
        child: Widget.Icon(icons.powermenu.shutdown),
        on_clicked: () => Utils.execAsync("wlogout -p layer-shell"),
    });

export const Header = () =>
    Widget.Box(
        { class_name: "header horizontal" },
        Avatar(),
        Widget.Box({ hexpand: true }),
        Widget.Button({
            vpack: "center",
            child: Widget.Icon(icons.ui.settings),
            on_clicked: () => {
                App.closeWindow("quicksettings");
                App.closeWindow("settings-dialog");
                App.openWindow("settings-dialog");
            },
        }),
        WLogoutButton(),
    );
