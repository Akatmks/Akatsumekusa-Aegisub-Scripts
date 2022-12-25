-- aka.config2
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

versioning.name = "aka.config2"
versioning.description = "Module aka.config2"
versioning.version = "0.1.10"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.config2"

-- local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
-- if hasDepCtrl then
--     DepCtrl({
--         name = versioning.name,
--         description = versioning.description,
--         version = versioning.version,
--         author = versioning.author,
--         moduleName = versioning.namespace,
--         url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
--         feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/dev/DependencyControl.json",
--         {
--             { "aegisub.re" },
--             { "aegisub.unicode" },
--             { "lfs" }
--         }
--     }):requireModules()
-- end

local config2 = require("aka.config2.config2")

local functions = {}

functions.versioning = versioning

functions.read_config = config2.read_config
functions.write_config = config2.write_config

functions.json = config2.json
functions.config_dir = config2.config_dir

return functions
