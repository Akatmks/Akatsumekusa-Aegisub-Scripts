-- config.lua
-- Copyright (c) Akatsumekusa

------------------------------------------------------------------------------
-- Permission is hereby granted, free of charge, to any person obtaining a
-- copy of this software and associated documentation files (the "Software"),
-- to deal in the Software without restriction, including without limitation
-- the rights to use, copy, modify, merge, publish, distribute, sublicense,
-- and/or sell copies of the Software, and to permit persons to whom the
-- Software is furnished to do so, subject to the following conditions:

-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.

-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
-- FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
-- DEALINGS IN THE SOFTWARE.
------------------------------------------------------------------------------

local json = require("aka/config/dkjson")

local config_dir = nil
local set_config_dir = function()
    local dep_ctrl_file
    local dep_ctrl_config

    global config_dir

    dep_ctrl_file = io.open(aegisub.decode_path("?user/config/l0.DependencyControl.json"))
    if dep_ctrl_file then
        dep_ctrl_config = json:decode(dep_ctrl_file:read("*all"))
        if dep_ctrl_config and dep_ctrl_config.config and dep_ctrl_config.config.configDir then
            config_dir = string.sub(dep_ctrl_config.config.configDir, -1) ~= "/" and dep_ctrl_config.config.configDir or string.sub(dep_ctrl_config.config.configDir, 1, -2)
            return
    end end
    config_dir = "?user/config" end
set_config_dir()

local functions = {}
------------------------------------------------
-- Read the specified config and return a table.
-- This is the only function to run when loading config.
-- If the config wasn't successfully read, please always run edit_config_gui() instead.
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder ["aka"]: The subfolder where the config is in; Set this to "" if the config are in the root config dir
-- @param func validation_func [function() return true end]: The function to validate the config before sending back;
--                                                           It should take the table as param and return true if the validation is sucessful,
--                                                           Otherwise it should return an error message
-- 
-- @returns bool is_success: True if the config was successfully read
-- @returns table config_data: The table read from the config
functions.read_config = function(config, subfolder, validation_func)
    subfolder = subfolder or "aka"
    validation_func = validation_func or function() return true end

    local config_file
    local config_data
    local err

    config_file = io.open(aegisub.decode_path(config_dir .. "/" .. subfolder .. (subfolder ~= "" and "/" or "") .. config .. ".json"), "r")
    if config_file then
        config_data, _, err = json:decode(config_file:read("*all"))
        assert(config_file:close())
        if not err and validation_func == true then
            return true, config_data
    end end
    return false, nil end

-------------------------------------------------
-- Overwrite the specified config with the table.
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder ["aka"]: The subfolder where the config is in;
--                               Set this to "" if the config are in the root config directory
-- @param table config_data: The table to save to the config
-- 
-- @returns bool is_success: True if the config was successfully saved
functions.write_config = function(config, subfolder, config_data)
    subfolder = subfolder or "aka"

    local config_directory
    local config_file
    local is_success, err, code
    
    config_directory = config_dir .. (subfolder ~= "" and "/" or "") .. subfolder
    is_success, err, code = os.rename(config_directory, config_directory)
    if not is_success then
        assert(code == 2)
        if package.config:sub(1, 1) == "\\" then
            is_success = os.execute("MKDIR " .. aegisub.decode_path(config_directory))
        else -- package.config:sub(1, 1) == "/"
            is_success = os.execute("mkdir -p " .. aegisub.decode_path(config_directory))
        assert(is_success)
    end end

    config_file = assert(io.open(aegisub.decode_path(config_directory .. "/" .. config .. ".json"), "w"))
    config_file:write(json:encode(config_data, { indent = true }))
    assert(config_file:close())
    return true end
------------------------------------------------
-- Open the GUI and edit the config, either when the user asks for an edit, or when the config failed to parse or is not found
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder ["aka"]: The subfolder where the config is in;
--                               Set this to "" if the config are in the root config directory
-- @param func validation_func [function() return true end]: The function to validate the config before sending back;
--                                                           It should take the table as param and return true if the validation is sucessful,
--                                                           Otherwise it should return an error message
-- @param str config_name: The name of the config for display in the title of GUI
-- @param table config_templates: Templates for the config
-- @param bool is_no_gui [false]: Do not show GUI but instead use the first config template to create config
--
-- @returns bool is_success: True if the config was sucessfully created or validated
functions.edit_config_gui = function(config, subfolder, validation_func, config_name, config_templates, is_no_gui)
    subfolder = subfolder or "aka"
    validation_func = validation_func or function() return true end

    local config_file
    local config_string
    local msg
    
    config_file = io.open(aegisub.decode_path(config_dir .. "/" .. subfolder .. (subfolder ~= "" and "/" or "") .. config .. ".json"), "r")
    if not config_file then
        config_string = ""
    else
        config_string = config_file:read("*all")
        assert(config_file:close())
    end

    if is_no_gui and config_string == "" then config_string = config_no_gui(config_templates)
    else
        msg = validate(config_string)
        if msg == true then msg = "Edit config for " .. config_name
        repeat
            config_string = config_gui(config_string, msg, config_templates)
            if config_string == false then return false
            else
                msg = validate(config_string)
            end
        until msg == true
    return functions.write_config(config, subfolder, json:decode(config_string)) end
------------------------------------------------
-- @param str config: The config to be validated
-- @param func validation_func [function() return true end]: The function to validate the config before sending back;
--                                                           It should take the table as param and return true if the validation is sucessful,
--                                                           Otherwise it should return an error message
-- @param str config_name: The name of the config for display in the title of GUI
-- 
-- @returns bool is_valid or str msg: Either return true if the config is valid, or return the error message for the error in the config
local validate = function(config, validation_func, config_name)
    local config_data
    local msg

    if config == "" then local msg = "Create config for " .. config_name
    else
        config_data, _, msg = json:decode(config)
        if not msg then
            msg = validation_func(config_data)
    end end
    return msg end

local selected_template_keys = nil
local get_template_key = function(config_templates)
    global selected_template_keys

    local it
    local swap

    if selected_template_keys == nil then
        for k in pairs(config_templates) do
            selected_template_keys = { key = k, next = nil }
            return k
        end
    else
        it = { next = selected_template_keys }
        while it.next != nil do
            if config_templates[it.next.key] then
                swap = it.next.next
                it.next.next = selected_template_keys
                selected_template_keys = it.next
                it.next = swap
                return selected_template_keys.key
            else
                it = it.ext
        end end
        for k in pairs(config_templates) do
            selected_template_keys = { key = k, next = selected_template_keys }
            return k
    end end end
local select_template_key = function(template_key)
    local fake_templates

    fake_templates = {}
    fake_templates[template_key] = ""
    get_template_key(fake_templates) end

------------------------------------------------
-- @param str config_string: The current config to be filled into the left panel
-- @param str msg: The message to display and the top of the right panel
-- @param table config_templates: Templates for the config
-- 
-- @returns str config_string or bool is_success: Either the user input to the left panel, or false if the user escape the gui
local config_gui = function(config, msg, config_templates)
    local dialog
    local buttons
    local button_ids
    local button
    local result_table
    local templates
    local template

    templates = {}
    for k in pairs(config_templates) do
        table.insert(templates, k)
    end
    template = nil

    while true do
        template = template or get_template_key(config_templates)
        dialog = { { class = "textbox", name = "config_text",    x = 0, y = 0, width = 10, height = 15,  text = config },
                   { class = "label",                            x = 10, y = 0, width = 10,              label = msg },
                   { class = "textbox", name = "template_text",  x = 10, y = 1, width = 10, height = 13, text = config_templates[template] },
                   { class = "label",                            x = 10, y = 14,                         label = "Templates: " },
                   { class = "dropdown", name = "template",      x = 12, y = 14, width = 8,              items = templates, value = template } }
        buttons = { "&Apply", "Load &Template", "Diminish" }
        button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Diminish", no = "Diminish", cancel = "Diminish" }

        button, result_table = aegisub.dialog.display(dialog, buttons, button_ids)

        if button == false or button == "Diminish" then return false
        elseif button == "&Apply" then return result_table["template_text"]
        else -- button == "Load &Template"
            template = result_table[template]
    end end end
------------------------------------------------
-- @param table config_templates: Templates for the config
-- 
-- @returns str config_string: The first template in the templates table
local config_no_gui = function(config_templates)
    for k, v in pairs(config_templates) do select_template_key(k) return v end end

return functions
