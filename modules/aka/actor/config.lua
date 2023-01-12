-- aka.actor
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

local aconfig = require("aka.config2")

local validation_func

validation_func = function(config_data)
    -- The only three string fields in https://github.com/arch1t3cht/Aegisub/blob/8c387cb63bf941eeaf30c6c5c849ced5604e786d/src/auto4_lua_assfile.cpp#L288
    return type(config_data[1]) == "string" and
           (config_data[1] == "actor" or
            config_data[1] == "effect" or
            config_data[1] == "style")
end

local Config = {}
Config.__index = Config

setmetatable(Config, { __call = function(cls) return cls.new() end })
Config.new = function()
    local self = setmetatable({}, Config)

    local is_success
    local config_data

    is_success, config_data = aconfig.read_config("aka.actor", validation_func)
    if is_success then self._field = config_data[1]
    else self._field = "actor" aconfig.write_config("aka.actor", { self._field }) end

    return self
end

Config.field = function(self)
    return self._field
end
Config.setField = function(self, field)
    local config_data

    config_data = { field }
    assert(validation_func(config_data))
    self._field = field aconfig.write_config("aka.actor", config_data)
end

return Config()
