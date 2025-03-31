-- aka.99PercentTags
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

versioning.name = "99%Tags"
versioning.description = "Add or modify tags on selected lines"
versioning.version = "1.1.6"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.99PercentTags"

versioning.requiredModules = "[{ \"moduleName\": \"aka.config\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"ILL.ILL\" }, { \"moduleName\": \"aegisub.util\" }, { \"moduleName\": \"aegisub.re\" }, { \"moduleName\": \"aka.StackTracePlus\" }, { \"moduleName\": \"aka.uikit\" }, { \"moduleName\": \"aka.unicode\" }]"

script_name = versioning.name
script_description = versioning.description
script_version = versioning.version
script_author = versioning.author
script_namespace = versioning.namespace

DepCtrl = require("l0.DependencyControl")({
    feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "aka.config", version = "1.0.0" },
        { "aka.outcome", version = "1.0.0" },
        { "ILL.ILL", version = "1.0.0" },
        { "aegisub.util" },
        { "aegisub.re" },
        { "aka.StackTracePlus", version = "1.0.0" },
        { "aka.uikit", version = "1.0.0" },
        { "aka.unicode", version = "1.0.0" }
    }
})
DepCtrl:requireModules()
local aconfig = require("aka.config")
local outcome = require("aka.outcome")
local o, ok, err, some, none = outcome.o, outcome.ok, outcome.err, outcome.some, outcome.none
local _ao_xpcall = outcome.xpcall
local ILL = require("ILL.ILL")
local Ass, Line, Table = ILL.Ass, ILL.Line, ILL.Table
local autil = require("aegisub.util")
local re = require("aegisub.re")
require("aka.StackTracePlus")()
local uikit = require("aka.uikit")
local adialog, abuttons, adisplay = uikit.dialog, uikit.buttons, uikit.display
local unicode = require("aka.unicode")



local table_concat
local single_tagsBlock_tags
local an_tags
local pos_tags
local move_tags
local org_tags
local alpha_tags
local single_tags
local colour_tags
local auto_dialog_tags
local non_tag_tags
local eval_tags
local prepro_tags
local all_tags
local parse_tags
local parse_other_data

local main
local re_tagsBlock_viewing
local presets_config
local show_dialog
local dialog_aconfig
local dialog_config
local generate_dialog
local apply_data
local re_extra_spaces
local re_if_omitted
local re_match_underscore
local re_match_invalid_varnames
local process_data
local re_clean_traceback
local execute_tags
local apply_tags



table_concat = function(...)
    local new
    
    new = {}
    for _, t in ipairs({...}) do
        for _, v in ipairs(t) do
            table.insert(new, v)
    end end

    return new
end
--[[
Select mode:
[ Generate data from active line once and apply to al... ]
Select tags block:  
[ 1 (Viewing)                                            ] 
Preprocess tag data:
[                                                        ]
[                                                        ]
[                                                        ]
[                                                        ]
Edit tag data:
an    5   [      ]  fn    "Nunito"        [              ]
posx  960 [      ]  fs    60  [      ]  cr    255 [      ]
posy  480 [      ]  fsp   0   [      ]  cg    255 [      ]
move2x -  [      ]  blur  0.5 [      ]  cb    255 [      ]
move2y -  [      ]  bord  2.5 [      ]  3cr   0   [      ]
orgx  960 [      ]  xbord 0   [      ]  3cg   0   [      ]
orgy  480 [      ]  ybord 0   [      ]  3cb   0   [      ]
frx   0   [      ]  shad  0   [      ]  4cr   0   [      ]
fry   0   [      ]  xshad 0   [      ]  4cg   0   [      ]
frz   0   [      ]  yshad 0   [      ]  4cb   0   [      ]
fax   0   [      ]  b     0   [      ]  alpha 255 [      ]
fay   0   [      ]  i     0   [      ]  1a    255 [      ]
fscx  100 [      ]  u     0   [      ]  3a    255 [      ]
fscy  100 [      ]  s     0   [      ]  4a    255 [      ]
q     0   [      ]  be    0   [      ]
Edit line data:
layer 0   [      ]  start [          ]  end   [          ]
Style [          ]  Actor [          ]  Effect [         ]
Load Preset:                 Save As Preset:
[           Last            ][                           ]
]]
an_tags = { "an" }
single_tagsBlock_tags = { "frx", "fry", "frz", "fax", "fay", "fscx", "fscy", "q",
                          "fn", "fs", "fsp", "blur", "bord", "xbord", "ybord", "shad", "xshad", "yshad", "b", "i", "u", "s", "be" }
single_tags = table_concat(an_tags, single_tagsBlock_tags)

pos_tags = { "posx", "posy" }
move_tags = table_concat(pos_tags, { "move2x", "move2y" })
org_tags = { "orgx", "orgy" }

colour_tags = { ["c"] = { "cr", "cg", "cb" }, ["3c"] = { "3cr", "3cg", "3cb" }, ["4c"] = { "4cr", "4cg", "4cb" } }
alpha_tags = { "alpha", "1a", "3a", "4a" }
auto_dialog_tags = table_concat(an_tags, move_tags, org_tags, single_tagsBlock_tags,
                                colour_tags["c"], colour_tags["3c"], colour_tags["4c"],
                                alpha_tags)

non_tag_tags = { "layer", "start", "end_",
                 "Style", "Actor", "Effect" }
eval_tags = table_concat(auto_dialog_tags, non_tag_tags)

prepro_tags = { "prepro" }
all_tags = table_concat(prepro_tags, eval_tags)

parse_tags = function(data, ILL_data)
    local ILL_data_tag

    ILL_data_tag = function(ILL_data, tag)
        if ASS_TAGS[tag].style_name then
            return ILL_data[ASS_TAGS[tag].style_name]
        else
            return ILL_data[tag]
    end end

    for _, tag in ipairs(single_tags) do
        data[tag] = ILL_data_tag(ILL_data, tag)
    end

    data[pos_tags[1]], data[pos_tags[2]] = table.unpack(ILL_data_tag(ILL_data, "pos"))
    if ILL_data_tag(ILL_data, "move") then
        _, _, data[move_tags[3]], data[move_tags[4]], _, _ = table.unpack(ILL_data_tag(ILL_data, "move"))
    end
    data[org_tags[1]], data[org_tags[2]] = table.unpack(ILL_data_tag(ILL_data, "org"))

    for tag, names in pairs(colour_tags) do
        data[names[1]], data[names[2]], data[names[3]], _ = autil.extract_color(ILL_data_tag(ILL_data, tag))
    end
    for _, tag in ipairs(alpha_tags) do
        _, _, _, data[tag] = autil.extract_color(ILL_data_tag(ILL_data, tag))
end end

parse_other_data = function(data, line, width, height)
    data["layer"] = line.layer
    data["start"] = line.start_time
    data["end_"] = line.end_time
    data["Style"] = line.style
    data["Actor"] = line.actor
    data["Effect"] = line.effect

    data["line"] = line
    data["width"] = width
    data["height"] = height
end



main = function(sub, sel, act, mode)
    local ass
    local dialog_data
    local act_data
    
    ass = Ass(sub, sel, act)

    dialog_data, act_data = show_dialog(ass, sub, act, mode)

    apply_data(ass, sub, act, dialog_data, act_data)

    return ass:getNewSelection()
end



re_tagsBlock_viewing = re.compile[[(\d+) \(Viewing\)]]
presets_config = aconfig.make_editor({ display_name = "aka.99PercentTags/presets",
                                      presets = { ["Default"] = {}, ["Example"] = [[{\n  "Swap fsc": {\n    "1a": "",\n    "3a": "",\n    "3cb": "",\n    "3cg": "",\n    "3cr": "",\n    "4a": "",\n    "4cb": "",\n    "4cg": "",\n    "4cr": "",\n    "Actor": "",\n    "Effect": "",\n    "Style": "",\n    "alpha": "",\n    "an": "",\n    "b": "",\n    "be": "",\n    "blur": "",\n    "bord": "",\n    "cb": "",\n    "cg": "",\n    "cr": "",\n    "end_": "",\n    "fax": "",\n    "fay": "",\n    "fn": "",\n    "frx": "",\n    "fry": "",\n    "frz": "",\n    "fs": "",\n    "fscx": "fscy",\n    "fscy": "swap",\n    "fsp": "",\n    "i": "",\n    "layer": "",\n    "mode": 2,\n    "move2x": "",\n    "move2y": "",\n    "orgx": "",\n    "orgy": "",\n    "posx": "",\n    "posy": "",\n    "prepro": "swap = fscx",\n    "q": "",\n    "s": "",\n    "shad": "",\n    "start": "",\n    "tagsblock": 1,\n    "u": "",\n    "xbord": "",\n    "xshad": "",\n    "ybord": "",\n    "yshad": ""\n  }\n}]] },
                                      default = "Default" })
show_dialog = function(ass, sub, act, mode)
    local dialog_base
    local dialog_data
    local act_l
    local act_tagsBlocks
    local act_data
    local presets

    local dialog
    local buttons
    local button_ids
    local button
    
    local match
    local new_dialog_data

    dialog_base = {}
    dialog_data = {}

    dialog_base["modes"] = { "Generate data from active line once and apply to all selected lines",
                             "Generate and apply data on each selected line respectively" }
    dialog_data["mode"] = mode

    for _, v in ipairs(all_tags) do
        dialog_data[v] = ""
    end

    act_l = sub[act]
    act_tagsBlocks = Line.tagsBlocks(ass, act_l, false)
    dialog_base["tagsblocks"] = {}
    for i, _ in ipairs(act_tagsBlocks) do
        dialog_base["tagsblocks"][i] = tostring(i)
    end
    dialog_data["tagsblock"] = 1

    presets = presets_config:read_and_validate_config_if_empty_then_default_or_else_edit_and_save("aka.99PercentTags", "presets", function(config)
        for k, v in pairs(config) do
            if not (type(k) == "string" and
                    type(v) == "table") then return
                err("Error occurs when parsing key \"" .. tostring(k) .. "\".\nView Preset „Example“ below for an example of the format.")
        end end return
        ok(config) end)
        :ifErr(aegisub.cancel)
        :unwrap()

    dialog_base["presets"] = {}
    for k, _ in pairs(presets) do
        table.insert(dialog_base["presets"], k)
    end
    table.sort(dialog_base["presets"])
    if presets["(Recall last)"] then
        dialog_data["preset"] = "(Recall last)"
    else
        for k, _ in pairs(presets) do
            dialog_data["preset"] = k
            break
    end end
    dialog_data["preset_new"] = ""

    dialog_base["help"] = false

    act_data = {}
    parse_other_data(act_data, act_l, act_tagsBlocks.width, act_tagsBlocks.height)

    while true do
        parse_tags(act_data, act_tagsBlocks[dialog_data["tagsblock"]].data)

        dialog_data["mode"] = dialog_base["modes"][dialog_data["mode"]]

        dialog_base["tagsblocks"][dialog_data["tagsblock"]] = tostring(dialog_data["tagsblock"]) .. " (Viewing)"
        dialog_data["tagsblock"] = tostring(dialog_data["tagsblock"]) .. " (Viewing)"

        if #dialog_base["presets"] == 0 then
            dialog_base["presets"] = { "(No presets)" }
            dialog_data["preset"] = "(No presets)"
        end

        dialog = generate_dialog(dialog_base, act_data, dialog_data)
        if not dialog_base["help"] then
            buttons = { "&Apply", "View &Tags Block", "&Load Preset", "&Del. Pre.", "&Save As Pre.", "&Help / More", "Cancel" }
        else
            buttons = { "&Apply", "View &Tags Block", "&Load Preset", "&Delete Preset", "&Save As Preset", "Open From F&ile" ,"Sav&e To File", "Config", "Cancel" }
        end
        button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Cancel", no = "Cancel", cancel = "Cancel" }

        button, dialog_data = aegisub.dialog.display(dialog, buttons, button_ids)

        for i, v in ipairs(dialog_base["modes"]) do
            if v == dialog_data["mode"] then
                dialog_data["mode"] = i
                break
        end end

        for i, v in ipairs(dialog_base["tagsblocks"]) do
            match = re_tagsBlock_viewing:match(v)
            if match then
                dialog_base["tagsblocks"][i] = match[2]["str"]
                if dialog_data["tagsblock"] == v then
                    dialog_data["tagsblock"] = match[2]["str"]
                end
                break
        end end
        dialog_data["tagsblock"] = tonumber(dialog_data["tagsblock"])

        if dialog_base["presets"][1] and not presets[dialog_base["presets"][1]] then
            dialog_base["presets"][1] = nil
            dialog_data["preset"] = nil
        end

        dialog_data[""] = nil
        
        if button == false or button == "Cancel" then
            aegisub.cancel()
        elseif button == "&Apply" then
            dialog_data["preset"] = nil
            dialog_data["preset_new"] = nil

            local do_save = false
            for _, v in pairs(dialog_data) do
                if type(v) == "string" and v ~= "" then
                    do_save = true
                    break
            end end
            
            if do_save then
                presets["(Recall last)"] = dialog_data
                aconfig.write_config("aka.99PercentTags", "presets", presets)
                    :ifErr(function(msg)
                        aegisub.debug.out("[aka.99PercentTags] Error occurred when updating recall last:\n" .. msg) end)
            end

            return dialog_data, act_data
        elseif button == "View &Tags Block" then
            -- pass
        elseif button == "&Load Preset" then
            if dialog_data["preset"] then
                new_dialog_data = Table.copy(presets[dialog_data["preset"]])

                for k, v in pairs(dialog_data) do
                    if type(new_dialog_data[k]) == "nil" then
                        new_dialog_data[k] = v
                end end

                dialog_data = new_dialog_data
            end
        elseif (button == "&Del. Pre." or button == "&Delete Preset") or
               ((button == "&Save As Pre." or button == "&Save As Preset") and
                dialog_data["preset_new"] == "-") then
            if button == "&Save As Pre." or button == "&Save As Preset" then
                dialog_data["preset_new"] = ""
            end

            if dialog_data["preset"] then
                presets[dialog_data["preset"]] = nil
                aconfig.write_config("aka.99PercentTags", "presets", presets)
                    :ifErr(function(msg)
                        aegisub.debug.out("[aka.99PercentTags] Error occurred when updating presets:\n" .. msg) end)
                
                for i, v in ipairs(dialog_base["presets"]) do
                    if v == dialog_data["preset"] then
                        table.remove(dialog_base["presets"], i)
                        break
                end end
                dialog_data["preset"] = nil
                for _, v in pairs(dialog_base["presets"]) do
                    dialog_data["preset"] = v
                    break
                end
            end
        elseif button == "&Save As Pre." or button == "&Save As Preset" then
            if dialog_data["preset_new"] == "_" then
                dialog_data["preset_new"] = dialog_data["preset"]
            end

            while dialog_data["preset_new"] == "" do
                local dialog_2 = adialog.new({ width = 16 })
                                      :label_edit({ label = "Preset name:", name = "preset" })
                local buttons_2 = abuttons.ok("Save"):close("Back")
                local b, r = adisplay(dialog_2, buttons_2):resolve()
                if buttons_2:is_ok(b) then
                    dialog_data["preset_new"] = r["preset"]
                elseif buttons_2:is_close(b) then
                    break -- continue
            end end
    
            if dialog_data["preset_new"] ~= "" then
                presets[dialog_data["preset_new"]] = Table.copy(dialog_data)
                presets[dialog_data["preset_new"]]["preset"] = nil
                presets[dialog_data["preset_new"]]["preset_new"] = nil
                aconfig.write_config("aka.99PercentTags", "presets", presets)
                    :ifErr(function(msg)
                        aegisub.debug.out("[aka.99PercentTags] Error occurred when saving presets:\n" .. msg) end)
                    
                match = false
                for _, v in ipairs(dialog_base["presets"]) do
                    if v == dialog_data["preset_new"] then
                        match = true
                        break
                end end
                if not match then
                    table.insert(dialog_base["presets"], 1, dialog_data["preset_new"])
                end
                dialog_data["preset"] = dialog_data["preset_new"]
                dialog_data["preset_new"] = ""
            end
        elseif button == "&Help / More" then
            dialog_base["help"] = true
        elseif button == "Open From F&ile" then
            o(aegisub.dialog.open("Opening preset...", "", "", ""))
                :ifOk(function(path)
                    o(io.open(path, "r"))
                        :andThen(function(f)
                            local r
                            r = o(f:read("*a"))
                            f:close() return
                            r end)
                        :andThen(function(t) return
                            aconfig.json:decode3(t) end)
                        :ifOk(function(new_dialog_data)
                            for k, v in pairs(dialog_data) do
                                if type(new_dialog_data[k]) == "nil" then
                                    new_dialog_data[k] = v
                            end end
            
                            dialog_data = new_dialog_data end)
                        :ifErr(function(msg)
                            aegisub.debug.out("[aka.99PercentTags] Error occurred when opening preset:\n" .. msg) end) end)
        elseif button == "Sav&e To File" then
            o(aegisub.dialog.save("Saving preset...", "", "", ""))
                :ifOk(function(path)
                    o(io.open(path, "w"))
                        :andThen(function(f)
                            local to_save_dialog_data
                            local r

                            to_save_dialog_data = Table.copy(dialog_data)
                            to_save_dialog_data["preset"] = nil
                            to_save_dialog_data["preset_new"] = nil

                            r = o(aconfig.json:encode_pretty(to_save_dialog_data))
                                :andThen(function(d) return
                                    o(f:write(d)) end)
                            f:close() return
                            r end)
                        :ifErr(function(msg)
                            aegisub.debug.out("[aka.99PercentTags] Error occurred when saving preset:\n" .. msg) end) end)
        elseif button == "Config" then
            local dialog_2 = adialog.new({ width = 16 })
                                    :label_intedit({ label = "Preprocess textbox height:", name = "prepro_height", min = 2, max = 2147483647 })
                                    :load_data(dialog_config)
            local buttons_2 = abuttons.ok("Set"):close("Cancel")
            local b, r = adisplay(dialog_2, buttons_2):resolve()
            if buttons_2:is_ok(b) then
                dialog_config = r
                aconfig.write_config("aka.99PercentTags", "dialog", dialog_config)
                    :ifErr(function()
                        aegisub.debug.out("[aka.config] Failed to write config to file.\n")
                        aegisub.debug.out("[aka.config] " .. error .. "\n") end)
            elseif buttons_2:is_close(b) then
                -- continue
end end end end

dialog_aconfig = aconfig.make_editor({ display_name = "aka.99PercentTags/dialog",
                                      presets = { ["Default"] = { ["prepro_height"] = 5 } },
                                      default = "Default" })
generate_dialog = function(dialog_base, act_data, dialog_data)
    if not dialog_config then
        dialog_config = dialog_aconfig:read_and_validate_config_if_empty_then_default_or_else_edit_and_save("aka.99PercentTags", "dialog", function(config)
            if config["prepro_height"] == nil then
                config["prepro_height"] = 5
            elseif type(config["prepro_height"]) ~= "number" or config["prepro_height"] < 2 then return
                err("Invalid key \"prepro_height\".")
            end return
            ok(config) end)
            :ifErr(aegisub.cancel)
            :unwrap()
    end

    local name = 3
    local value = 2
    local arrow = 1
    local edit = 2
    local onefull = name + value + arrow + edit
    local twofull = 2 * onefull
    local threefull = 3 * onefull
    local help = 48

    local mode_text = 0
    local mode = 1
    local tagsBlock_text = 2
    local tagsBlock = 3
    local prepro_text = 4
    local prepro = 5
    local tags_text = 10 + dialog_config["prepro_height"] - 5 local prepro_next = tags_text
    local tags = 11 + dialog_config["prepro_height"] - 5
    local line_text = 26 + dialog_config["prepro_height"] - 5 local tags_next = line_text
    local layer = 27 + dialog_config["prepro_height"] - 5
    local preset_text = 29 + dialog_config["prepro_height"] - 5
    local preset = 30 + dialog_config["prepro_height"] - 5 local help_height = preset + 2 -- Why?

    local B
    local dialog
    local tag

    B = function(string)
        local return_string
        local codepoint

        return_string = ""
        for char in unicode.chars(string) do
            codepoint = unicode.codepoint(char)
            if 0x0041 <= codepoint and codepoint <= 0x005A then
                codepoint = codepoint + 0x1D593
            elseif 0x0061 <= codepoint and codepoint <= 0x007A then
                codepoint = codepoint + 0x1D58D
            elseif 0x0030 <= codepoint and codepoint <= 0x0039 then
                codepoint = codepoint + 0x1D7BC
            end
            return_string = return_string .. unicode.char(codepoint)
        end
        return return_string
    end


--[[
 0  Select mode:
 1  [ Generate data from active line once and apply to al... ]
 2  Select tags block:  
 3  [ 1 (Viewing)                                           ] 
 4  Preprocess tag data:
 5  [                                                        ]
 6  [                                                        ]
 7  [                                                        ]
 8  [                                                        ]
 9  Edit tag data:
10  an    5   [      ]  fn    Nunito          [              ]
11  posx  960 [      ]  fs    60  [      ]  cr    255 [      ]
12  posy  480 [      ]  fsp   0   [      ]  cg    255 [      ]
13  move2x -  [      ]  blur  0.5 [      ]  cb    255 [      ]
14  move2y -  [      ]  bord  2.5 [      ]  3cr   0   [      ]
15  orgx  960 [      ]  xbord 0   [      ]  3cg   0   [      ]
16  orgy  480 [      ]  ybord 0   [      ]  3cb   0   [      ]
17  frx   0   [      ]  shad  0   [      ]  4cr   0   [      ]
18  fry   0   [      ]  xshad 0   [      ]  4cg   0   [      ]
19  frz   0   [      ]  yshad 0   [      ]  4cb   0   [      ]
20  fax   0   [      ]  b     0   [      ]  alpha 255 [      ]
21  fay   0   [      ]  i     0   [      ]  1a    255 [      ]
22  fscx  100 [      ]  u     0   [      ]  3a    255 [      ]
23  fscy  100 [      ]  s     0   [      ]  4a    255 [      ]
24  q     0   [      ]  be    0   [      ]
25  Edit line data:
26  layer 0   [      ]  start [          ]  end   [          ]
27  Style [          ]  Actor [          ]  Effect [         ]
28  Load Preset:                 Save As Preset:
29  [           Last            ][                           ]
]]
    dialog = { { class = "label",                       x = 0, y = mode_text, width = threefull,
                                                        label = "Select mode:" },
               { class = "dropdown", name = "mode",     x = 0, y = mode, width = threefull,
                                                        items = dialog_base["modes"], value = dialog_data["mode"] },



               { class = "label",                       x = 0, y = tagsBlock_text, width = threefull,
                                                        label = "Select tags block:" },
               { class = "dropdown", name = "tagsblock", x = 0, y = tagsBlock, width = threefull,
                                                        items = dialog_base["tagsblocks"], value = dialog_data["tagsblock"] },



               { class = "label",                       x = 0, y = prepro_text, width = threefull,
    --                                                              U+2000 EN QUAD [ ]
                                                        label = "Preprocess data 🡢" },
               { class = "textbox", name = "prepro",    x = 0, y = prepro, width = threefull, height = tags_text - prepro,
                                                        text = dialog_data["prepro"] },
                                                
                                                
                                                
                { class = "label",                      x = 0, y = tags_text, width = threefull,
                                                        label = "Edit tag data:" } }

    for i = 1, tags_next - tags do
        tag = auto_dialog_tags[i]

        table.insert(dialog, { class = "label",         x = 0, y = tags + i - 1, width = name,
                                                        label = B(tag) })
        if (tag == "move2x" or tag == "move2y") and (not act_data[tag]) then
            table.insert(dialog, { class = "label",     x = name, y = tags + i - 1, width = value,
                                                        label = "-" })
        else
            table.insert(dialog, { class = "label",     x = name, y = tags + i - 1, width = value,
                                                        label = tostring(act_data[tag]) })
        end
        table.insert(dialog, { class = "label",         x = name + value, y = tags + i - 1, width = arrow,
                                                        label = "🡢" })
        table.insert(dialog, { class = "edit", name = tag, x = name + value + arrow, y = tags + i - 1, width = edit,
                                                        text = dialog_data[tag] })
    end

    table.insert(dialog, { class = "label",             x = onefull, y = tags, width = name,
                                                        label = B"fn" })
    table.insert(dialog, { class = "label",             x = onefull + name, y = tags, width = value + arrow + edit,
                                                        label = "\"" .. tostring(act_data["fn"]) .. "\"" })
    table.insert(dialog, { class = "label",             x = twofull, y = tags, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "fn", x = twofull + arrow, y = tags, width = onefull - arrow,
                                                        text = dialog_data["fn"] })
                            
    for i = tags_next - tags + 2, #auto_dialog_tags do
        tag = auto_dialog_tags[i]

        table.insert(dialog, { class = "label",         x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = name,
                                                        label = B(tag) })
        if tag == "cr" or tag == "cg" or tag == "cb" or
           tag == "3cr" or tag == "3cg" or tag == "3cb" or
           tag == "4cr" or tag == "4cg" or tag == "4cb" or
           tag == "alpha" or tag == "1a" or tag == "3a" or tag == "4a" then
            table.insert(dialog, { class = "label",         x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull + name, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = value,
                                                            label = string.format("0x%02X", act_data[tag]) })
        else
            table.insert(dialog, { class = "label",         x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull + name, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = value,
                                                            label = tostring(act_data[tag]) })
        end
        table.insert(dialog, { class = "label",         x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull + name + value, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = arrow,
                                                        label = "🡢" })
        table.insert(dialog, { class = "edit", name = tag, x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull + name + value + arrow, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = edit,
                                                        text = dialog_data[tag] })
    end
    


    table.insert(dialog, { class = "label",             x = 0, y = line_text, width = threefull,
                                                        label = "Edit line data:" })

    table.insert(dialog, { class = "label",             x = 0, y = layer, width = name,
                                                        label = B"layer" })
    table.insert(dialog, { class = "label",             x = name, y = layer, width = value,
                                                        label = tostring(act_data["layer"]) })
    table.insert(dialog, { class = "label",             x = name + value, y = layer, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "layer", x = name + value + arrow, y = layer, width = edit,
                                                        text = dialog_data["layer"] })
    table.insert(dialog, { class = "label",             x = onefull, y = layer, width = name,
                                                        label = B"start" })
    table.insert(dialog, { class = "label",             x = onefull + name, y = layer, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "start", x = onefull + name + arrow, y = layer, width = value + edit,
                                                        text = dialog_data["start"] })
    table.insert(dialog, { class = "label",             x = twofull, y = layer, width = name,
                                                        label = B"end_" })
    table.insert(dialog, { class = "label",             x = twofull + name, y = layer, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "end_", x = twofull + name + arrow, y = layer, width = value + edit,
                                                        text = dialog_data["end_"] })

    table.insert(dialog, { class = "label",             x = 0, y = layer + 1, width = name,
                                                        label = B"Style" })
    table.insert(dialog, { class = "label",             x = name, y = layer + 1, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "Style", x = name + arrow, y = layer + 1, width = value + edit,
                                                        text = dialog_data["Style"] })
    table.insert(dialog, { class = "label",             x = onefull, y = layer + 1, width = name,
                                                        label = B"Actor" })
    table.insert(dialog, { class = "label",             x = onefull + name, y = layer + 1, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "Actor", x = onefull + name + arrow, y = layer + 1, width = value + edit,
                                                        text = dialog_data["Actor"] })
    table.insert(dialog, { class = "label",             x = twofull, y = layer + 1, width = name,
                                                        label = B"Effect" })
    table.insert(dialog, { class = "label",             x = twofull + name, y = layer + 1, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "Effect", x = twofull + name + arrow, y = layer + 1, width = value + edit,
                                                        text = dialog_data["Effect"] })



    table.insert(dialog, { class = "label",             x = 0, y = preset_text, width = twofull - edit,
                                                        label = "Load or delete preset:" })
    table.insert(dialog, { class = "label",             x = twofull - edit, y = preset_text, width = onefull + edit,
                                                        label = "Save as preset:" })
    table.insert(dialog, { class = "dropdown", name = "preset", x = 0, y = preset, width = twofull - edit,
                                                        items = dialog_base["presets"], value = dialog_data["preset"] })
    table.insert(dialog, { class = "edit", name = "preset_new", x = twofull - edit, y = preset, width = onefull + edit,
                                                        text = dialog_data["preset_new"] })



    if dialog_base["help"] then
        table.insert(dialog, { class = "textbox",       x = threefull, y = 0, width = help, height = help_height,
                                                        text = [[
The interface of 99%Tags consists of six sections:
– Mode selector,
– Tags block selector,
– Preprocess data,
– Tag data editor,
– Line data editor,
– Preset editor.

To edit tags as in 𝗛𝗬𝗗𝗥𝗔, enter the value you want in the edit fields in tag and line data editor:
> fs  [ 50 ]
> fsp [ .1 ]
In above example, we set \fs to 50 and \fsp to 0.1.

You can switch between tags block using the tags block selector at the top:
> Select tags block [ 2 ]
You can click „View Tags Block“ button to see the tag values at the newly selected tags block.
> Select tags block [ 2 (Viewing) ]

Unlike HYDRA where the edit fields are limited to floating point numbers, edit fields in 99%Tags can be any Lua expressions.
> cr  [ 0b10000000 ]
> frz [ math.deg(math.pi / 2) ]
In above example, we set cr (the red channel of \c) to &H80& and \frz to `math.deg(math.pi / 2)` which equals to 90.
> fn  [ "Noto Sans Medium" ]
For fn, Style, Actor and Effect fields, a pair of quotation marks are required.

There are a lot of variables you can refer to in edit fields.
First, all tags and data listed in the tag and line data editor are variables under the same name.
> fscy [ fscx ]
> cr [ 0x100 - 3cr ]
In above exmaple, we set \fscy to match the current value of \fscx, and we set the red channel of \c to the opposite of the red channel of \3c. You may noticed that `3cr` shouldn't be valid Lua variables because Lua variables can't start with digits. For and only for the listed ASS tag names, 99%Tags will convert these identifiers before evaluation.

Second, there is a special variable `_` (one underscore) that represents the current tag itself.
> frz [ _ ]
> fax [ _ ]
In above example, we set \frz and \fax to its current value.

Note the mode selector at the top of the interface. which reads „Generate data from active line once and apply to all selected lines“. If we have multiple lines selected, setting tags to `_` essentially copys the value from active line to all selected lines like 𝗡𝗲𝗰𝗿𝗼𝘀𝗖𝗼𝗽𝘆.
> frz [ _ ]
> fax [ _ ]
In above example, provided that we have multiple lines selected and the mode set to „Generate data from active line once and apply to all selected lines“, we copy \frz and \fax value from active line to all selected lines.

The next natural thing with `_` is to do arithmetic operations like in 𝗥𝗲𝗰𝗮𝗹𝗰𝘂𝗹𝗮𝘁𝗼𝗿. Select mode to „Generate and apply data on each selected line respectively“ and enter expressions like `_+200`, or to add 200 to the current value. To make things simple, you can omit the first `_` and starts the expression with the operators like `+` or `*`.
> posx  [ +200 ]
In above example, we add 200 to posx (the x axis of \pos), shifting the sign to the right. `+200` is the same as `_+200`, as the first `_` in `_+200` is omited.
> posx  [ (_+200)*0.8 ]
In above example, we add 200 to posx and then multiply it by 0.8. Note that the first `_` in this case is not omittable because it is inside a pair of parentheses.

Caution! One consequence of allowing the first `_` to be omitted is that you can't assign negative values to tags. In order to set negative values, you need to write it as zero minus the value. This tradeoff is made because there are very few tags in ASS like \pos and \fax that allows negative values.
> fax [ 0-0.1 ]
In above example, we set \fax to `0-0.1`, or -0.1.

There is also a special case in edit fields. Setting edit field to `-` (one hyphen) removes the active tag and revert it to Style value. Depending on the situation, this may remove the tag or add the tag with the value of Style.
> bord  [ - ]
In above example, we set \bord to the value specified in Style.
> posx  [ - ]
For pairing tags like posx and posy (the x and y axis of \pos), removing one of the axis will only revert the axis to Style.
> orgx  [ - ]
For \org tags, removing one of the axis will revert the axis back to \pos instead of Style.
> move2x  [ - ]
For \move tags, removing one of the axis will set the axis to the axis' starting position. Removing both move2x and move2y will revert \move back to \pos.

At last, you can preprocess the data in the big text field above. Unlike edit fields of the tags, the preprocess field is for Lua commands instead of expressions. This allows us to do basic 𝗟𝘂𝗮𝗜𝗻𝘁𝗲𝗿𝗽𝗿𝗲𝘁 works.
The proprocess field shares the same envionment with all the tag fields. They execute in the following order:
– preprocess → an → posx → … → q → fn → fs → … → be → cr → … → 4a → layer → start → end → Style → Actor → Effect
If during the execution of a earlier field a tag has been modified, it will stay modified in the execution of later field.
> preprocess [ sw = fscx ]
> fscx [ fscy ]
> fscy [ sw ]
Because the fscy is below fscx, in this example, we assign fscx to a new variable named `sw`, we assign fscy to fscx and then assign sw to fscy, essentially swapping \fscx and \fscy value.

> preprocess [ sw = fscx ]
> preprocess [ fscx = fscy ]
> preprocess [ fscy = sw ]
> fscx [ _ ]
> fscy [ _ ]
You could, however, put every calculations in preprocess and put a `_` in edit fields of the tags to apply the changes. A tag modification will only be applied if there are expressions in the tag edit field.

If „Generate and apply data on each selected line respectively“ is used, all selected lines also share the same environment. All tag values will be reset when a new line is loaded in, but values defined in the preprocess field will be kept.
> preprocess [ l = l == nil and -1 or l ]
> preprocess [ l = l + 1 ]
> layer [ l ]
This set the layer of each selected line to incremental values starting from 0.

Additionally, line object after ILL's `Line.process()` is exposed under `line` and you may modify them directly.
> preprocess [ line.margin_l = 100 ]
In this example, we set left margin of selected lines to 100.

At the bottom of the UI, you can load, delete, or save your modifications as presets, or recall last, using „Load Preset“, „Delete Preset“ and „Save As Preset“ buttons.

The „Save as preset“ edit field recognises two special cases, `_` and `-`. They are triggered when pressing the „Save As Preset“ button. The special cases here are different than the special cases of the tag edit fields.
Using `_`, you can overwrite the preset that's currently selected in the „Load or delete preset“ dropdown selector, even if it isn't the one that's currently loaded. This is the same as typing out the full name of the preset you want to overwrite.
Using `-` in „Save as preset“ edit field and pressing „Save As Preset“ button is the same as pressing „Delete Preset“ button alone.

You can save and share 99%Tags operations using „Save To File“ and „Open From File“ button. These two buttons are only visible after pressing „Help / More“ button.]] })
    end

    return dialog
end



apply_data = function(ass, sub, act, data, act_data)
    local commands
    local operations
    local line
    local style_data
    local original_data
    local line_data
    local tagsBlocks

    commands, operations = process_data(data)

    line = sub[act]
    line.text = ""
    style_data = {}
    Line.process(ass, line)
    parse_tags(style_data, line.data)

    if data["mode"] == 1 then
        execute_tags(commands, act_data)
        for line, s, i, n in ass:iterSel(false) do
            ass:progressLine(s, i, n)
            -- Internal ILL variable; May break
            line.isShape = false
            line_data = {}
            tagsBlocks = Line.tagsBlocks(ass, line, false)
            parse_tags(line_data, tagsBlocks[data["tagsblock"]].data)

            if tagsBlocks[data["tagsblock"]] then
                apply_tags(operations, line, line.text.tagsBlocks, data["tagsblock"], act_data, line_data, style_data)

                ass:setLine(line, s)
            else
                aegisub.debug.out("[aka.99PercentTags] Skipping line " .. tostring(s) .. " because line " .. tostring(s) .. " does not have tags block " .. tostring(data["tagsblock"]) .. "\n")
        end end
    else
        line_data = {}
        for line, s, i, n in ass:iterSel(false) do
            ass:progressLine(s, i, n)
            -- Internal ILL variable; May break
            line.isShape = false
            tagsBlocks = Line.tagsBlocks(ass, line, false)
            parse_tags(line_data, tagsBlocks[data["tagsblock"]].data)
            parse_other_data(line_data, line, tagsBlocks.width, tagsBlocks.height)

            original_data = Table.copy(line_data)
            execute_tags(commands, line_data)
            if tagsBlocks[data["tagsblock"]] then
                apply_tags(operations, line, line.text.tagsBlocks, data["tagsblock"], line_data, original_data, style_data)
                
                ass:setLine(line, s)
            else
                aegisub.debug.out("[aka.99PercentTags] Skipping line " .. tostring(s) .. " because line " .. tostring(s) .. " does not have tags block " .. tostring(data["tagsblock"]) .. "\n")
        end end
    end
end

re_extra_spaces = re.compile([[^ *(.+?) *$]], re.NO_MOD_M)
re_if_omitted = re.compile([[^(?:(?:\+|\-|\*|\/|%|\^|==|~=|<|>|<=|>=|\.\.)[^\+\-\*\/%\^=~<>\.]|and |or )]], re.NO_MOD_M)
re_match_underscore = re.compile([[^(.*[^\w]|)_([^\w].*|)$]], re.NO_MOD_M)
re_match_invalid_varnames = re.compile([[^((?:[^"']*(?:"(?:[^"]*(?<!\\)(?:\\\\)*\\")*?[^"]*(?<!\\)(?:\\\\)*"|'(?:[^']*(?<!\\)(?:\\\\)*\\')*?[^']*(?<!\\)(?:\\\\)*'))*(?:[^"']*[^\w"']|)|)(3cr|3cg|3cb|4cr|4cg|4cb|1a|2a|3a|4a)([^\w].*|)$]], re.NO_MOD_M)
process_data = function(data)
    local commands
    local operations
    local command
    local match

    operations = {}

    match = re_extra_spaces:match(data["prepro"])
    if match then
        command = match[2]["str"]

        while true do
            match = re_match_invalid_varnames:match(command)
            if match then
                command = match[2]["str"] .. "_G[\"" .. match[3]["str"] .. "\"]" .. match[4]["str"]
            else
                break
        end end

        commands = commands and (commands .. "\n" .. command) or command
    end 

    for _, tag in ipairs(eval_tags) do
        match = re_extra_spaces:match(data[tag])
        if match then
            command = match[2]["str"]

            if command == "-" then
                table.insert(operations, { "Clear", tag })
            elseif command == "_" then
                table.insert(operations, { "Set", tag })
            else
                if re_if_omitted:find(command) then
                    command = tag .. " " .. command
                end

                while true do
                    match = re_match_underscore:match(command)
                    if match then
                        command = match[2]["str"] .. tag .. match[3]["str"]
                    else
                        break
                end end

                command = tag .. " = " .. command

                while true do
                    match = re_match_invalid_varnames:match(command)
                    if match then
                        command = match[2]["str"] .. "_G[\"" .. match[3]["str"] .. "\"]" .. match[4]["str"]
                    else
                        break
                end end

                commands = commands and (commands .. "\n" .. command) or command
                table.insert(operations, { "Set", tag })
    end end end

    return commands, operations
end

re_clean_traceback = re.compile[[(.*?)(?:\([0-9]+\) Lua upvalue '_ao_xpcall')]]
execute_tags = function(commands, line_data)
    local run

    if commands then
        line_data._G = line_data
        setmetatable(line_data, { __index = _G })
        run = o(loadstring(commands))
            :ifErr(function(err)
                aegisub.debug.out("[aka.99PercentTags] Invalid Lua commands or expressions\n")
                aegisub.debug.out("[aka.99PercentTags] The following commands are collected from dialog and fed to loadstring():\n")
                aegisub.debug.out(commands .. "\n")
                aegisub.debug.out("[aka.99PercentTags] The following error occurs during loadstring():\n")
                aegisub.debug.out(err .. "\n")
                aegisub.cancel() end)
            :unwrap()
        setfenv(run, line_data)
        _ao_xpcall(run, function(err)
            local traceback
            local match
            aegisub.debug.out("[aka.99PercentTags] Error during command execution\n")
            aegisub.debug.out("[aka.99PercentTags] The following commands are collected from dialog and executed:\n")
            aegisub.debug.out(commands .. "\n")
            aegisub.debug.out("[aka.99PercentTags] The following error occurs:\n")
            traceback = debug.traceback(err)
            match = re_clean_traceback:match(traceback)
            if match then
                traceback = match[2]["str"]
            end
            aegisub.debug.out(traceback) end)
            :ifErr(aegisub.cancel)
end end

apply_tags = function(operations, line, tagsBlocks, i, data, original_data, style_data)
    local single_find
    local deep_find
    local messy_set
    local ch

    single_find = function(table, value)
        for _, v in ipairs(table) do
            if value == v then return v end
        end
        for k, _ in pairs(table) do
            if value == k then return k end
    end end
    deep_find = function(table, value)
        for k, v in pairs(table) do
            for j, w in ipairs(v) do
                if value == w then return { k, j } end
    end end end

    -- some():  Set
    -- none():  Clear
    -- nil:     Original
    messy_set = {}

    for _, v in ipairs(operations) do
        o(single_find(single_tagsBlock_tags, v[2]))
            :ifOk(function(tag)
                if v[1] == "Set" then
                    tagsBlocks[i]:insert({ { tag, data[tag] } })

                elseif v[1] == "Clear" then
                    if i == 1 then
                        tagsBlocks[1]:remove(tag)
                    else
                        ch = false
                        for j = i, 1, -1 do
                            if tagsBlocks[j]:existsTag(tag) then
                                tagsBlocks[i]:insert({ { tag, style_data[tag] } })
                                ch = true
                        end end
                        if not ch then
                            tagsBlocks[i]:remove(tag)
                end end end end)

            :orElseOther(function() return
                o(single_find(alpha_tags, v[2]))
                    :ifOk(function(tag)
                        if v[1] == "Set" then
                            tagsBlocks[i]:insert({ { tag, autil.ass_alpha(data[tag]) } })

                        elseif v[1] == "Clear" then
                            if i == 1 then
                                tagsBlocks[1]:remove(tag)
                            else
                                ch = false
                                for j = i, 1, -1 do
                                    if tagsBlocks[j]:existsTag(tag) then
                                        tagsBlocks[i]:insert({ { tag, autil.ass_alpha(style_data[tag]) } })
                                        ch = true
                                end end
                                if not ch then
                                    tagsBlocks[i]:remove(tag)
                        end end end end) end)

            :orElseOther(function() return
                o(v[2] == "an")
                    :ifOk(function(tag)
                        for _, b in ipairs(tagsBlocks) do
                            b:remove("an")
                        end
                        if v[1] == "Set" then
                            tagsBlocks[1]:insert({ { "an", data["an"] } })
                        end end) end)

            :orElseOther(function()
                for j, w in ipairs(move_tags) do
                    if v[2] == w then
                        if not messy_set["move"] then
                            messy_set["move"] = {}
                        end

                        if v[1] == "Set" then
                            messy_set["move"][j] = some(data[v[2]])
                        elseif v[1] == "Clear" then
                            messy_set["move"][j] = none()
                        end
                        return
                        ok()
                end end return
                err() end)

            :orElseOther(function()
                for j, w in ipairs(org_tags) do
                    if v[2] == w then
                        if not messy_set["org"] then
                            messy_set["org"] = {}
                        end

                        if v[1] == "Set" then
                            messy_set["org"][j] = some(data[v[2]])
                        elseif v[1] == "Clear" then
                            messy_set["org"][j] = none()
                        end
                        return
                        ok()
                end end return
                err() end)

            :orElseOther(function() return
                o(deep_find(colour_tags, v[2]))
                    :ifOk(function(tj)
                        local tag
                        local j
                        
                        tag, j = table.unpack(tj)
                        if not messy_set[tag] then
                            messy_set[tag] = {}
                        end
                        
                        if v[1] == "Set" then
                            messy_set[tag][j] = some(data[v[2]])
                        elseif v[1] == "Clear" then
                            messy_set[tag][j] = none()
                        end end) end)

            :orElseOther(function()
                if v[2] == "layer" then
                    if v[1] == "Set" then
                        line.layer = data["layer"]
                    elseif v[1] == "Clear" then
                        line.layer = 0
                    end
                elseif v[2] == "start" then
                    if v[1] == "Set" then
                        line.start_time = data["start"]
                    elseif v[1] == "Clear" then
                        aegisub.debug.out("[aka.99PercentTags] Skipping settings line start time to \"-\"\n")
                    end
                elseif v[2] == "end_" then
                    if v[1] == "Set" then
                        line.end_time = data["end_"]
                    elseif v[1] == "Clear" then
                        aegisub.debug.out("[aka.99PercentTags] Skipping settings line end time to \"-\"\n")
                    end
                elseif v[2] == "Style" then
                    if v[1] == "Set" then
                        line.style = data["Style"]
                    elseif v[1] == "Clear" then
                        aegisub.debug.out("[aka.99PercentTags] Skipping settings line Style to \"-\"\n")
                    end
                elseif v[2] == "Actor" then
                    if v[1] == "Set" then
                        line.actor = data["Actor"]
                    elseif v[1] == "Clear" then
                        line.actor = ""
                    end
                elseif v[2] == "Effect" then
                    if v[1] == "Set" then
                        line.effect = data["Effect"]
                    elseif v[1] == "Clear" then
                        line.effect = ""
                    end
                else return
                    err()
                end return
                ok() end)

            :unwrap()
    end
    

    for tag, tag_data in pairs(messy_set) do
        if tag == "move" then
            if (tag_data[3] and tag_data[3]:isNone() and tag_data[4] and tag_data[4]:isNone()) or
               (not tag_data[3] and not original_data[move_tags[3]] and not tag_data[4] and not original_data[move_tags[4]]) then
                for _, b in ipairs(tagsBlocks) do
                    b:remove("pos")
                    b:remove("move")
                end
                
                if tag_data[1] and tag_data[1]:isNone() and tag_data[2] and tag_data[2]:isNone() then
                    messy_set["move"] = { style_data[move_tags[1]], style_data[move_tags[2]] } -- This is for messy_set["org"] below
                else
                    for j = 1, 2 do
                        if not tag_data[j] then
                            tag_data[j] = original_data[move_tags[j]]
                        elseif tag_data[j]:isSome() then
                            tag_data[j] = tag_data[j]:unwrap()
                        elseif tag_data[j]:isNone() then
                            tag_data[j] = style_data[move_tags[j]]
                    end end
                    tagsBlocks[1]:insert({ { "pos", { tag_data[1], tag_data[2] } } })
                end
            else
                for _, b in ipairs(tagsBlocks) do
                    b:remove("pos")
                    b:remove("move")
                end

                if tag_data[1] and tag_data[1]:isNone() and tag_data[2] and tag_data[2]:isNone() and
                   tag_data[3] and tag_data[3]:isNone() and tag_data[4] and tag_data[4]:isNone() then
                    messy_set["move"] = { style_data[move_tags[1]], style_data[move_tags[2]] }
                else
                    for j = 1, 2 do
                        if not tag_data[j] then
                            tag_data[j] = original_data[move_tags[j]]
                        elseif tag_data[j]:isSome() then
                            tag_data[j] = tag_data[j]:unwrap()
                        elseif tag_data[j]:isNone() then
                            tag_data[j] = style_data[move_tags[j]]
                    end end
                    for j = 3, 4 do
                        if not tag_data[j] then
                            if original_data[move_tags[j]] then
                                tag_data[j] = original_data[move_tags[j]]
                            else
                                tag_data[j] = tag_data[j-2]
                            end
                        elseif tag_data[j]:isSome() then
                            tag_data[j] = tag_data[j]:unwrap()
                        elseif tag_data[j]:isNone() then
                            tag_data[j] = tag_data[j-2]
                    end end
                    tagsBlocks[1]:insert({ { "move", { tag_data[1], tag_data[2], tag_data[3], tag_data[4] } } })
            end end

        elseif single_find(colour_tags, tag) then
            ch = false
            if tag_data[1] and tag_data[1]:isNone() and tag_data[2] and tag_data[2]:isNone() and tag_data[3] and tag_data[3]:isNone() then
                ch = true
                for j = i - 1, 1, -1 do
                    if tagsBlocks[j]:existsTag(tag) then
                        ch = false
                end end
                if ch then
                    tagsBlocks[i]:remove(tag)
            end end
            
            if not ch then
                for j = 1, 3 do
                    if not tag_data[j] then
                        tag_data[j] = original_data[colour_tags[tag][j]]
                    elseif tag_data[j]:isSome() then
                        tag_data[j] = tag_data[j]:unwrap()
                    elseif tag_data[j]:isNone() then
                        tag_data[j] = style_data[colour_tags[tag][j]]
                end end
                tagsBlocks[i]:insert({ { tag, autil.ass_color(tag_data[1], tag_data[2], tag_data[3]) } })
    end end end

    if messy_set["org"] then
        for _, b in ipairs(tagsBlocks) do
            b:remove("org")
        end

        if not (messy_set["org"][1] and messy_set["org"][1]:isNone() and messy_set["org"][2] and messy_set["org"][2]:isNone()) then
            for j = 1, 2 do
                if not messy_set["org"][j] then
                    messy_set["org"][j] = messy_set["move"] and messy_set["move"][j] or original_data[org_tags[j]]
                elseif messy_set["org"][j]:isSome() then
                    messy_set["org"][j] = messy_set["org"][j]:unwrap()
                elseif messy_set["org"][j]:isNone() then
                    messy_set["org"][j] = style_data[org_tags[j]]
            end end
            tagsBlocks[1]:insert({ { "org", { messy_set["org"][1], messy_set["org"][2] } } })
end end end



DepCtrl:registerMacros({
    { "99%Tags", "Add or modify tags on selected lines", function(sub, sel, act) main(sub, sel, act, 1) end, nil, nil, false },
    { "99%Tags (open in Recalculator mode)", "Add or modify tags on selected lines", function(sub, sel, act) main(sub, sel, act, 2) end, nil, nil, false }
})
