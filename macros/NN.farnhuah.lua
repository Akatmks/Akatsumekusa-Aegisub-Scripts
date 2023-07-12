-- NN.Fanhua
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

versioning.name = "farnhuah"
versioning.description = "farn huah jeau been"
versioning.version = "1.0.4"
versioning.author = "Akatsumekusa"
versioning.namespace = "NN.farnhuah"

versioning.requireModules = "[{ \"moduleName\": \"json\" }, { \"moduleName\": \"aka.request\" }, { \"moduleName\": \"aka.config\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"aegisub.re\" }, { \"moduleName\": \"aka.actor\" }, { \"moduleName\": \"aka.optimising\", \"optional\": True }]"

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
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
        {
            { "json" },
            { "aka.request" },
            { "aka.config" },
            { "aka.outcome" },
            { "aegisub.re" },
            { "aka.actor" },
            { "aka.optimising", optional = true }
        }
    }):requireModules()
end
local json = require("json")
local request = require("aka.request")
local aactor = require("aka.actor")
local aconfig = require("aka.config")
local outcome = require("aka.outcome")
local ok, err = outcome.ok, outcome.err
local re = require("aegisub.re")
local hasOptimising, optimising = pcall(require, "aka.optimising")


local Detect
Detect = function(line)
    local return_

    return_ = false
    for _, flag in ipairs(aactor._flags(line, "")) do
        if flag["body"] == "chs" then
            if return_ == false then return_ = "chs"
            else return false end
        elseif flag["body"] == "cht" then
            if return_ == false then return_ = "cht"
            else return false end
        elseif flag["body"] ~= "" then
            return false
    end end
    return return_
end


local target
local Target
Target = function(sub)
    local i
    local detect

    if target then return end

    for i = 1, #sub do
        line = sub[i]
        if line.class == "dialogue" then
            detect = Detect(line)
            
            if detect == "chs" then
                if line.comment == false then target = "chs"
                else target = "cht" end
            elseif detect == "cht" then
                if line.comment == false then target = "cht"
                else target = "chs" end
    end end end

    if not target then
        target = false
end end


local SwitchST
SwitchST = function(sub)
    local i
    local line

    if not target then Target(sub) end
    
    if not target then return
    elseif target == "chs" then target = "cht"
    elseif target == "cht" then target = "chs" end

    for i = 1, #sub do
        line = sub[i]
        if line.class == "dialogue" then
            detect = Detect(line)

            if target == "chs" and detect == "chs" or
               target == "cht" and detect == "cht" then
                if line.comment == true then
                    line.comment = false
                    sub[i] = line
                end
            elseif target == "chs" and detect == "cht" or
                   target == "cht" and detect == "chs" then
                if line.comment == false then
                    line.comment = true
                    sub[i] = line
end end end end end


local config
local validation_func
local Config
local ConfigTarget
aconfig = aconfig.make_editor({
    display_name = "zhconvert",
    presets = {
        ["SweetSub"] = {
            converter = "Taiwan",
            modules = {
                ["*"] = 0,
                ["ChineseVariant"] = -1,
                ["Computer"] = -1,
                ["ProperNoun"] = -1,
                ["Repeat"] = -1,
                ["RepeatAutoFix"] = -1,
                ["Unit"] = -1
            },
            userPostReplace = [[
Source Han Sans SC=Source Han Sans TC
Source Han Sans CN=Source Han Sans TW
SourceHanSansSC=SourceHanSansTC

Source Han Serif SC=Source Han Serif TC
Source Han Serif CN=Source Han Serif TW
]]      }
    },
    default = "SweetSub"
})
validation_func = function(configd)
    local msg

    if not configd then
        msg = "Root object not found"
    else
        if configd.converter == nil then
            if not msg then msg = "Key \"converter\" is required by zhconvert\nSome possible values includes \"Traditional\", \"Hongkong\", \"Taiwan\" and \"WikiTraditional\""
            else msg = msg .. "\n" .. "Key \"converter\" is required by zhconvert\nSome possible values includes \"Traditional\", \"Hongkong\", \"Taiwan\" and \"WikiTraditional\"" end
        elseif configd.converter ~= "Simplified" and
               configd.converter ~= "Traditional" and
               configd.converter ~= "China" and
               configd.converter ~= "Hongkong" and
               configd.converter ~= "Taiwan" and
               configd.converter ~= "Pinyin" and
               configd.converter ~= "Bopomofo" and
               configd.converter ~= "Mars" and
               configd.converter ~= "WikiSimplified" and
               configd.converter ~= "WikiTraditional" then
            if not msg then msg = "Invalid value for key \"converter\"\nSome possible values includes \"Traditional\", \"Hongkong\", \"Taiwan\" and \"WikiTraditional\""
            else msg = msg .. "\n" .. "Invalid value for key \"converter\"\nSome possible values includes \"Traditional\", \"Hongkong\", \"Taiwan\" and \"WikiTraditional\"" end
        end
        if configd.text ~= nil then
            if not msg then msg = "Key \"text\" should be left nil for the script to fill"
            else msg = msg .. "\n" .. "Key \"text\" should be left nil for the script to fill" end
    end end
    
    if not msg then return ok(configd)
    else return err(msg) end
end
Config = function()
    if not config then
        config = aconfig:read_and_validate_config_or_else_edit_and_save("NN.farnhuah", validation_func)
            :ifErr(aegisub.cancel)
            :unwrap()
end end
ConfigTarget = function()
    if config.converter == "Simplified" or
       config.converter == "China" or
       config.converter == "WikiSimplified" then
        return "chs"
    elseif config.converter == "Traditional" or
           config.converter == "Hongkong" or
           config.converter == "Taiwan" or
           config.converter == "WikiTraditional" then
        return "cht"
    else return "else" end
end
EditConfig = function()
    config = aconfig:read_edit_validate_and_save_config("NN.farnhuah", validation_func)
        :ifErr(aegisub.cancel)
        :unwrap()
end


local Fanhua
local ProprocessSub
local LoadLines
local FanhuaLines
local ApplyLines
local ApplyLinesApply

Fanhua = function(sub, sel, act)
    local ctarget
    local lines
    local farnhuah

    if hasOptimising then optimising.start() end

    if hasOptimising then optimising.lap("Loading config") end
    Config()

    ctarget = ConfigTarget()
    ProprocessSub(sub, ctarget)

    lines, farnhuah = LoadLines(sub, sel)

    farnhuah = FanhuaLines(farnhuah)

    sel, act = ApplyLines(sub, sel, act, ctarget, lines, farnhuah)
    
    if hasOptimising then optimising.lap("farnhuah finished") end
    return sel, act
end
ProprocessSub = function(sub, ctarget)
    if hasOptimising then optimising.lap("Detecting target") end
    if not target then Target(sub) end
    
    if ctarget == "chs" then
        if not target then target = "chs"
        elseif target == "cht" then
            if hasOptimising then optimising.lap("Switching chs and cht") end
            SwitchST(sub)
        end
    elseif ctarget == "cht" then
        if not target then target = "cht"
        elseif target == "chs" then
            if hasOptimising then optimising.lap("Switching chs and cht") end
            SwitchST(sub)
        end
end end
LoadLines = function(sub, sel)
    local lines
    local farnhuah

    lines = {}
    farnhuah = ""
    for i = 1, #sel do
        if hasOptimising then optimising.lap("Loading line " .. tostring(i)) end

        lines[i] = sub[sel[i]]
        farnhuah = farnhuah .. lines[i].text .. "\n"
    end

    return lines, farnhuah
end
FanhuaLines = function(farnhuah)
    local data
    local response
    local err
    local msg

    data = {}
    for k, v in pairs(config) do
        if type(v) == "string" then data[k] = v
        elseif type(v) == "table" then data[k] = json.encode(v)
        else data[k] = tostring(v) end
    end
    data.text = farnhuah
    data.ensureNewlineAtEof = "true"
    response, err, msg = request.send("https://api.zhconvert.org/convert", { method = "GET", data = data })

    if not response then
        aegisub.debug.out("[NN.farnhuah] Request failed with error " .. tostring(err) .. "\n")
        aegisub.debug.out("[NN.farnhuah] " .. tostring(err) .. " " .. tostring(msg) .. "\n")
        aegisub.cancel()
    elseif response.code ~= 200 then
        aegisub.debug.out("[NN.farnhuah] Request failed with status code " .. tostring(response.code) .. "\n")
        if response.body ~= "" then aegisub.debug.out("[NN.farnhuah] " .. tostring(response.code) .. " " .. tostring(response.body) .. "\n") end
        aegisub.cancel()
    end
    data = json.decode(response.body)
    if data.code ~= 0 then
        aegisub.debug.out("[NN.farnhuah] zhconvert responded with code " .. tostring(data.code) .. "\n")
        aegisub.debug.out("[NN.farnhuah] " .. tostring(data.code) .. " " .. tostring(data.msg) .. "\n")
        aegisub.cancel()
    end

    return data.data.text
end
ApplyLines = function(sub, sel, act, ctarget, lines, farnhuah)
    local i
    local j

    j = #sel repeat
        i = 1 repeat
            if j - i == sel[j] - sel[i] then
                if hasOptimising then optimising.lap("Writing line " .. tostring(i) .. " to " .. tostring(j)) end
                
                sel, act = ApplyLinesApply(sub, sel, act, ctarget, lines, farnhuah, i, j)
                j = i - 1
                break
            else i = i + 1 end
        until false
    until j == 0

    return sel, act
end
ApplyLinesApply = function(sub, sel, act, ctarget, lines, farnhuah, i, j)
    local k
    local comment_
    local farnhuahs

    local select = function(selected, sel_i, sel_j)
        if selected < sel_i then return selected
        else return selected + sel_j - sel_i + 1 end
    end

    for k = i, j do
        if ctarget == "chs" then
            lines[k][aactor.field:value()] = "cht"
            comment_ = lines[k].comment
            lines[k].comment = true
            sub[sel[k]] = lines[k]
            lines[k].comment = comment_

        elseif ctarget == "cht" then
            lines[k][aactor.field:value()] = "chs"
            comment_ = lines[k].comment
            lines[k].comment = true
            sub[sel[k]] = lines[k]
            lines[k].comment = comment_
    end end
    
    farnhuahs = {}
    k = i
    for t in farnhuah:gmatch"([^\n]*)\n" do
        farnhuahs[k] = t
        k = k + 1
    end

    for k = j, i, -1 do
        if ctarget == "chs" then
            lines[k][aactor.field:value()] = "chs"
        elseif ctarget == "cht" then
            lines[k][aactor.field:value()] = "cht"
        end
        lines[k].text = farnhuahs[k]
        
        sub[-sel[j]-1] = lines[k]
    end
    
    i = sel[i] j = sel[j]
    for k in ipairs(sel) do sel[k] = select(sel[k], i, j) end
    act = select(act, i, j)
    return sel, act
end


local Field
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
                                                            items = { "Actor", "Effect", "Style" }, value = re.sub(aactor.field:value(), "^\\w", string.upper) },
               { class = "label",                           x = 0, y = 2, width = 24,
                                                            label = "This setting will apply to all NN and aka scripts." } }
    buttons = { "&Apply", "Close" }
    button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Close", no = "Close", cancel = "Close" }

    button, result_table = aegisub.dialog.display(dialog, buttons, button_ids)

    if button == false or button == "Close" then aegisub.cancel()
    elseif button == "&Apply" then
        aactor.field:setValue(string.lower(result_table["field"]))
end end


if hasDepCtrl then
    DepCtrl:registerMacros({
        { "farnhuah/farn huah", "farnhuah selected lines", Fanhua },
        { "farnhuah/chie huann chs her cht", "Comment all the chs and uncomment all the cht lines in the subtitle, or vice versa", SwitchST },
        { "farnhuah/zhconvert sheh dinq", "Edit zhconvert settings", EditConfig },
        { "farnhuah/chs cht chyi biau sheh dinq", "Change where chs and cht flags are placed", Field }
    })
else
    aegisub.register_macro("farnhuah/farn huah", "farnhuah selected lines", Fanhua)
    aegisub.register_macro("farnhuah/chie huann chs her cht", "Comment all the chs and uncomment all the cht lines in the subtitle, or vice versa", SwitchST)
    aegisub.register_macro("farnhuah/zhconvert sheh dinq", "Edit zhconvert settings", EditConfig)
    aegisub.register_macro("farnhuah/chs cht chyi biau sheh dinq", "Change where chs and cht flags are placed", Field)
end
