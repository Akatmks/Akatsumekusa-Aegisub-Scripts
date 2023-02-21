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
local outcome = require("aka.outcome")
local ok, err, o = outcome.ok, outcome.err, outcome.o
local re = require("aegisub.re")
local unicode = require("aegisub.unicode")
local lfs = require("lfs")
local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")

local config_dir
local read_config
local write_config

json.error = nil
json.onDecodeError = function(message, text, location, etc)
    local matches
    local i

    if not text or not location or not etc then return end

    location = "\n" .. location .. "\n"
    etc = etc + 1
    matches = re.find(location, "(\\r|\\n|\\r\\n)")
    i = 1
    while matches[i + 1] do
        if etc == 2 then
            if not json.error then json.error =     text
            else json.error = json.error .. "\n" .. text end
            return
        elseif etc > matches[i]["last"] and etc <= matches[i + 1]["first"] then
            if not json.error then json.error =     text .. " in line " .. tostring(i) .. " column " .. tostring(unicode.len(string.sub(location, matches[i]["last"] + 1, etc - 1)) + 1) .. "\n" ..
                                                    "`" .. string.sub(location, matches[i]["last"] + 1, matches[i + 1]["first"] - 1) .. "`"
            else json.error = json.error .. "\n" .. text .. " in line " .. tostring(i) .. " column " .. tostring(unicode.len(string.sub(location, matches[i]["last"] + 1, etc - 1)) + 1) .. "\n" ..
                                                    "`" .. string.sub(location, matches[i]["last"] + 1, matches[i + 1]["first"] - 1) .. "`" end
            return
        end
        i = i + 1
    end
    assert(false)
end
json.reset_error = function() json.error = nil end
json.decode2 = function(text, etc, options) json.reset_error() return json:decode(text, etc, options) end

config_dir = aegisub.decode_path(hasDepCtrl and DepCtrl.config.c.configDir or "?user/config")

------------------------------------------------
-- Read the specified config and return a table.
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- 
-- @returns outcome.result<table, string>
read_config = function(config, config_supp) return
    o(io.open(config_dir .. "/" .. (config and config .. "/" or "") .. config_supp .. ".json", "r"))
        :andThen(function(file)
            local config_data = json.decode2(file:read("*all"))
            file:close()
            if not json.error then return
                ok(config_data)
            else return
                err(json.error)
            end end)
end

-------------------------------------------------
-- Overwrite the specified config with the table.
--
-- Optional arguments can be omitted in place as write_config(config, config_data)
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- @param table config_data: The table to save to the config
-- 
-- @returns bool is_success: True if the config was successfully saved
write_config = function(config, config_supp, config_data)
    if type(config_supp) == "table" then config_data = config_supp config_supp = config config = nil end

    return
    o(lfs.attributes(config_dir .. (config and "/" .. config or ""), "mode"))
        :orElseOther(function(_) return
            o(lfs.mkdir(config_dir .. (config and "/" .. config or ""))) end)
        :andThen(function(_) return
            o(io.open(config_dir .. (config and "/" .. config or "") .. "/" .. config_supp .. ".json", "w")) end)
        :andThen(function(file)
            file:write(json:encode_pretty(config_data))
            file:close()
            if not json.error then return
                ok(config_data)
            else return
                err(json.error)
            end end)
end

local functions = {}

functions.read_config = read_config
functions.write_config = write_config

functions.json = json
functions.config_dir = config_dir

return functions
