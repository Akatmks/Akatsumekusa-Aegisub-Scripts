-- NN.switchst
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

versioning.name = "Switch CHS and CHT"
versioning.description = "Comment and uncomment all the CHS and CHT lines in the subtitle"
versioning.version = "0.1.2"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "NN.switchst"

versioning.requireModules = "[{ \"moduleName\": \"aka.actor\" }, { \"moduleName\": \"aegisub.re\" }]"

script_name = versioning.name
script_description = versioning.description
script_version = versioning.version
script_author = versioning.author
script_namespace = versioning.namespace

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl = DepCtrl({
        name = versioning.name,
        description = versioning.description,
        version = versioning.version,
        author = versioning.author,
        moduleName = versioning.namespace,
        url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/dev/DependencyControl.json",
        {
            { "aka.actor" },
            { "aegisub.re" }
        }
    })
    DepCtrl:requireModules()
end
local aactor = require("aka.actor")
local re = require("aegisub.re")

local SwitchST

local Field

SwitchST = function(sub)
    local i
    local line
    local target

    for i = 1, #sub do
        line = sub[i]
        if line.class == "dialogue" then
            if not target then
                if aactor.flag(line, "chs") then
                    if line.comment then target = "chs"
                    else target = "cht" end
                elseif aactor.flag(line, "cht") then
                    if line.comment then target = "cht"
                    else target = "chs" end
            end end

            if target == "chs" and aactor.flag(line, "chs") or
               target == "cht" and aactor.flag(line, "cht") then
                if line.comment == true then
                    line.comment = false
                    sub[i] = line
                end
            elseif target == "chs" and aactor.flag(line, "cht") or
                   target == "cht" and aactor.flag(line, "chs") then
                if line.comment == false then
                    line.comment = true
                    sub[i] = line
end end end end end

Field = function()
    local dialog
    local buttons
    local button_ids
    local button
    local result_table

    dialog = { { class = "label",                           x = 0, y = 0, width = 24,
                                                            label = "Select the field for chs and cht flag" },
               { class = "label",                           x = 1, y = 1, width = 5,
                                                            label = "Field: " },
               { class = "dropdown", name = "field",        x = 6, y = 1, width = 6,
                                                            items = { "Actor", "Effect", "Style" }, value = re.sub(aactor.field:field(), "^\\w", string.upper) },
               { class = "label",                           x = 0, y = 2, width = 24,
                                                            label = "This setting will apply to all Akatsumekusa's scripts." } }
    buttons = { "&Apply", "Figurative" }
    button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Figurative", no = "Figurative", cancel = "Figurative" }

    button, result_table = aegisub.dialog.display(dialog, buttons, button_ids)

    if button == false or button == "Figurative" then aegisub.cancel()
    elseif button == "&Apply" then
        aactor.field:setField(string.lower(result_table["field"]))
end end

if hasDepCtrl then
    DepCtrl:registerMacros({
        { "Switch CHS and CHT", "Comment and uncomment all the CHS and CHT lines in the subtitle", SwitchST },
        { "Edit settings", "Edit field settings", Field }
    })
else
    aegisub.register_macro("BackupProto/Switch CHS and CHT", "Comment and uncomment all the CHS and CHT lines in the subtitle", SwitchST)
    aegisub.register_macro("BackupProto/Edit settings", "Edit field settings", Field)
end
