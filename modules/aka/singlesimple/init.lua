-- aka.singlesimple
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

local versioning = {}

versioning.name = "aka.singlesimple"
versioning.description = "Module aka.singlesimple"
versioning.version = "0.1.2"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.singlesimple"

versioning.requireModules = "[{ \"moduleName\": \"aka.config2\" }]"

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl({
        name = versioning.name,
        description = versioning.description,
        version = versioning.version,
        author = versioning.author,
        moduleName = versioning.namespace,
        url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/dev/DependencyControl.json",
        {
            { "aka.config2" }
        }
    }):requireModules()
end

local aconfig = require("aka.config2")

local make_config

-------------------------------------------------
-- Create the config
-- 
-- @param str config: The name for the config file without the file extension
-- @param str subfolder: The subfolder where the config is in
--                       This parameter is optional. Omit in place if not needed
-- @param table possible_values: All the possible values for the config
-- @param table default_value: The default value for the config
-- 
-- @returns table Config: A initialised config object with Config.value and Config.setValue
make_config = function(...)
    local arg = table.pack(...)

    local config
    local subfolder
    local possible_values
    local default_value
    assert(type(arg[1]) == "string") config = arg[1]
    if #arg >= 4 and type(arg[2]) == "string" then
        subfolder = arg[2]
        assert(type(arg[3]) == "table") possible_values = arg[3]
        default_value = arg[4]
    else
        possible_values = arg[2]
        default_value = arg[3]
    end

    local Config
    local validation_func

    Config = {}
    Config.__index = Config
    
    validation_func = function(config_data)
        for _, value in ipairs(possible_values) do
            if config_data[1] == value then
                return true
        end end
        return false
    end

    setmetatable(Config, { __call = function(cls) return cls.new() end })
    Config.new = function()
        local self = setmetatable({}, Config)
    
        local is_success
        local config_data
    
        is_success, config_data = aconfig.read_config(config, subfolder, validation_func)
        if is_success then self._value = config_data[1]
        else self._value = default_value aconfig.write_config(config, subfolder, { self._value }) end
    
        return self
    end
    
    Config.value = function(self)
        return self._value
    end
    Config.setValue = function(self, value)
        local config_data
    
        config_data = { value }
        assert(validation_func(config_data))
        self._value = value aconfig.write_config(config, subfolder, config_data)
    end

    return Config()
end

local functions = {}

functions.versioning = versioning

functions.make_config = make_config

return functions
