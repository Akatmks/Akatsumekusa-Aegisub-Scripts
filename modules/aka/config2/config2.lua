-- aka.config2
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

local json = require("aka.config2.json")
local re = require("aegisub.re")
local unicode = require("aegisub.unicode")
local lfs = require("lfs")
local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")

local config_dir
local read_config
local write_config

json.error = false
json.error_table = {}
json.onDecodeError = function(message, text, location, etc)
    local matches
    local i

    if not text or not location or not etc then return end
    if json.error == false then json.error = 1
    else json.error = json.error + 1 end

    location = "\n" .. location .. "\n"
    etc = etc + 1
    matches = re.find(location, "(\\r|\\n|\\r\\n)")
    i = 1
    while matches[i + 1] do
        if etc == 2 then
            table.insert(json.error_table, text)
            return
        elseif etc > matches[i]["last"] and etc <= matches[i + 1]["first"] then
            table.insert(json.error_table, text .. " in line " .. tostring(i) .. " column " .. tostring(unicode.len(string.sub(location, matches[i]["last"] + 1, etc - 1)) + 1))
            json.error = json.error + 1
            table.insert(json.error_table, "`" .. string.sub(location, matches[i]["last"] + 1, matches[i + 1]["first"] - 1) .. "`")
            return
        end
        i = i + 1
    end
    assert(false)
end
json.reset_error = function() json.error = false json.error_table = {} end
json.decode2 = function(text, etc, options) json.reset_error() return json:decode(text, etc, options) end

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
read_config = function(config, subfolder, validation_func)
    assert(config ~= nil)
    subfolder = subfolder or ""
    validation_func = validation_func or function() return true end

    local config_file
    local config_data

    config_file = io.open(config_dir .. "/" .. subfolder .. (subfolder ~= "" and "/" or "") .. config .. ".json", "r")
    if config_file then
        config_data = json.decode2(config_file:read("*all"))
        assert(config_file:close())
        if not json.error and validation_func(config_data) == true then
            return true, config_data
    end end
    return false, config_data
end
-------------------------------------------------
-- Overwrite the specified config with the table.
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder [""]: The subfolder where the config is in;
--                               Set this to "" if the config are in the root config directory
-- @param table config_data: The table to save to the config
-- 
-- @returns bool is_success: True if the config was successfully saved
write_config = function(config, subfolder, config_data)
    assert(config ~= nil)
    subfolder = subfolder or ""
    assert(config_data ~= nil)

    local config_directory
    local config_file
    local is_success, err, code
    
    config_directory = config_dir .. (subfolder ~= "" and "/" or "") .. subfolder
    if lfs.attributes(config_directory, "mode") == nil then
        lfs.mkdir(config_directory)
    end

    config_file = assert(io.open(config_directory .. "/" .. config .. ".json", "w"))
    config_file:write(json:encode_pretty(config_data))
    assert(config_file:close())
    return true
end

local functions = {}

functions.read_config = read_config
functions.write_config = write_config

functions.json = json
functions.config_dir = config_dir

return functions
