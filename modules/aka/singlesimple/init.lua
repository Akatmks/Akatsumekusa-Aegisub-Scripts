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
versioning.version = "1.0.13"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.singlesimple"

versioning.requiredModules = "[{ \"moduleName\": \"aka.config2\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"aka.effil\" }]"

local version = require("l0.DependencyControl")({
    name = versioning.name,
    description = versioning.description,
    version = versioning.version,
    author = versioning.author,
    moduleName = versioning.namespace,
    url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
    feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "aka.config2" },
        { "aka.outcome" },
        { "aka.effil" }
    }
})
version:requireModules()

local aconfig = require("aka.config2")
local outcome = require("aka.outcome")
local ok, err = outcome.ok, outcome.err
local effil = require("aka.effil").effil()

local make_config

-------------------------------------------------
-- Create the config
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- @param table possible_values: A table for all the possible values for the config
-- @param anytype or function default_value: The default value for the config or a function as value provider
-- 
-- @return table Config: A initialised config object with Config.value and Config.setValue
make_config = function(config, config_supp, possible_values, default_value)
    if type(config_supp) == "table" or
       default_value == nil then
        default_value = possible_values possible_values = config_supp config_supp = config config = nil
    end

    local Config = {}
    Config.__index = Config
    
    Config.value = function(self)
        if self._time ~= os.time() then
            self._value = aconfig.read_config(config, config_supp)
                :andThen(function(config)
                    for _, v in ipairs(possible_values) do
                        if config[1] == v then return
                            ok(config[1])
                    end end return
                    err("[aka.singlesimple] Error") end)
                :ifErr(function()
                    effil.sleep(20, "ms") end)
                :orElseOther(function() return
                    aconfig.read_config(config, config_supp)
                        :andThen(function(config)
                            for _, v in ipairs(possible_values) do
                                if config[1] == v then return
                                    ok(config[1])
                            end end return
                            err("[aka.singlesimple] Error") end) end)
                :orElseOther(function()
                    if type(default_value) == "function" then default_value = default_value() end
                    for _, v in ipairs(possible_values) do
                        if default_value == v then
                            aconfig.write_config(config, config_supp, { default_value })
                                :ifErr(function(err)
                                    aegisub.debug.out(1, "[aka.singlesimple] Failed to save value to file\n" .. err .. "\n") end) return
                            ok(default_value)
                    end end
                    error("[aka.singlesimple] default_value not found in possible_values") end)
                :unwrap()
            self._time = os.time()
        end
        return self._value
    end
    Config.setValue2 = function(self, value)
        return
        ok(value):andThen(function(value)
            for _, v in ipairs(possible_values) do
                if value == v then
                    self._value = value
                    self._time = os.time() return
                    ok(value)
            end end return
            err("[aka.singlesimple] Value not found in possible_values") end)
        :ifOk(function(value)
            aconfig.write_config(config, config_supp, { value })
                :ifErr(function(err)
                    aegisub.debug.out(1, "[aka.singlesimple] Failed to save value to file\n" .. err .. "\n") end) end)
    end
    Config.setValue = function(self, value)
        self:setValue2(value)
            :ifErr(function(err)
                aegisub.debug.out(0, err .. "\n")
                aegisub.cancel() end)
    end

    local self = setmetatable({}, Config)

    self:value()

    return self
end

local functions = {}

functions.make_config = make_config

functions.version = version
functions.versioning = versioning

return version:register(functions)
