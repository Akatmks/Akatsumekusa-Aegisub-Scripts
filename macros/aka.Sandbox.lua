-- aka.uikit
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

versioning.name = "Sandbox"
versioning.description = "LuaInterpret but raw"
versioning.version = "1.0.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.Sandbox"

versioning.requiredModules = "[{ \"moduleName\": \"aka.uikit\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"ILL.ILL\" }, { \"moduleName\": \"a-mo.LineCollection\" }, { \"moduleName\": \"l0.ASSFoundation\" }, { \"moduleName\": \"aegisub.re\" }, { \"moduleName\": \"aka.unicode\" }]"

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
        { "ILL.ILL" },
        { "a-mo.LineCollection" },
        { "l0.ASSFoundation" },
        { "aegisub.re" },
        { "aka.unicode" }
    }
})

local uikit, outcome, ILL, LineCollection, ASS, re, unicode = DepCtrl:requireModules()
local adialog, abuttons, adisplay = uikit.dialog, uikit.buttons, uikit.display
local o, op, ok, err = outcome.o, outcome.pcall, outcome.ok, outcome.err

local Sandbox = function(sub, sel, act)
    local dialog = adialog.new({ width = 60 })

    local err_dialog = adialog.ifable({ name = "err_msg" })
    err_dialog:label({ label = "Error occuried:" })
    err_dialog:textbox({ height = 6, name = "err_msg" })

    dialog:label({ label = "These variables are required:" })
    local one, two, three, four
    one, two, three, four = dialog:columns({ widths = { 15, 15, 15, 15 } })
    one:label({ label = "sub: Subtitle object" })
    two:label({ label = "sel: Selected lines" })
    three:label({ label = "act: Active line" })
    four:label({ label = "aegisub: aegisub object" })
    one, three = dialog:columns({ widths = { 40, 20 } })
    one:label({ label = "Aegi, Ass, Line, Table, ...: All classes from ILL.ILL" })
    three:label({ label = "ass: Ass loaded with sub, sel and act" })
    one:label({ label = "LineCollection, ASS: a-mo.LineCollection and l0.ASSFoundation" })
    three:label({ label = "lines: LineCollection loaded with sub and sel" })
    one, two, three = dialog:columns({ widths = { 20, 20, 20 } })
    one:label({ label = "logger: logger from l0.DependencyControl" })
    two:label({ label = "re: aegisub.re" })
    three:label({ label = "unicode: aegisub.unicode (aka.unicode)" })

    dialog:label({ label = "Enter Lua code:" })
          :textbox({ height = 20, name = "command" })

    local buttons = abuttons.ok("Run"):extra("&Open snippet"):extra("&Save as snippet"):close("Close")

    adisplay(dialog, buttons)
        :repeatUntil(function(button, result)
            if button == "&Open snippet" then
                o(aegisub.dialog.open("Opening snippet..."))
                    :ifOk(function(f)
                        o(io.open(f, "r"))
                            :andThen(function(f)
                                local r = o(f:read("*a"))
                                    :ifOk(function(t)
                                        result["command"] = t end)
                                f:close() return
                                r end)
                            :ifErr(function(msg)
                                result["err_msg"] = msg end) end) return
                err(result)
            elseif button == "&Save as snippet" then
                o(aegisub.dialog.save("Saving snippet..."))
                    :ifOk(function(f)
                        o(io.open(f, "w"))
                            :andThen(function(f)
                                local r = o(f:write(result["command"]))
                                f:close() return
                                r end)
                            :ifErr(function(msg)
                                result["err_msg"] = msg end) end) return
                err(result)
            else -- button == "Run"
                local gt = setmetatable({}, { __index = _G })
                gt.uikit = uikit
                for k, v in pairs(ILL) do
                    if not string.find(k, "version") then
                        gt[k] = v
                end end
                gt.ass = ILL.Ass(sub, sel, act)
                gt.LineCollection = LineCollection
                gt.lines = LineCollection(sub, sel)
                gt.ASS = ASS
                gt.re = re
                gt.unicode = unicode

                local r = op(loadstring(result["command"]))
                if r:isErr() then
                    result["err_msg"] = r:unwrapErr()
                    return err(result)
                end
                local f = r:unwrap()
                setfenv(f, gt)

                r = op(f())
                if r:isErr() then
                    result["err_msg"] = r:unwrapErr()
                    return err(result)
                end
                return ok()
            end end)
end

DepCtrl:registerMacro(Sandbox)
