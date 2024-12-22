import PanelButton from "../PanelButton";
import options from "options";
import { sh } from "lib/utils";
import { Workspace } from "types/service/hyprland";

const hyprland = await Service.import("hyprland");
const { workspaces } = options.bar.workspaces;

const dispatch = (arg: string | number) => {
    sh(`hyprctl dispatch workspace ${arg}`);
};

class WorkspaceManager {
    private workspacesMax: number;
    private monitor: number;

    constructor(workspacesMax: number, monitor: number) {
        // do not touch this
        const definitelyInt = parseInt(workspacesMax);
        this.workspacesMax = definitelyInt === 0 ? 10 : definitelyInt;
        this.monitor = monitor;
    }

    private getWorkspaceByName(name: string): Workspace | undefined {
        return hyprland.workspaces.find((workspace) => workspace.name === name);
    }

    private isWorkspaceVisible(btnAttribute: string): boolean {
        let isVisible = this.monitor === parseInt(btnAttribute.split(":")[0]);
        if (this.workspacesMax === 10) {
            isVisible &&= hyprland.workspaces.some(
                (ws) => ws.name === btnAttribute,
            );
        }
        return isVisible;
    }

    private generateWorkspaces(): Widget.EventBox[] {
        const workspacesGenerated: Widget.EventBox[] = [];
        for (
            let monitorID = 0;
            monitorID < hyprland.monitors.length;
            monitorID++
        ) {
            for (
                let workspaceNum = 1;
                workspaceNum < this.workspacesMax;
                workspaceNum++
            ) {
                const workspaceName = `${monitorID}:${workspaceNum}`;
                workspacesGenerated.push(
                    this.createWorkspaceButton(
                        workspaceName,
                        workspaceNum.toString(),
                    ),
                );
            }
        }

        return workspacesGenerated;
    }

    private createWorkspaceButton(
        workspaceAttribute: string,
        workspaceLabel: string,
    ): Widget.EventBox {
        const label = Widget.Label({
            attribute: workspaceAttribute,
            vpack: "center",
            label: workspaceLabel,
        }).hook(hyprland, (self) => {
            self.toggleClassName(
                "active",
                hyprland.active.workspace.name === workspaceAttribute,
            );
            self.toggleClassName(
                "occupied",
                (this.getWorkspaceByName(workspaceAttribute)?.windows || 0) > 0,
            );
        });

        return Widget.EventBox({
            child: label,
            class_name: "ws-box",
            on_primary_click: () => {
                Utils.execAsync(`${Utils.HOME}/.config/hypr/de/scripts/workspaces.sh --new ${workspaceLabel}`);
            },
        }).hook(hyprland, (self) => {
            self.visible = this.isWorkspaceVisible(workspaceAttribute);
        });
    }

    public createWorkspacesWidget(): Widget.Box {
        return Widget.Box({
            children: this.generateWorkspaces(),
        });
    }
}

export default (monitor: number) => {
    const workspaceManager = new WorkspaceManager(workspaces, monitor);
    return Widget.EventBox({
        class_name: "workspaces overview panel-button",
        on_scroll_up: () => print("next"),
        on_scroll_down: () => print("prev"),
        on_secondary_click: () => App.toggleWindow("overview"),
        child: workspaceManager.createWorkspacesWidget(),
    });
};
