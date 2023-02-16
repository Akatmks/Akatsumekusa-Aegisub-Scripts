-- NN.CJSpacing
-- Copyright (c) Akatsumekusa and contributors

------------------------------------------------------------------------------
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
-- 
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.
------------------------------------------------------------------------------

local versioning = {}

versioning.name = "NN.CJSpacing"
versioning.description = "Module NN.CJSpacing"
versioning.version = "0.1.5"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "NN.CJSpacing"

versioning.requireModules = "[{ \"moduleName\": \"NN.CJCharacter\" }, { \"moduleName\": \"aegisub.unicode\" }]"

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
            { "NN.CJCharacter" },
            { "aegisub.unicode" }
        }
    }):requireModules()
end
local characters = require("NN.CJCharacter")
local unicode = require("aegisub.unicode")

function()
    type = characters.at(unicode.codepoint(something))
end
