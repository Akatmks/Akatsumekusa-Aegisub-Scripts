-- NN.CJCharacter
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

versioning.name = "NN.CJCharacter"
versioning.description = "Module NN.CJCharacter"
versioning.version = "0.1.8"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "NN.CJCharacter"

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl({
        name = versioning.name,
        description = versioning.description,
        version = versioning.version,
        author = versioning.author,
        moduleName = versioning.namespace,
        url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/dev/DependencyControl.json"
    })
end

local characters
local f
local at

f = assert(io.open("NN/CJCharacter/characters.ansi", "rb"))
characters = f:read("*all")
f:close()
at = function(idx) return string.sub(characters, idx, idx) end

local functions

functions.characters = characters
functions.at = at

functions.versioning = versioning

return functions
