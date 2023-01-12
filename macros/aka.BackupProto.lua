-- aka.BackupProto.lua
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

versioning.name = "BackupProto"
versioning.description = "Macro BackupProto"
versioning.version = "0.1.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.BackupProto"

versioning.requireModules = "[{ \"moduleName\": \"aka.actor\" }]"

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
            { "aka.actor" }
        }
    })
    DepCtrl:requireModules()
end
local aactor = require("aka.actor")

local Backup
local backup
local select

Backup = function(sub, sel, act)
    local i
    local j

    j = #sel repeat
        i = 1 repeat
            if j - i == sel[j] - sel[i] then
                sel, act = backup(sub, sel, act, sel[i], sel[j])
                j = i - 1
                break
            else i = i + 1 end
        until false
    until j == 0
    
    return sel, act
end
backup = function(sub, sel, act, i, j)
    local k
    local line

    for _ = i, j do
        line = sub[j]
        aactor.onemoreFlag(line, "backup")
        line.comment = true
        sub[-i] = line
    end

    for k in ipairs(sel) do sel[k] = select(sel[k], i, j) end
    act = select(act, i, j)
    return sel, act
end
select = function(selected, i, j)
    if selected < i then return selected
    else return selected + j - i + 1 end
end

if hasDepCtrl then
    DepCtrl:registerMacros({
        { "Backup", "Backup selected lines", Backup }
    })
else
    aegisub.register_macro("BackupProto/Backup", "Backup selected lines", Backup)
end
