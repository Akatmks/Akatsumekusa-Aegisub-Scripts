-- aka.BackupSelection
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

versioning.name = "BackupSelection"
versioning.description = "Backup selected lines"
versioning.version = "1.0.13"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.BackupSelection"

versioning.requiredModules = "[{ \"moduleName\": \"aka.actor\" }, { \"moduleName\": \"aegisub.re\" }, { \"moduleName\": \"aka.optimising\", \"optional\": True }]"

script_name = versioning.name
script_description = versioning.description
script_version = versioning.version
script_author = versioning.author
script_namespace = versioning.namespace

DepCtrl = require("l0.DependencyControl")({
    name = versioning.name,
    description = versioning.description,
    version = versioning.version,
    author = versioning.author,
    moduleName = versioning.namespace,
    url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
    feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "aka.actor" },
        { "aegisub.re" },
        { "aka.optimising", optional = true }
    }
})
local aactor, re, optimising = DepCtrl:requireModules()

local Backup
local backup
local select

local Field

Backup = function(sub, sel, act)
    local i
    local j
    
    if optimising then optimising.start() end

    j = #sel repeat
        i = 1 repeat
            if j - i == sel[j] - sel[i] then
                if optimising then optimising.lap("Backup line " .. tostring(i) .. " to " .. tostring(j)) end
                
                sel, act = backup(sub, sel, act, sel[i], sel[j])
                j = i - 1
                break
            else i = i + 1 end
        until false
    until j == 0
    
    if optimising then optimising.lap("Backup finished") end
    return sel, act
end
backup = function(sub, sel, act, i, j)
    local k
    local line

    for _ = i, j do
        line = sub[j]

        -- The logic is quite weird. Think it like this:
        -- Why would you want to make a backup of a backup?
        -- It's because you want to use the new copy of the backup to do something new.
        -- That's why it will automatically uncomment the new lines for you to use.
        if aactor.flag(line, "backup-c") then
            line.comment = true
            sub[-i] = line

            aactor.clearFlag(line, "backup")
            aactor.clearFlag(line, "backup-c")
            sub[j + 1] = line
        elseif aactor.flag(line, "backup") then
            line.comment = true
            sub[-i] = line

            aactor.clearFlag(line, "backup")
            line.comment = false
            sub[j + 1] = line

        else
            if line.comment ~= true then
                aactor.setFlag(line, "backup")
                line.comment = true
            else aactor.setFlag(line, "backup-c") end
            sub[-i] = line
    end end

    for k in ipairs(sel) do sel[k] = select(sel[k], i, j) end
    act = select(act, i, j)
    return sel, act
end
select = function(selected, i, j)
    if selected < i then return selected
    else return selected + j - i + 1 end
end

Field = function()
    local dialog
    local buttons
    local button_ids
    local button
    local result_table

    dialog = { { class = "label",                           x = 0, y = 0, width = 24,
                                                            label = "Select the field " .. versioning.name .. " is going to put backup flag in" },
               { class = "label",                           x = 1, y = 1, width = 5,
                                                            label = "Field: " },
               { class = "dropdown", name = "field",        x = 6, y = 1, width = 6,
                                                            items = { "Actor", "Effect", "Style" }, value = re.sub(aactor.field:value(), "^\\w", string.upper) },
               { class = "label",                           x = 0, y = 2, width = 24,
                                                            label = "This setting will apply to all Akatsumekusa's scripts." } }
    buttons = { "&Apply", "Close" }
    button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Close", no = "Close", cancel = "Close" }

    button, result_table = aegisub.dialog.display(dialog, buttons, button_ids)

    if button == false or button == "Close" then aegisub.cancel()
    elseif button == "&Apply" then
        aactor.field:setValue(string.lower(result_table["field"]))
    end
end

DepCtrl:registerMacros({
    { "Backup", "Backup selected lines", Backup },
    { "Edit settings", "Edit backup settings", Field }
})
