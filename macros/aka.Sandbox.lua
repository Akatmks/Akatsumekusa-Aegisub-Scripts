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
versioning.version = "1.0.5"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.Sandbox"

versioning.requiredModules = "[{ \"moduleName\": \"aegisub.re\" }, { \"moduleName\": \"aka.config\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"aka.uikit\" }, { \"moduleName\": \"ILL.ILL\" }, { \"moduleName\": \"moonscript\" }, { \"moduleName\": \"a-mo.LineCollection\" }, { \"moduleName\": \"l0.ASSFoundation\" }, { \"moduleName\": \"Yutils\" }, { \"moduleName\": \"aka.unicode\" }, { \"moduleName\": \"aegisub.util\" }]"

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
        { "aegisub.re" },
        { "aka.config" },
        { "aka.outcome" },
        { "aka.uikit" },
        { "ILL.ILL" },
        { "moonscript" },
        { "a-mo.LineCollection" },
        { "l0.ASSFoundation" },
        { "Yutils" },
        { "aka.unicode" },
        { "aegisub.util" }
    }
})

local re, config, outcome, uikit, ILL, moonscript, LineCollection, ASS, yutils, unicode, util = DepCtrl:requireModules()
local file_extension = re.compile([[.*\.([^\\\/]+)$]])
local presets_config = config.make_editor({ display_name = "aka.Sandbox/presets",
                                            presets = { ["Default"] = {} },
                                            default = "Default" })
local o, ok, err = outcome.o, outcome.ok, outcome.err
local adialog, abuttons, adisplay = uikit.dialog, uikit.buttons, uikit.display
local Table = ILL.Table

local Sandbox = function(sub, sel, act)
    local presets = presets_config:read_and_validate_config_if_empty_then_default_or_else_edit_and_save("aka.Sandbox", "presets", function(config)
        for k, v in pairs(config) do
            if type(k) ~= "string" then
                return err("All keys in the config table shall be strings.\nKey " .. tostring(k) .. " is a " .. type(k) .. ".")
        end end
        return ok(config) end)
        :ifErr(aegisub.cancel)
        :unwrap()

    local dialog = adialog.new({ width = 57 })

    local left, right = dialog:columns({ widths = { 55, 2 } })
    left:textbox({ height = 31, name = "command" })

    local err_dialog = right:ifable({ name = "err_msg" })
    err_dialog:label({ label = "𝗘𝗿𝗿𝗼𝗿 𝗼𝗰𝗰𝘂𝗿𝗶𝗲𝗱 during previous operation:" })
              :textbox({ height = 12, name = "err_msg" })

    right:label({ label = "Select Language:" })
         :dropdown({ name = "language", items = { "Lua", "MoonScript" }, value = "Lua" })

    right:label({ label = "Available variables:" })
    local var, exp = right:columns({ widths = { 1, 1 } })
    var:label({ label = "│ sub" })
    exp:label({ label = "Subtitle object" })
    var:label({ label = "│ sel:" })
    exp:label({ label = "Selected lines" })
    var:label({ label = "│ act:" })
    exp:label({ label = "Active line" })

    right:label({ label = "Required libraries:" })
    var, exp = right:columns({ widths = { 1, 1 } })
    var:label({ label = "│ Ass, Line, Aegi, …:" })
    exp:label({ label = "All ILL.ILL classes" })
    var:label({ label = "│ ass:" })
    exp:label({ label = "Ass loaded with subtitle" })
    var:label({ label = "│ LineCollection:" })
    exp:label({ label = "a-mo.LineCollection" })
    var:label({ label = "│ lines:" })
    exp:label({ label = "LineCollection loaded" })
    var:label({ label = "│ ASS:" })
    exp:label({ label = "l0.ASSFoundation" })
    var:label({ label = "│ logger:" })
    exp:label({ label = "logger from l0.DepCtrl" })
    var:label({ label = "│ aegisub:" })
    exp:label({ label = "aegisub object" })
    var:label({ label = "│ yutils:" })
    exp:label({ label = "Yutils" })
    var:label({ label = "│ re:" })
    exp:label({ label = "aegisub.re" })
    var:label({ label = "│ unicode:" })
    exp:label({ label = "aegisub.unicode (m)" })
    var:label({ label = "│ util:" })
    exp:label({ label = "aegisub.util" })

    local buttons = abuttons.ok("&Run"):extra("&Load Preset"):extra("&Save As Preset"):extra("&Delete Preset"):extra("Open Sn&ippet"):extra("Save As Snipp&et"):close("Close")

    local r = adisplay(dialog, buttons)
        :loadRepeatUntilAndSave("aka.Sandbox", "dialog", function(button, result)
            result["err_msg"] = false

            if button == "&Load Preset" then
                local items = {}
                local value
                for k, _ in pairs(presets) do
                    table.insert(items, k)
                    value = k
                end
                local dialog = adialog.new({ width = 16 })
                                      :label_dropdown({ label = "Presets:", name = "preset", items = items, value = value })
                local buttons = abuttons.ok("Load"):close("Back")
                local b, r = adisplay(dialog, buttons):resolve()
                if buttons:is_ok(b) then
                    result["command"] = presets[r["preset"]]
                end
                return err(result)
            elseif button == "&Delete Preset" then
                local items = {}
                local value
                for k, _ in pairs(presets) do
                    table.insert(items, k)
                    value = k
                end
                local dialog = adialog.new({ width = 16 })
                                      :label_dropdown({ label = "Presets:", name = "preset", items = items, value = value })
                local buttons = abuttons.ok("Delete"):close("Back")
                local b, r = adisplay(dialog, buttons):resolve()
                if buttons:is_ok(b) then
                    presets[r["preset"]] = nil
                    presets_config.write_config("aka.Sandbox", "presets", presets)
                        :ifErr(function(msg)
                            result["err_msg"] = "Error occuried when updating presets:\n" ..
                                                msg end)
                end
                return err(result)
            elseif button == "&Save As Preset" then
                local dialog = adialog.new({ width = 16 })
                                      :label_edit({ label = "Preset name:", name = "preset" })
                local buttons = abuttons.ok("Save"):close("Back")
                local b, r = adisplay(dialog, buttons):resolve()
                if buttons:is_ok(b) then
                    presets[r["preset"]] = result["command"]
                    presets_config.write_config("aka.Sandbox", "presets", presets)
                        :ifErr(function(msg)
                            result["err_msg"] = "Error occuried when saving presets:\n" ..
                                                msg end)
                end
                return err(result)
            elseif button == "Open Sn&ippet" then
                o(aegisub.dialog.open("Opening snippet...", "", "", ""))
                    :ifOk(function(path)
                        o(io.open(path, "r"))
                            :andThen(function(f)
                                local r = o(f:read("*a"))
                                    :ifOk(function(t)
                                        result["command"] = t
                                        local ext = file_extension:match(path)[2]["str"]
                                        if string.lower(ext) == "lua" then
                                            result["language"] = "Lua"
                                        elseif string.lower(ext) == "moon" then
                                            result["language"] = "MoonScript"
                                        end end)
                                f:close() return
                                r end)
                            :ifErr(function(msg)
                                result["err_msg"] = "Error occuried when opening snippet:\n" ..
                                                    msg end) end) return
                err(result)
            elseif button == "Save As Snipp&et" then
                o(aegisub.dialog.save("Saving as snippet...", "", "", ""))
                    :ifOk(function(f)
                        o(io.open(f, "w"))
                            :andThen(function(f)
                                local r = o(f:write(result["command"]))
                                f:close() return
                                r end)
                            :ifErr(function(msg)
                                result["err_msg"] = "Error occuried when saving snippet:\n" ..
                                                    msg end) end) return
                err(result)
            else -- button == "Run"
                local gt = setmetatable({}, { __index = _G })
                gt.sub = sub
                gt.sel = sel
                gt.act = act
                for k, v in pairs(ILL) do
                    if not string.find(k, "version") then
                        gt[k] = v
                end end
                gt.ass = ILL.Ass(sub, sel, act)
                gt.LineCollection = LineCollection
                gt.lines = LineCollection(sub, sel)
                gt.ASS = ASS
                gt.aegisub = aegisub
                gt.logger = DepCtrl:getLogger()
                gt.yutils = yutils
                gt.re = re
                gt.unicode = unicode
                gt.util = util

                local r
                if result["language"] == "Lua" then
                    r = o(loadstring(result["command"]))
                else
                    r = o(moonscript.loadstring(result["command"]))
                end
                if r:isErr() then
                    result["err_msg"] = "Error occuried during loadstring():\n" ..
                                        r:unwrapErr()
                    return err(result)
                end
                local f = r:unwrap()
                setfenv(f, gt)

                r = o(xpcall(f, function(err)
                    if err ~= nil and type(err) ~= "string" then err = Table.view(err) end
                    result["err_msg"] = "Error occuried during execution:\n" ..
                                        debug.traceback(err) end))
                if r:isOk() then
                    r = r:unwrap()
                    if type(r) == "table" and type(r[1]) == "table" and type(r[2]) == "number" then
                        (function()
                            for i, v in ipairs(result[1]) do
                                if type(v) ~= "number" then
                                    return err()
                            end end
                            return ok() end)()
                            :ifOk(function()
                                result[1] = r[1] result[2] = r[2] end)
                    end
                    return ok(result)
                else
                    return err(result)
            end end end)

    if r:isOk() then
        r = r:unwrap()
        if type(r) == "table" then
            return r[1], r[2]
end end end

DepCtrl:registerMacro(Sandbox)
