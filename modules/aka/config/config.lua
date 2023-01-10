-- aka.config
-- Copyright (c) Akatsumekusa and contributors

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

local config2 = require("aka.config2")
local json = config2.json
local has_template, atemplate = pcall(require, "aka.template")
if not has_template then atemplate = nil end

local edit_config_gui
local validate
local config_gui2
local config_gui3
local config_gui
local config_no_gui

------------------------------------------------
-- Open the GUI and edit the config, either when the user asks for an edit, or when the config failed to parse or is not found
-- 
-- This function is also overloaded, at full, it is:
-- function(string config, string subfolder,
--          function validation_func, function ui_func, function validation_func_ui,
--          table words, table config_templates,
--          boolean is_no_gui_init)
-- Among these arguments, string subfolder, function validation_func, function ui_func, function validation_func_ui
-- and boolean is_no_gui_init can be omitted in place
-- 
-- @param string config: The name for the config file without the file extension
-- @param string subfolder [""]: The subfolder where the config is in;
--                               Set this to "" if the config are in the root config directory
-- @param function validation_func [function() return true end]: The function to validate the config before sending back;
--                                                               It should take the config data as param and return true if the validation is sucessful,
--                                                               Otherwise it should return an int as error message count and a table of string as error messages
-- @param function ui_func [nil]: The function to display a custom ui instead of the default JSON editor;
--                                It should take the config data as param and return true and the new config data as table if sucessful,
--                                If for whatever reason it wants to open the default JSON editor instead, it should return a string "JSON" and a new config data table to be converted to string;
--                                After the user close the JSON editor, the new new config data will be fed back to the ui_func again.
--                                In case the user cancel the ui or escape the ui, the function should return false
-- @param function validation_func_ui [validation_func]: The function to validate the config before sending to ui_func
-- @param table words The words to be displayed in the GUI, which contains these key-value pairs:
--        string name_b: The name of the config for display in the title of GUI, bold
--        string config_b ["𝗖𝗼𝗻𝗳𝗶𝗴"]: The English word for config, bold
--        string template ["Template"]: The English word for template
--        string templates_b ["𝗧𝗲𝗺𝗽𝗹𝗮𝘁𝗲𝘀"]: The English word for templates, bold
-- @param table config_templates: Templates for the config
-- @param boolean is_no_gui_init [false]: Do not show GUI but instead use the first config template to create config
--
-- @returns bool is_success: True if the config was sucessfully created or validated
-- @returns table config_data: The table read from the config
edit_config_gui = function(...)
    local config
    local subfolder
    local validation_func
    local ui_func
    local validation_func_ui
    local word_name_b
    local word_config_b
    local word_template
    local word_templates_b
    local config_templates
    local is_no_gui_init
    assert(type(arg[1]) == "string") config = arg[1]
    if type(arg[2]) ~= "string" then table.insert(arg, 2, "") end subfolder = arg[2]
    if type(arg[3]) ~= "function" then table.insert(arg, 3, function() return true end) end validation_func = arg[3]
    if type(arg[4]) ~= "function" then table.insert(arg, 3, nil) end validation_func = arg[3]
    if type(arg[5]) ~= "function" then table.insert(arg, 3, validation_func) end validation_func = arg[3]
    assert(type(arg[6]) == "table") assert(arg[6]["name_b"])
    word_name_b = arg[6]["name_b"] word_config_b = arg[6]["config_b"] word_template = arg[6]["template"] word_templates_b = arg[6]["templates_b"]
    assert(type(arg[7]) == "table") config_templates = arg[7]
    is_no_gui_init = arg[8] or false

    subfolder = subfolder or ""
    validation_func = validation_func or function() return true end
    validation_func_ui = validation_func_ui or validation_func
    assert(word_name_b ~= nil)
    word_config_b = word_config_b or "𝗖𝗼𝗻𝗳𝗶𝗴"
    word_template = word_template or "Template"
    word_templates_b = word_templates_b or "𝗧𝗲𝗺𝗽𝗹𝗮𝘁𝗲𝘀"
    assert(config_templates ~= nil)

    local config_file
    local config_string
    local is_success
    local config_data
    local return_config_data
    local msg_count
    local msg

    config_file = io.open(config2.config_dir .. "/" .. subfolder .. (subfolder ~= "" and "/" or "") .. config .. ".json", "r")
    if not config_file then
        config_string = ""
    else
        config_string = config_file:read("*all")
        assert(config_file:close())
    end

    if is_no_gui_init and config_string == "" then
        is_success, _, config_data = validate(config_no_gui(config_templates))
        assert(is_success == true)
    else
        if ui_func then
            config_data = config_gui3(config_string, validation_func_ui, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
            if config_data == false then return false end
            repeat
                is_success, return_config_data = ui_func(config_data)
                if return_config_data then config_data = return_config_data end
                if is_success == false then return false
                elseif is_success == "JSON" then
                    return_config_data = config_gui2(json:encode_pretty(config_data), validation_func_ui, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
                    if return_config_data then config_data = return_config_data end
                end
            until is_success == true
            assert(validation_func(config_data))
        else
            config_data = config_gui2(config_string, validation_func, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
            if config_data == false then return false end
    end end

    return config2.write_config(config, subfolder, config_data), config_data
end

validate = function(config_string, validation_func)
    local config_data
    local msg_count
    local msg

    config_data = json.decode2(config_string)
    if json.error then
        msg_count = json.error msg = json.error_table
    else
        msg_count, msg = validation_func(config_data)
        if msg_count == true then msg_count = 0 msg = {} end
    end
    return msg_count, msg, config_data
end
config_gui2 = function(config_string, validation_func, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
    local msg_count
    local msg
    local config_data

    msg_count, msg = validate(config_string, validation_func)
    repeat
        config_string = config_gui(config_string, msg_count, msg, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
        if config_string == false then return false end
        msg_count, msg, config_data = validate(config_string, validation_func)
    until msg_count == 0
    return config_data
end
config_gui3 = function(config_string, validation_func, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
    local msg_count
    local msg
    local config_data

    msg_count, msg, config_data = validate(config_string, validation_func)
    while msg_count ~= 0 do
        config_string = config_gui(config_string, msg_count, msg, word_name_b, word_config_b, word_template, word_templates_b, config_templates)
        if config_string == false then return false end
        msg_count, msg, config_data = validate(config_string, validation_func)
    end
    return config_data
end

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
    for k in pairs(config_templates) do if type(k) ~= "number" then table.insert(templates, k) end end
    if atemplate then template = atemplate.get_template_key(config_templates)
    else template = templates[1] end
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
            if atemplate then atemplate.select_template_key(template) end
end end end
------------------------------------------------
-- @param table config_templates: Templates for the config
-- 
-- @returns str config_string: The first template in the templates table
config_no_gui = function(config_templates) return config_templates[config_templates[1]] end

local functions = {}

functions.read_config = config2.read_config
functions.write_config = config2.write_config
functions.edit_config_gui = edit_config_gui

functions.json = json
functions.config_dir = config2.config_dir
functions.validate = validate
functions.config_gui2 = config_gui2
functions.config_gui3 = config_gui3
functions.config_gui = config_gui
if atemplate then
    functions.get_template_key = atemplate.get_template_key
    functions.select_template_key = atemplate.select_template_key
end

return functions
