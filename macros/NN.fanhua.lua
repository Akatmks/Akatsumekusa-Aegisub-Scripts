-- NN.Fanhua.lua
-- Copyright (c) Akatsumekusa

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

versioning.name = "NN.fanhua"
versioning.description = "Macro NN.fanhua"
versioning.version = "0.1.2"
versioning.author = "Akatsumekusa"
versioning.namespace = "NN.fanhua"

versioning.requireModules = "[{ \"moduleName\": \"aka.luajit-request\" }, { \"moduleName\": \"aka.config\" }, { \"moduleName\": \"aka.template\" }]"

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
            { "aka.luajit-request" },
            { "aka.config" },
            { "aka.template" }
        }
    }):requireModules()
end
local request = require("aka.luajit-request")
local config = require("aka.config")
