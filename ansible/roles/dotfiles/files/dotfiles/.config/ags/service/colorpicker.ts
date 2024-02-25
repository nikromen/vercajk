import { bash } from "lib/utils";

const COLORS_CACHE = Utils.CACHE_DIR + "/colorpicker.json";
const MAX_NUM_COLORS = 10;

class ColorPicker extends Service {
    static {
        Service.register(
            this,
            {},
            {
                colors: ["jsobject"],
            },
        );
    }

    #colors = JSON.parse(Utils.readFile(COLORS_CACHE) || "[]") as string[];

    get colors() {
        return [...this.#colors];
    }
    set colors(colors) {
        this.#colors = colors;
        this.changed("colors");
    }

    readonly pick = async () => {
        const color = await bash("hyprpicker -r");
        bash(`wl-copy "${color}"`);
        if (!color) return;

        const list = this.colors;
        if (!list.includes(color)) {
            list.push(color);
            if (list.length > MAX_NUM_COLORS) list.shift();

            this.colors = list;
            Utils.writeFile(JSON.stringify(list, null, 2), COLORS_CACHE);
        }
    };
}

export default new ColorPicker();
