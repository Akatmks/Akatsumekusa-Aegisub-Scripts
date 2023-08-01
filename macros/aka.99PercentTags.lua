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

versioning.name = "99% Tags"
versioning.description = "Add or modify tags on selected lines"
versioning.version = "0.1.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.99PercentTags"

versioning.requireModules = "[{ \"moduleName\": \"aka.config2\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"ILL.ILL\" }, { \"moduleName\": \"aegisub.util\" }, { \"moduleName\": \"aegisub.re\" }, { \"moduleName\": \"aka.unicode\" }]"

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
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
        {
            { "aka.config2" },
            { "aka.outcome" },
            { "ILL.ILL" },
            { "aegisub.util" },
            { "aegisub.re" },
            { "aka.unicode" }
        }
    })
    DepCtrl:requireModules()
end
local aconfig = require("aka.config2")
local outcome = require("aka.outcome")
local ok, err = outcome.ok, outcome.err
local ILL = require("ILL.ILL")
local Ass, Line, Table = ILL.Ass, ILL.Line, ILL.Table
local autil = require("aegisub.util")
local re = require("aegisub.re")
local unicode = require("aka.unicode")



local all_tags
local single_tags
local alpha_tags
local double_tags
local colour_tags
local move_tags
local auto_dialog_tags
local parse_tags
local parse_other_data

local main
local re_tagsBlock_selected
local show_dialog
local generate_dialog





--[[
Select mode:
[ Generate data from active line once and apply to all s ]
Edit line data:
layer 0   [      ]  start [          ]  end   [          ]
Style [          ]  Actor [          ]  Effect [         ]
Select tags block:
TagsBlock           [       1        ]
Preprocess tag data:
[                                                        ]
[                                                        ]
[                                                        ]
[                                                        ]
Edit tag data:
an    5   [      ]  fn    Nunito          [              ]
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
Load Preset                  Save As Preset
[           Last            ][                           ]
]]
all_tags = { "layer", "start", "end",
             "Style", "Actor", "Effect",
             "prepro",
             "an", "posx", "posy", "move2x", "move2y", "orgx", "orgy", "frx", "fry", "frz", "fax", "fay", "fscx", "fscy", "q",
             "fn", "fs", "fsp", "blur", "bord", "xbord", "ybord", "shad", "xshad", "yshad", "b", "i", "u", "s", "be",
             "cr", "cg", "cb", "3cr", "3cg", "3cb", "4cr", "4cg", "4cb", "alpha", "1a", "3a", "4a" }
single_tags = { "an", "frx", "fry", "frz", "fax", "fay", "fscx", "fscy",
                "fn", "fs", "fsp", "blur", "bord", "xbord", "ybord", "shad", "xshad", "yshad", "b", "i", "u", "s", "q", "be" }
alpha_tags = { "alpha", "1a", "3a", "4a" }
double_tags = { ["pos"] = { "posx", "posy" }, ["org"] = { "orgx", "orgy" } }
colour_tags = { ["c"] = { "cr", "cg", "cb" }, ["3c"] = { "3cr", "3cg", "3cb" }, ["4c"] = { "4cr", "4cg", "4cb" } }
move_tags = { "posx", "posy", "move2x", "move2y" }
auto_dialog_tags = { "an", "posx", "posy", "move2x", "move2y", "orgx", "orgy", "frx", "fry", "frz", "fax", "fay", "fscx", "fscy", "q",
                     "fn", "fs", "fsp", "blur", "bord", "xbord", "ybord", "shad", "xshad", "yshad", "b", "i", "u", "s", "be",
                     "cr", "cg", "cb", "3cr", "3cg", "3cb", "4cr", "4cg", "4cb", "alpha", "1a", "3a", "4a" }

parse_tags = function(data, line, ILL_data)
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
    for _, tag in ipairs(alpha_tags) do
        _, _, _, data[tag] = autil.extract_color(ILL_data_tag(ILL_data, tag))
    end
    for tag, names in pairs(double_tags) do
        data[names[1]], data[names[2]] = table.unpack(ILL_data_tag(ILL_data, tag))
    end
    for tag, names in pairs(colour_tags) do
        data[names[1]], data[names[2]], data[names[3]], _ = autil.extract_color(ILL_data_tag(ILL_data, tag))
    end
    if ILL_data_tag(ILL_data, "move") then
        _, _, data[move_tags[3]], data[move_tags[4]], _, _ = table.unpack(ILL_data_tag(ILL_data, "move"))
    end
end
parse_other_data = function(data, line, width, height)
    data["layer"] = line.layer
    data["start"] = line.start_time
    data["end"] = line.end_time
    data["Style"] = line.style
    data["Actor"] = line.actor
    data["Effect"] = line.effect

    -- data["line"] = line
    data["width"] = width
    data["height"] = height
end



logger = DepCtrl:getLogger() -- TODO
dumper = logger -- TODO
main = function(sub, sel, act)
    local ass
    
    ass = Ass(sub, sel, act)

    dumper:dump(show_dialog(ass, sub, act))
end

--                                  (\d+) \(Selected\)
re_tagsBlock_selected = re.compile("(\\d+) \\(Selected\\)")
show_dialog = function(ass, sub, act)
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
                             "Generate data from each selected line and apply respectively" }
    dialog_data["mode"] = 1

    for _, v in ipairs(all_tags) do
        dialog_data[v] = ""
    end

    act_l = sub[act]
    act_tagsBlocks = Line.tagsBlocks(ass, act_l)
    dialog_base["tagsblocks"] = {}
    for i, _ in ipairs(act_tagsBlocks) do
        dialog_base["tagsblocks"][i] = tostring(i)
    end
    dialog_data["tagsblock"] = 1

    presets = aconfig.read_config("aka.99PercentTags")
        :andThen(function(config)
            if type(config) ~= "table" then
                return err("[aka.99PercentTags] Error")
            end
            for k, v in pairs(config) do
                if type(v) ~= "table" then
                    config[k] = nil
            end end
            return ok(config) end)
        :orElseOther(function()
            aconfig.write_config("aka.99PercentTags", {})
            return ok({}) end)
        :unwrap()
    dialog_base["presets"] = {}
    for k, _ in pairs(presets) do
        table.insert(dialog_base["presets"], k)
    end
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
        parse_tags(act_data, act_l, act_tagsBlocks[dialog_data["tagsblock"]].data)

        dialog_data["mode"] = dialog_base["modes"][dialog_data["mode"]]

        dialog_base["tagsblocks"][dialog_data["tagsblock"]] = tostring(dialog_data["tagsblock"]) .. " (Selected)"
        dialog_data["tagsblock"] = tostring(dialog_data["tagsblock"]) .. " (Selected)"

        if #dialog_base["presets"] == 0 then
            dialog_base["presets"] = { "(No presets)" }
            dialog_data["preset"] = "(No presets)"
        end

        dialog = generate_dialog(dialog_base, act_data, dialog_data)
        buttons = { "&Apply", "Select &Tags Block", "&Load Pre.", "&Del. Pre.", "&Save As Pre.", "&Help", "Cancel" }
        button_ids = { ok = "&Apply", yes = "&Apply", save = "&Apply", apply = "&Apply", close = "Cancel", no = "Cancel", cancel = "Cancel" }

        button, dialog_data = aegisub.dialog.display(dialog, buttons, button_ids)

        for i, v in ipairs(dialog_base["modes"]) do
            if v == dialog_data["mode"] then
                dialog_data["mode"] = i
            end
            break
        end

        for i, v in ipairs(dialog_base["tagsblocks"]) do
            match = re_tagsBlock_selected:match(v)
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
        
        if button == false or button == "Cancel" then
            aegisub.cancel()
        elseif button == "&Apply" then
            dialog_data["preset"] = nil
            dialog_data["preset_new"] = nil
            presets["(Recall last)"] = dialog_data
            aconfig.write_config("aka.99PercentTags", presets)

            return dialog_data
        elseif button == "Select &Tags Block" then
            -- pass
        elseif button == "&Load Pre." then
            new_dialog_data = Table.copy(presets[dialog_data["preset"]])

            for k, v in pairs(dialog_data) do
                if type(new_dialog_data[k]) == "nil" then
                    new_dialog_data[k] = v
            end end

            dialog_data = new_dialog_data
        elseif button == "&Del. Pre." then
            presets[dialog_data["preset"]] = nil
            aconfig.write_config("aka.99PercentTags", presets)
            
            for k, _ in pairs(presets) do
                dialog_data["preset"] = k
                break
            end
        elseif button == "&Save As Pre." then
            presets[dialog_data["preset_new"]] = Table.copy(dialog_data)
            presets[dialog_data["preset_new"]]["preset"] = nil
            presets[dialog_data["preset_new"]]["preset_new"] = nil
            aconfig.write_config("aka.99PercentTags", presets)
        elseif button == "&Help" then
            dialog_base["help"] = true
end end end

generate_dialog = function(dialog_base, act_data, dialog_data)
    local name = 3
    local value = 2
    local arrow = 1
    local edit = 2
    local onefull = name + value + arrow + edit
    local twofull = 2 * onefull
    local threefull = 3 * onefull
    local help = 18

    local mode_text = 0
    local mode = 1
    local line_text = 2
    local layer = 3
    local tagsBlock_text = 5
    local tagsBlock = 6
    local prepro_text = 7
    local prepro = 8
    local tags_text = 13 local prepro_next = tags_text
    local tags = 14
    local preset_text = 29 local tags_next = preset_text
    local preset = 30 local help_height = preset

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
 1  [ Generate data from active line once and apply to all s ]
 2  Edit line data:
 3  layer 0   [      ]  start [          ]  end   [          ]
 4  Style [          ]  Actor [          ]  Effect [         ]
 5  Select tags block:
 6  TagsBlock           [       1        ]
 7  Preprocess tag data:
 8  [                                                        ]
 9  [                                                        ]
10  [                                                        ]
11  [                                                        ]
12  Edit tag data:
13  an    5   [      ]  fn    Nunito          [              ]
14  posx  960 [      ]  fs    60  [      ]  cr    255 [      ]
15  posy  480 [      ]  fsp   0   [      ]  cg    255 [      ]
16  move2x -  [      ]  blur  0.5 [      ]  cb    255 [      ]
17  move2y -  [      ]  bord  2.5 [      ]  3cr   0   [      ]
18  orgx  960 [      ]  xbord 0   [      ]  3cg   0   [      ]
19  orgy  480 [      ]  ybord 0   [      ]  3cb   0   [      ]
20  frx   0   [      ]  shad  0   [      ]  4cr   0   [      ]
21  fry   0   [      ]  xshad 0   [      ]  4cg   0   [      ]
22  frz   0   [      ]  yshad 0   [      ]  4cb   0   [      ]
23  fax   0   [      ]  b     0   [      ]  alpha 255 [      ]
24  fay   0   [      ]  i     0   [      ]  1a    255 [      ]
25  fscx  100 [      ]  u     0   [      ]  3a    255 [      ]
26  fscy  100 [      ]  s     0   [      ]  4a    255 [      ]
27  q     0   [      ]  be    0   [      ]
28  Load preset                  Save as preset
29  [           Last            ][                           ]
]]
    dialog = { { class = "label",                       x = 0, y = mode_text, width = threefull,
                                                        label = "Select mode:" },
               { class = "dropdown", name = "mode",     x = 0, y = mode, width = threefull,
                                                        items = dialog_base["modes"], value = dialog_data["mode"] },



               { class = "label",                       x = 0, y = line_text, width = threefull,
                                                        label = "Edit line data:" },

               { class = "label",                       x = 0, y = layer, width = name,
                                                        label = B"layer" },
               { class = "label",                       x = name, y = layer, width = value,
                                                        label = tostring(act_data["layer"]) },
               { class = "label",                       x = name + value, y = layer, width = arrow,
                                                        label = "🡢" },
               { class = "edit", name = "layer",        x = name + value + arrow, y = layer, width = edit,
                                                        text = dialog_data["layer"] },
               { class = "label",                       x = onefull, y = layer, width = name,
                                                        label = B"start" },
               { class = "label",                       x = onefull + name, y = layer, width = arrow,
                                                        label = "🡢" },
               { class = "edit", name = "start",        x = onefull + name + arrow, y = layer, width = value + edit,
                                                        text = dialog_data["start"] },
               { class = "label",                       x = twofull, y = layer, width = name,
                                                        label = B"end" },
               { class = "label",                       x = twofull + name, y = layer, width = arrow,
                                                        label = "🡢" },
               { class = "edit", name = "end",          x = twofull + name + arrow, y = layer, width = value + edit,
                                                        text = dialog_data["end"] },

               { class = "label",                       x = 0, y = layer + 1, width = name,
                                                        label = B"Style" },
               { class = "label",                       x = name, y = layer + 1, width = arrow,
                                                        label = "🡢" },
               { class = "edit", name = "Style",        x = name + arrow, y = layer + 1, width = value + edit,
                                                        text = dialog_data["Style"] },
               { class = "label",                       x = onefull, y = layer + 1, width = name,
                                                        label = B"Actor" },
               { class = "label",                       x = onefull + name, y = layer + 1, width = arrow,
                                                        label = "🡢" },
               { class = "edit", name = "Actor",        x = onefull + name + arrow, y = layer + 1, width = value + edit,
                                                        text = dialog_data["Actor"] },
               { class = "label",                       x = twofull, y = layer + 1, width = name,
                                                        label = B"Effect" },
               { class = "label",                       x = twofull + name, y = layer + 1, width = arrow,
                                                        label = "🡢" },
               { class = "edit", name = "Effect",       x = twofull + name + arrow, y = layer + 1, width = value + edit,
                                                        text = dialog_data["Effect"] },


                                                    
               { class = "label",                       x = 0, y = tagsBlock_text, width = threefull,
                                                        label = "Select tags block:" },
               { class = "dropdown", name = "tagsblock", x = 0, y = tagsBlock, width = threefull,
                                                        items = dialog_base["tagsblocks"], value = dialog_data["tagsblock"] },



               { class = "label",                       x = 0, y = prepro_text, width = threefull,
    --                                                              U+2000 EN QUAD [ ]
                                                        label = "Preprocess tag data 🡢" },
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
                                                        label = tostring(act_data["fn"]) })
    table.insert(dialog, { class = "label",             x = twofull, y = tags, width = arrow,
                                                        label = "🡢" })
    table.insert(dialog, { class = "edit", name = "fn", x = twofull + arrow, y = tags, width = onefull - arrow,
                                                        text = dialog_data["fn"] })

    for i = tags_next - tags + 2, #auto_dialog_tags do
        tag = auto_dialog_tags[i]

        table.insert(dialog, { class = "label",         x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = name,
                                                        label = B(tag) })
        table.insert(dialog, { class = "label",         x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull + name, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = value,
                                                        label = tostring(act_data[tag]) })
        table.insert(dialog, { class = "label",         x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull + name + value, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = arrow,
                                                        label = "🡢" })
        table.insert(dialog, { class = "edit", name = tag, x = math.floor((i - 3) / (tags_next - tags - 1)) * onefull + name + value + arrow, y = tags + 1 + math.fmod((i - 3), tags_next - tags - 1), width = edit,
                                                        text = dialog_data[tag] })
    end



    table.insert(dialog, { class = "label",             x = 0, y = preset_text, width = twofull - edit,
                                                        label = "Load or delete preset" })
    table.insert(dialog, { class = "label",             x = twofull - edit, y = preset_text, width = onefull + edit,
                                                        label = "Save as preset" })
    table.insert(dialog, { class = "dropdown", name = "preset", x = 0, y = preset, width = twofull - edit,
                                                        items = dialog_base["presets"], value = dialog_data["preset"] })
    table.insert(dialog, { class = "edit", name = "preset_new", x = twofull - edit, y = preset, width = onefull + edit,
                                                        text = dialog_data["preset_new"] })



    for i, tag in ipairs(auto_dialog_tags) do
    end
    if dialog_data["help"] then
        table.insert(dialog, { class = "edit",          x = threefull, y = 0, width = help, height = help_height,
                                                        text = [[]] })
    end


    return dialog
end


if hasDepCtrl then
    DepCtrl:registerMacro(main)
else
    aegisub.register_macro("99% Tags", "Add or modify tags on selected lines", main)
end
