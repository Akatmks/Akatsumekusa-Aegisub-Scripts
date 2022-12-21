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

------------------------------------------------------------------------------
-- If you want to have a try at aka.config, here is a small tutorial.
-- 
-- While this module is called aka.config, you can serialise anything you want
-- using this module, not only configs. Comparing to other serialisation
-- modules like DepCtrl's ConfigHandler, this module creates a prettified JSON
-- which the user can edit inside Aegisub.
-- Another feature provided by aka.config is that you can have multiple
-- presets or templates for the user to choose from when they first run the
-- script.
-- 
-- In order to 

local json = require("aka.config.json")
local re = require("aegisub.re")
local unicode = require("aegisub.unicode")
local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
local functions = {}

local json_error
local json_error_table
local reset_json_error
local config_dir
local set_config_dir
local validate
local selected_template_keys
local get_template_key
local select_template_key
local config_gui
local config_no_gui

json_error = false
json_error_table = {}
json.onDecodeError = function(message, text, location, etc)
    local matches
    local i

    if not text or not location or not etc then return end
    if json_error == false then json_error = 1
    else json_error = json_error + 1 end

    location = "\n" .. location .. "\n"
    etc = etc + 1
    matches = re.find(location, "(\\r|\\n|\\r\\n)")
    i = 1
    while matches[i + 1] do
        if etc == 2 then
            table.insert(json_error_table, text)
            return
        elseif etc > matches[i]["last"] and etc <= matches[i + 1]["first"] then
            table.insert(json_error_table, text .. " in line " .. tostring(i) .. " column " .. tostring(unicode.len(string.sub(location, matches[i]["last"] + 1, etc - 1)) + 1))
            json_error = json_error + 1
            table.insert(json_error_table, "`" .. string.sub(location, matches[i]["last"] + 1, matches[i + 1]["first"] - 1) .. "`")
            return
        end
        i = i + 1
    end
    assert(false) end
reset_json_error = function() json_error = false json_error_table = {} end
json.decode2 = function(text, etc, options) reset_json_error() return json:decode(text, etc, options) end

config_dir = aegisub.decode_path(hasDepCtrl and DepCtrl.config.c.configDir or "?user/config")

------------------------------------------------
-- Read the specified config and return a table.
-- This is the only function to run when loading config.
-- If the config wasn't successfully read, please always run edit_config_gui() instead.
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder [""]: The subfolder where the config is in; Set this to "" if the config are in the root config dir
-- @param func validation_func [function() return true end]: The function to validate the config before sending back;
--                                                           It should take the config data as param and return true if the validation is sucessful,
--                                                           Otherwise it should return an int as error message count and a table of string as error messages
-- 
-- @returns bool is_success: True if the config was successfully read
-- @returns table config_data: The table read from the config
functions.read_config = function(config, subfolder, validation_func)
    subfolder = subfolder or ""
    validation_func = validation_func or function() return true end

    local config_file
    local config_data

    config_file = io.open(config_dir .. "/" .. subfolder .. (subfolder ~= "" and "/" or "") .. config .. ".json", "r")
    if config_file then
        config_data = json.decode2(config_file:read("*all"))
        assert(config_file:close())
        if not json_error and validation_func(config_data) == true then
            return true, config_data
    end end
    return false, config_data end
-------------------------------------------------
-- Overwrite the specified config with the table.
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder [""]: The subfolder where the config is in;
--                               Set this to "" if the config are in the root config directory
-- @param table config_data: The table to save to the config
-- 
-- @returns bool is_success: True if the config was successfully saved
functions.write_config = function(config, subfolder, config_data)
    subfolder = subfolder or ""

    local config_directory
    local config_file
    local is_success, err, code
    
    config_directory = config_dir .. (subfolder ~= "" and "/" or "") .. subfolder
    is_success, err, code = os.rename(config_directory, config_directory)
    if not is_success and code == 2 then
        if package.config:sub(1, 1) == "\\" then
            is_success = os.execute("MKDIR " .. config_directory)
        else -- package.config:sub(1, 1) == "/"
            is_success = os.execute("mkdir -p " .. config_directory)
        assert(is_success)
    end end

    config_file = assert(io.open(config_directory .. "/" .. config .. ".json", "w"))
    config_file:write(json:encode_pretty(config_data))
    assert(config_file:close())
    return true end
------------------------------------------------
-- Open the GUI and edit the config, either when the user asks for an edit, or when the config failed to parse or is not found
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder [""]: The subfolder where the config is in;
--                               Set this to "" if the config are in the root config directory
-- @param func validation_func [function() return true end]: The function to validate the config before sending back;
--                                                           It should take the config data as param and return true if the validation is sucessful,
--                                                           Otherwise it should return an int as error message count and a table of string as error messages
-- @param func ui_func [nil]: The function to display a custom ui instead of the default JSON editor;
--                            It will be fed with three params, current config string, error message count and error messages;
--                            error message count will be 0 either when the string is "" or when the string passed validation_func;
--                            It should return the new config string which will then be put into validation_func;
--                            In case the user cancel the ui or escape the ui, the function should return false
-- @param str word_name_b: The name of the config for display in the title of GUI
-- @param str word_config_b ["𝗖𝗼𝗻𝗳𝗶𝗴"]: The English word for config
-- @param str word_template ["Template"]: The English word for template
-- @param str word_templates_b ["𝗧𝗲𝗺𝗽𝗹𝗮𝘁𝗲𝘀"]: The English word for templates
-- @param table config_templates: Templates for the config
-- @param bool is_no_gui_init [false]: Do not show GUI but instead use the first config template to create config
--
-- @returns bool is_success: True if the config was sucessfully created or validated
-- @returns table config_data: The table read from the config
functions.edit_config_gui = function(config, subfolder, validation_func, ui_func, word_name_b, word_config_b, word_template, word_templates_b, config_templates, is_no_gui_init)
    subfolder = subfolder or ""
    validation_func = validation_func or function() return true end
    word_config_b = word_config_b or "𝗖𝗼𝗻𝗳𝗶𝗴"
    word_templates_b = word_templates_b or "𝗧𝗲𝗺𝗽𝗹𝗮𝘁𝗲𝘀"

    local config_file
    local config_string
    local config_data
    local msg_count
    local msg
    
    config_file = io.open(config_dir .. "/" .. subfolder .. (subfolder ~= "" and "/" or "") .. config .. ".json", "r")
    if not config_file then
        config_string = ""
    else
        config_string = config_file:read("*all")
        assert(config_file:close())
    end

    if is_no_gui_init and config_string == "" then
        config_data = json.decode2(config_no_gui(config_templates))
        assert(json_error == false)
    else
        if config_string == "" then msg_count = 0 msg = {}
        else
            msg_count, msg, config_data = validate(config_string, validation_func)
            if msg_count == true then msg_count = 0 msg = {} end
        end
        repeat
            if ui_func then config_string = ui_func(config_string, msg_count, msg)
            else config_string = config_gui(config_string, msg_count, msg, word_name_b, word_config_b, word_template, word_templates_b, config_templates) end
            if config_string == false then return false
            else
                msg_count, msg, config_data = validate(config_string, validation_func)
            end
        until msg_count == true
    end
    
    return functions.write_config(config, subfolder, config_data), config_data end
------------------------------------------------
-- @param str config_string: The config to be validated
-- @param func validation_func [function() return true end]: The function to validate the config before sending back;
--                                                           It should take the config data as param and return true if the validation is sucessful,
--                                                           Otherwise it should return an int as error message count and a table of string as error messages
-- 
-- @returns bool is_valid or int msg_count: Either return true if the config is valid, or return the count of error messages
-- @returns table msg: Return the error messages for the error in the config
-- @returns table config_data: Return the config table if valid
validate = function(config_string, validation_func)
    local config_data
    local msg_count
    local msg

    if config_string == "" then msg_count = 1 msg = { "Root object not found" }
    else
        config_data = json.decode2(config_string)
        if json_error then
            msg_count = json_error msg = json_error_table
        else -- not json_error
            msg_count, msg = validation_func(config_data)
    end end
    return msg_count, msg, config_data end

selected_template_keys = nil
get_template_key = function(config_templates)
    local it
    local swap

    if selected_template_keys then
        if config_templates[selected_template_keys.key] then
            return selected_template_keys.key
        end
        it = selected_template_keys
        while it.next ~= nil do
            if config_templates[it.next.key] then
                swap = it.next.next
                it.next.next = selected_template_keys
                selected_template_keys = it.next
                it.next = swap
                return selected_template_keys.key
            end
            it = it.next
    end end

    for k in pairs(config_templates) do
        selected_template_keys = { key = k, next = selected_template_keys }
        return k
    end end
select_template_key = function(template_key)
    local fake_templates

    fake_templates = {}
    fake_templates[template_key] = ""
    get_template_key(fake_templates) end

------------------------------------------------
-- @param str config_string: The current config to be filled into the left panel
-- @param int msg_count: The number of messages
-- @param table msg: The messages to display on the top of the right panel
-- @param str word_name_b: The name of the config for display in the title of GUI
-- @param str word_config_b: The English word for config
-- @param str word_template: The English word for template
-- @param str word_templates_b: The English word for templates
-- @param table config_templates: Templates for the config
-- 
-- @returns str config_string or bool is_success: Either the user input to the left panel, or false if the user escape the gui
config_gui = function(config_string, msg_count, msg, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
    local dialog
    local buttons
    local button_ids
    local button
    local result_table
    local templates
    local template
    local height
    local height_template_textbox

    templates = {}
    for k in pairs(config_templates) do table.insert(templates, k) end
    template = get_template_key(config_templates)
    if msg_count == 0 then height = 19 height_template_textbox = height - 2
    elseif msg_count <= 13 then height = 19 height_template_textbox = height - msg_count - 3
    else height = msg_count + 6 height_template_textbox = 3 end

    while true do
        dialog = { { class = "label",                           x = 0, y = 0, width = 32,
                                                                label = (config_string == "" and "𝗖𝗿𝗲𝗮𝘁𝗲 " or "𝗘𝗱𝗶𝘁 ") .. word_config_b .. " 𝗳𝗼𝗿 " .. word_name_b .. ":" },
                   { class = "textbox", name = "config_text",   x = 0, y = 1, width = 32, height = height - 1,
                                                                text = config_string },
                   { class = "label",                           x = 32, y = height - height_template_textbox - 2, width = 32,
                                                                label = word_templates_b .. ":" },
                   { class = "textbox", name = "template_text", x = 32, y = height - height_template_textbox - 1, width = 32, height = height_template_textbox,
                                                                text = config_templates[template] },
                   { class = "label",                           x = 32, y = height - 1, width = 8,
                                                                label = "Select " .. word_template .. ":" },
                   { class = "dropdown", name = "template",     x = 40, y = height - 1, width = 24,
                                                                items = templates, value = template } }
        if msg_count ~= 0 then
            table.insert(dialog, { class = "label",             x = 32, y = 0, width = 32,
                                                                label = "𝗘𝗿𝗿𝗼𝗿 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱:" })
            for k, v in ipairs(msg) do
                table.insert(dialog, { class = "label",         x = 32, y = k, width = 32,
                                                                label = v })
        end end
        buttons = { "&Apply", "Apply " .. word_template, "View &" .. word_template, "Diminish" }
        button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Diminish", no = "Diminish", cancel = "Diminish" }

        button, result_table = aegisub.dialog.display(dialog, buttons, button_ids)

        if button == false or button == "Diminish" then return false
        elseif button == "&Apply" then return result_table["config_text"]
        elseif button == "Apply " .. word_template then return config_templates[result_table["template"]]
        else -- button == "View &" .. word_template
            config_string = result_table["config_text"]
            template = result_table["template"]
            select_template_key(template)
    end end end
------------------------------------------------
-- @param table config_templates: Templates for the config
-- 
-- @returns str config_string: The first template in the templates table
config_no_gui = function(config_templates)
    for k, v in pairs(config_templates) do select_template_key(k) return v end end

return functions
