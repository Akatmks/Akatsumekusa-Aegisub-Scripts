-- aka.InlineStorage
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

versioning.name = "InlineStorage"
versioning.description = "Put AAE data or preset files inline so they are available to the people reworking on the subtitle in the future"
versioning.version = "1.0.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.InlineStorage"

versioning.requiredModules = "[{ \"moduleName\": \"aka.uikit\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"aegisub.clipboard\" }]"

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
        { "aka.uikit" },
        { "aka.outcome" },
        { "aegisub.clipboard" }
    }
})

local uikit, outcome, clipboard = DepCtrl:requireModules()
local adialog, abuttons, adisplay = uikit.dialog, uikit.buttons, uikit.display
local o = outcome.o

local main = function(sub, sel, act)
    line = sub[act]
    text = string.gsub(line.text, "\\N", "\n")
    local set_text = function(text)
        line.text = string.gsub(text, "\n", "\\N")
        sub[act] = line
    end

    ::restart::
    local dialog = adialog.new({ width = 50 })
                          :textbox({ height = 32, name = "text", value = text })
    local buttons = abuttons.ok("Modify")
                            :extra("&Copy To Clipboard")
                            :extra("&Paste From Clipboard")
                            :extra("&Import From File")
                            :extra("&Export To File")
                            :cancel("Close")
    local b, r = adisplay(dialog, buttons):resolve()

    if buttons:is_ok(b) then
        set_text(r["text"])
    elseif b == "&Copy To Clipboard" then
        clipboard.set(r["text"])
    elseif b == "&Paste From Clipboard" then
        o(clipboard.get())
            :ifOk(function(t)
                set_text(t) end)
            :ifErr(function()
                aegisub.debug.out("Error occurred when pasting.") end)
    elseif b == "&Import From File" then
        if not o(aegisub.dialog.open("Importing...", "", "", ""))
            :ifOk(function(path)
                o(io.open(path, "r"))
                    :andThen(function(f)
                        local r = o(f:read("*a"))
                            :ifOk(function(t)
                                set_text(t) end)
                        f:close() return
                        r end)
                    :ifErr(function(msg)
                        aegisub.debug.out("Error occurred when importing from file:\n" ..
                                          msg) end) end) then
            goto restart
        end
    elseif b == "&Export To File" then
        if not o(aegisub.dialog.save("Exporting...", "", "", ""))
            :ifOk(function(f)
                o(io.open(f, "w"))
                    :andThen(function(f)
                        local r = o(f:write(r["text"]))
                        f:close() return
                        r end)
                    :ifErr(function(msg)
                        aegisub.debug.out("Error occurred when exporting to file:\n" ..
                                          msg) end) end) then
            goto restart
        end
end end

DepCtrl:registerMacro(main)
