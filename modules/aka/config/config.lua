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

local config = require("aka.config2")
local outcome = require("aka.outcome")
local ok, err, some, none, o = outcome.ok, outcome.err, outcome.some, outcome.none, outcome.o
local unicode = require("aka.unicode")
local re = require("aegisub.re")

local config_methods = {}
config_methods.__index = config

-------------------------------------------------
-- Create config GUI.
--
-- config itself is setmetatable to config2 so all the config2 functions will be able to used without initialising config GUI
-- 
-- @param table param:
--     display_name: The display name of your script / config
--     width [32]: The width for a column (two columns in total)
--     height [32]: The height of a column
--     presets: Every presets in a key-value table
--     default: THe name (key) of the default preset
-- 
-- @returns table: an instance of config with GUI functions
config.make_editor = function(param)
    local codepoint
    
    local self = setmetatable({}, config_methods)
    self.display_name = param.display_name
    self.display_name_b = ""
    for char in unicode.chars(param.display_name) do
        codepoint = unicode.codepoint(char)
        if 0x0041 <= char and char <= 0x005A then
            codepoint = codepoint + 0x1D593
        elseif 0x0061 <= char and char <= 0x007A then
            codepoint = codepoint + 0x1D58D
        end
        self.display_name_b = self.display_name_b .. unicode.char(codepoint)
    end
    self.width = param.width or 32
    self.height = param.height or 20
    self.presets = param.presets
    self.preset_names = {}
    for k, _ in pairs(param.presets) do
        table.insert(self.preset_names, k)
    end
    self.default = param.default
end

-------------------------------------------------
-- Edit config GUI.
--
-- This function will only return with valid JSON (before validation function) or the user click cancel
-- 
-- @param outcome.Option<string, string> config_string: config JSON
-- @param outcome.Option<string, string> error: Errors probably coming from validation function
-- 
-- @returns outcome.result<table, string>: Return the same config table back if success
config_methods.edit_config = function(self, config_string, error)
    local dialog
    local buttons
    local button_ids
    local button
    local result_table
    local config_text
    local preset_name
    local config_data

    config_text = config_string:unwrapOr("")
    preset_name = self.default
    while true do
        error = error
            :mapOr({}, function(error) return
                re.split(error, "\n") end)
        dialog = { { class = "label",                           x = 0, y = 0, width = self.width,
                                                                label = (config_string:isSome() and "𝗘𝗱𝗶𝘁" or "𝗖𝗿𝗲𝗮𝘁𝗲") .. " 𝗖𝗼𝗻𝗳𝗶𝗴 𝗳𝗼𝗿 " .. self.display_name_b .. ":" },
                   { class = "textbox", name = "config_text",   x = 0, y = 1, width = self.width, height = self.height - 1,
                                                                text = config_text },
                   { class = "label",                           x = self.width, y = #error > 0 and #error + 1 or 0, width = self.width,
                                                                label = "𝗣𝗿𝗲𝘀𝗲𝘁:" },
                   { class = "textbox", name = "preset_text",   x = self.width, y = 1 + (#error > 0 and #error + 1 or 0), width = self.width, height = self.height - 2 - (#error > 0 and #error + 1 or 0),
                                                                text = self.presets[preset_name] },
                   { class = "label",                           x = self.width, y = self.height - 1, width = 8,
                                                                label = "Select Preset:" },
                   { class = "dropdown", name = "preset",       x = self.width + 8, y = self.height - 1, width = 24,
                                                                items = self.preset_names, value = preset_name } }
        if #error > 0 then
            table.insert(dialog, { class = "label",             x = self.width, y = 0, width = self.width,
                                                                label = "𝗘𝗿𝗿𝗼𝗿 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱:" })
            for i, v in ipairs(error) do
                table.insert(dialog, { class = "label",         x = self.width, y = i, width = self.width,
                                                                label = v })
        end end
        buttons = { "&Apply", "&Beautify", "&View Preset", "Diminish" }
        button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Diminish", no = "Diminish", cancel = "Diminish" }

        button, result_table = aegisub.dialog.display(dialog, buttons, button_ids)

        if button == false or button == "Diminish" then return false
        elseif button == "&Apply" then
            config_text = result_table["config_text"]

            self.json:decode2(config_text)
            if self.json.error:isNone() then
                return ok(config_text)
            else
                error = self.json.error
            end
        elseif button == "&Beautify" then
            config_text = result_table["config_text"]

            config_data = self.json:decode2(config_text)
            if self.json.error:isNone() then
                config_text = self.json:encode_pretty(config_data)
            else
                error = self.json.error
            end
        elseif button == "View &Preset" then
            config_text = result_table["config_text"]
            preset_name = result_table["preset"]
        elseif button == "Diminish" then
            return err()
end end end

-------------------------------------------------
-- Read, edit and validate and then save config.
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- @param function validation_func: The validation function that takes the config_data and returns either ok(config_data) or err(error_message)
-- 
-- @returns outcome.result<table, string>: Return the config table back if success, or return err() if the user cancel the option
--
-- @aegisub.debug.out: This will print message to aegisub.debug.out and return ok(config_data) if the save process failed
config_methods.read_edit_validate_and_save_config = function(self, config, config_supp, validation_func)
    local config_string
    local error
    local config_data
    
    if type(config_supp) ~= "string" then validation_func = config_supp config_supp = config config = nil end
    
    config_string = self.read_config_string(config, config_supp)
    error = config_string
        :andThen(function(config_string) return
            self.json:decode3(config_string) end)
        :andThen(validation_func)
        :errOption()
    config_string = config_string
        :okOption()

    while true do
        config_string = self:edit_config(config_string, error)
            :mapErr(function() return
                err("[aka.config] Operation cancelled by user") end)
        config_data = config_string
            :andThen(function(config_string) return
                self.json:decode3(config_string) end)
        error = config_data
            :andThen(validation_func)
            :errOption()
        
        if error:isNone() then
            self.write_config_string(config, config_supp, config_string)
                :mapErr(function(config_string) return
                    aegisub.debug.out(1, error) end)
            return ok(config_data)
end end end

-------------------------------------------------
-- Read and validate config. If anything happens, edit, validate and save config
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- @param function validation_func: The validation function that takes the config_data and returns either ok(config_data) or err(error_message)
-- 
-- @returns outcome.result<table, string>: Return the config table back if success, or return err() if the user cancel the option
--
-- @aegisub.debug.out: This will print message to aegisub.debug.out and return ok(config_data) if the save process failed
config_methods.read_and_validate_config_or_else_edit_and_save = function(self, config, config_supp, validation_func)
    local config_string
    local error
    local config_data
    
    if type(config_supp) ~= "string" then validation_func = config_supp config_supp = config config = nil end
    
    config_string = self.read_config_string(config, config_supp)
    while true do
        config_data = config_string
            :andThen(function(config_string) return
                self.json:decode3(config_string) end)
        error = config_data
            :andThen(validation_func)
            :errOption()
        
        if error:isNone() then
            self.write_config_string(config, config_supp, config_string)
                :mapErr(function(config_string) return
                    aegisub.debug.out(1, error) end)
            return ok(config_data)
        end
        
        config_string = self:edit_config(config_string, error)
            :mapErr(function() return
                err("[aka.config] Operation cancelled by user") end)
end end

-------------------------------------------------
-- Read and validate config. If it is empty, save and return the default config happens; Or else edit, validate and save config
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- @param function validation_func: The validation function that takes the config_data and returns either ok(config_data) or err(error_message)
-- 
-- @returns outcome.result<table, string>: Return the config table back if success, or return err() if the user cancel the option
--
-- @aegisub.debug.out: This will print message to aegisub.debug.out and return ok(config_data) if the save process failed
config_methods.read_and_validate_config_if_empty_then_default_or_else_edit_and_save = function(self, config, config_supp, validation_func)
    local config_string
    local error
    local config_data
    
    local config_string
    local error
    local config_data
    
    if type(config_supp) ~= "string" then validation_func = config_supp config_supp = config config = nil end
    
    config_string = self.read_config_string(config, config_supp)
    if config_string:isErr() then
        self.write_config_string(config, config_supp, self.presets[self.default])
            :mapErr(function(config_string) return
                aegisub.debug.out(1, error) end)
        return self.json:decode3(self.presets[self.default])
    end
    while true do
        config_data = config_string
            :andThen(function(config_string) return
                self.json:decode3(config_string) end)
        error = config_data
            :andThen(validation_func)
            :errOption()
        
        if error:isNone() then
            self.write_config_string(config, config_supp, config_string)
                :mapErr(function(config_string) return
                    aegisub.debug.out(1, error) end)
            return ok(config_data)
        end
        
        config_string = self:edit_config(config_string, error)
            :mapErr(function() return
                err("[aka.config] Operation cancelled by user") end)
end end

return config
