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
versioning.version = "0.1.8"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.singlesimple"

versioning.requireModules = "[{ \"moduleName\": \"aka.config2\" }, { \"moduleName\": \"aka.outcome\" }]"

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
            { "aka.config2" },
            { "aka.outcome" }
        }
    }):requireModules()
end

local aconfig = require("aka.config2")
local outcome = require("aka.outcome")
local ok, err, o = outcome.ok, outcome.err, outcome.o

local make_config

-------------------------------------------------
-- Create the config
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- @param table possible_values: All the possible values for the config
-- @param table default_value: The default value for the config
-- 
-- @returns table Config: A initialised config object with Config.value and Config.setValue
make_config = function(config, config_supp, possible_values, default_value)
    if type(config_supp) == "table" then default_value = possible_values possible_values = config_supp config_supp = config config = nil end

    local Config = {}
    Config.__index = Config
    
    Config.value = function(self)
        return self._value
    end
    Config.setValue2 = function(self, value)
        self._value = value
        return aconfig.write_config(config, config_supp, { value })
    end
    Config.setValue = function(self, value)
        self:setValue2(value)
            :ifErr(function(err)
                aegisub.debug.out(1, "[aka.singlesimple] Failed to save the value to file\n" .. err) end)
    end

    local self = setmetatable({}, Config)

    self._value = aconfig.read_config(config, config_supp)
        :andThen(function(config)
            for _, v in ipairs(possible_values) do
                if config[1] == possible_values then
                    return ok(config[1])
            end end
            return err("[aka.singlesimple] Error") end)
        :orElseOther(function()
            aconfig.write_config(config, config_supp, { default_value })
            return ok(default_value) end)
        :unwrap()

    return self
end

local functions = {}

functions.versioning = versioning

functions.make_config = make_config

return functions
