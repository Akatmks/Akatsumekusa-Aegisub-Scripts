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
versioning.version = "1.0.4"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.singlesimple"

versioning.requireModules = "[{ \"moduleName\": \"aka.config2\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"aka.mmapfile\" }, { \"moduleName\": \"aka.effil\" }, { \"moduleName\": \"ffi\" }]"

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl({
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
            { "aka.mmapfile" },
            { "aka.effil" },
            { "ffi" }
        }
    }):requireModules()
end

local aconfig = require("aka.config2")
local outcome = require("aka.outcome")
local ok, err, pcall_ = outcome.ok, outcome.err, outcome.pcall
local mmapfile = require("aka.mmapfile")
local effil = require("aka.effil")
local ffi = require("ffi")

ffi.cdef[[
struct config { size_t idx; };
]]

local pid
if jit.os == "Windows" then
    ffi.cdef[[
uint32_t GetCurrentProcessId();
    ]]
    pid = tonumber(ffi.C.GetCurrentProcessId())
else
    ffi.cdef[[
int32_t getpid();
    ]]
    pid = tonumber(ffi.C.getpid())
end

local make_config

-------------------------------------------------
-- Create the config
-- 
-- @param str config [nil]: The subfolder where the config is in
-- @param str config_supp: The name for the config file without the file extension
-- @param table possible_values: A table for all the possible values for the config
-- @param anytype or function default_value: The default value for the config or a function as value provider
-- 
-- @returns table Config: A initialised config object with Config.value and Config.setValue
make_config = function(config, config_supp, possible_values, default_value)
    local try

    if type(config_supp) == "table" or
       default_value == nil then
        default_value = possible_values possible_values = config_supp config_supp = config config = nil
    end

    local Config = {}
    Config.__index = Config
    
    Config.value2 = function(self) return
        pcall_(mmapfile.open, self._filename, "struct config")
            :andThen(function(ptr)
                local idx = tonumber(ptr.idx)
                mmapfile.close(ptr) return
                ok(idx) end)
            :andThen(function(idx) return
                ok(possible_values[idx]) end)
    end
    Config.value = function(self) return
        self:value2()
            :ifErr(function(err)
                aegisub.debug.out(err)
                aegisub.cancel() end)
            :unwrap()
    end
    Config.setValue2 = function(self, value)
        local idx

        for i, v in ipairs(possible_values) do
            if value == v then
                idx = i
                break
        end end
        if not idx then
            return err("[aka.singlesimple] Invalid value")
        end
        return
        pcall_(mmapfile.open, self._filename, "struct config", "rw")
            :andThen(function(ptr)
                ptr.idx = idx
                mmapfile.close(ptr) return
                ok() end)
            :andThen(function() return
                aconfig.write_config(config, config_supp, { value }) end)
    end
    Config.setValue = function(self, value)
        self:setValue2(value)
            :ifErr(function(err)
                aegisub.debug.out(1, err) end)
    end

    local self = setmetatable({}, Config)

    self._filename = "aka.singlesimple." .. (config and config .. "." or "") .. config_supp .. "." .. tostring(pid)

    try = function()
        return pcall_(mmapfile.open, self._filename, "struct config")
            :andThen(function(ptr)
                mmapfile.close(ptr) return
                ok() end)
            :orElseOther(function(_) return
                aconfig.read_config(config, config_supp)
                    :andThen(function(config)
                        for i, v in ipairs(possible_values) do
                            if config[1] == v then return
                                ok(i)
                        end end return
                        err("[aka.singlesimple] Invalid config") end)
                    :orElseOther(function()
                        if type(default_value) == "function" then
                            default_value = default_value()
                        end
                        for i, v in ipairs(possible_values) do
                            if default_value == v then return
                                aconfig.write_config(config, config_supp, { v })
                                    :andThen(function() return
                                        ok(i) end)
                        end end
                        error("[aka.singlesimple] Invalid default value") end)
                    :andThen(function(i) return
                        pcall_(mmapfile.gccreate, self._filename, 1, "struct config")
                            :andThen(function(ptr)
                                ptr.idx = i
                                mmapfile.close(ptr) return
                                ok(ptr) end) end) end)
    end

    self._ptr_no_gc = try()
        :orElseOther(function()
            effil.sleep(50, "ms") return
            try() end)
        :unwrap()

    return self
end

local functions = {}

functions.versioning = versioning

functions.make_config = make_config

return functions
