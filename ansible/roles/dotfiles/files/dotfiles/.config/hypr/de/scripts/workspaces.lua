#!/usr/bin/env lua

local cjson = require("cjson")

local function workspace_name(monitor_id, workspace_identifier)
    return monitor_id .. ":" .. workspace_identifier
end

local function run_command(command)
    local handle = io.popen(command)
    if handle == nil then
        io.stderr:write("Failed to run command: " .. command .. "\n")
        os.exit(1)
    end

    local output = handle:read("*a")
    handle:close()
    return output
end

local function get_active_monitor_id()
    local active_workspace = cjson.decode(run_command("hyprctl -j activeworkspace"))
    if active_workspace == nil then
        io.stderr:write("No active workspace found\n")
        os.exit(1)
    end
    return active_workspace.monitorID
end

local function find_next_available_id_for_workspace()
    local workspaces = cjson.decode(run_command("hyprctl -j workspaces"))
    local workspace_ids = {}
    for _, workspace in ipairs(workspaces) do
        table.insert(workspace_ids, workspace.id)
    end

    table.sort(workspace_ids)
    for i, id in ipairs(workspace_ids) do
        if i ~= id then
            return i
        end
    end
    return #workspace_ids + 1
end


local function get_workspace_id_for_workspace_name(workspace_name)
    local workspaces = cjson.decode(run_command("hyprctl -j workspaces"))
    for _, workspace in ipairs(workspaces) do
        if workspace.name == workspace_name then
            return workspace.id
        end
    end
    return nil
end

local function new_workspace(workspace)
    local active_monitor_id = get_active_monitor_id()
    local workspace_name = workspace_name(active_monitor_id, workspace)
    local workspace_id = get_workspace_id_for_workspace_name(workspace_name)
    local need_to_rename = false
    if workspace_id == nil then
        workspace_id = find_next_available_id_for_workspace()
        need_to_rename = true
    end

    run_command("hyprctl workspace " .. workspace_id)
    if need_to_rename then
        run_command("hyprctl dispatch renameworkspace " .. workspace_id .. " " .. workspace_name)
    end
end

local function move_active_window_to_workspace(workspace)
end

local function refresh_workspaces()
end

local function to_integer(str)
    local num = tonumber(str)
    if not num or num ~= math.floor(num) then
        return nil
    end
    return num
end

local function usage()
    return "Usage: " .. arg[0] .. " COMMAND [ARGS]\n" ..
        "Options:\n" ..
        "  -h, --help    Show this help message and exit\n" ..
        "Commands:\n" ..
        "  new-ws NUMBER    Create a new workspace or switch to an existing one on monitor\n" ..
        "  move-ws NUMBER   Move the active window to the specified workspace on monitor\n" ..
        "  refresh          Refresh the workspaces for all monitors\n" ..
        "  move-ws-to [left|right]  Move the active worspace to the left or right monitor\n"
end

local function parse_workspace_args(args)
    if #args < 1 then
        io.stderr:write(usage())
        os.exit(1)
    end

    local workspace_number = to_integer(args[1])
    if workspace_number == nil then
        io.stderr:write("Invalid workspace number: " .. args[1] .. "\n")
        io.stderr:write(usage())
        os.exit(1)
    end
    return workspace_number
end

local function parse_args(args)
    if #args < 1 then
        io.stderr:write(usage())
        os.exit(1)
    end

    local command = args[1]
    if command == "new" then
        new_workspace(parse_workspace_args(args))
    elseif command == "move" then
        move_active_window_to_workspace(parse_workspace_args(args))
    elseif command == "refresh" then
        refresh_workspaces()
    elseif command == "--help" or command == "-h" then
        print(usage())
    else
        io.stderr:write("Invalid command: " .. command .. "\n")
        io.stderr:write(usage())
        os.exit(1)
    end
end

parse_args({...})
