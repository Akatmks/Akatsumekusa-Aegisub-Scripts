-- aka.config
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

------------------------------------------------------------------------------
-- Although this module is called aka.config, you can serialise anything you
-- want using this module, not only configs.
-- This module, compared to other serialisation modules like DepCtrl's
-- ConfigHandler, generates beautified JSON. Additionally, it also provides a
-- basic GUI so that the user may edit the JSON in Aegisub. The JSON editor
-- supports templates or presets.
--
-- If you for whatever reason are interested in using this module, tutorials
-- are available at „docs/Using aka.config.md“.
------------------------------------------------------------------------------

local versioning = {}

versioning.name = "aka.config"
versioning.description = "Module aka.config"
versioning.version = "0.1.21"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.config"

versioning.requireModules = "[{ \"moduleName\": \"aka.config2\" }, { \"moduleName\": \"aka.template\", \"optional\": True }]"

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
            { "aka.template", optional = true }
        }
    }):requireModules()
end

local config = require("aka.config.config")

local functions = {}

functions.versioning = versioning

functions.read_config = config.read_config
functions.write_config = config.write_config
functions.edit_config_gui = config.edit_config_gui

functions.json = config.json
functions.config_dir = config.config_dir
functions.validate = config.validate
functions.config_gui2 = config.config_gui2
functions.config_gui3 = config.config_gui3
functions.config_gui = config.config_gui
functions.get_template_key = config.get_template_key
functions.select_template_key = config.select_template_key

return functions
