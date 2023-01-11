-- aka.Cycles.lua
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

versioning.name = "aka.Cycles"
versioning.description = "Macro aka.Cycles"
versioning.version = "0.1.3"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.Cycles"

versioning.requireModules = "[{ \"moduleName\": \"a-mo.LineCollection\", \"feed\": \"https://raw.githubusercontent.com/TypesettingTools/Aegisub-Motion/DepCtrl/DependencyControl.json\" }, { \"moduleName\": \"l0.ASSFoundation\", \"feed\": \"https://raw.githubusercontent.com/TypesettingTools/ASSFoundation/master/DependencyControl.json\" }, { \"moduleName\": \"aka.config\" }, { \"moduleName\": \"aka.template\" }]"

script_name = versioning.name
script_description = versioning.description
script_version = versioning.version
script_author = versioning.author
script_namespace = versioning.namespace

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
            { "a-mo.LineCollection" },
            { "l0.ASSFoundation" },
            { "aka.config" },
            { "aka.template" }
        }
    }):requireModules()
end
local LineCollection = require("a-mo.LineCollection")
local ASS = require("l0.ASSFoundation")
local config = require("aka.config")
