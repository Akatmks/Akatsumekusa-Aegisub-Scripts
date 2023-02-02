-- aka.optimising
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

versioning.name = "aka.optimising"
versioning.description = "Module aka.optimising"
versioning.version = "0.1.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.optimising"

versioning.requireModules = "[{ \"moduleName\": \"aka.singlesimple\" }, { \"moduleName\": \"ffi\" }]"

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
            { "aka.singlesimple" },
            { "ffi" }
        }
    }):requireModules()
end

local clock = require("aka.optimising.time")
local ssconfig = require("aka.singlesimple").make_config("aka.optimising", { true, false }, false)

local start
local lap
local time

start = function()
    if jit.os ~= "Windows" then
        aegisub.debug.out(3, "[aka.optimising] aka.optimising is only supported on Windows.\n")
        aegisub.debug.out(3, "[aka.optimising] Please turn aka.optimising config to false in order to avoid this error.\n")
        aegisub.cancel()
    end
    if ssconfig:value() then
        time = clock.time()
        aegisub.debug.out(3, "[aka.optimising][" .. string.format("%.6f", 0) .. "] Start aka.optimising\n")
end end
lap = function(lap_name)
    if ssconfig:value() then
        aegisub.debug.out(3, "[aka.optimising][" .. string.format("%.6f", clock.time() - time) .. "] " .. tostring(lap_name) .. "\n")
end end

local functions = {}

functions.versioning = versioning

functions.start = start
functions.lap = lap

functions.time = time
functions.ssconfig = ssconfig

return functions
