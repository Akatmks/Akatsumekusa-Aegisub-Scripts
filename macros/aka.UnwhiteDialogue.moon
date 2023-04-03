-- aka.UnwhiteDialogue.lua
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

versioning =
    name: "UnwhiteDialogue"
    description: "Automatically select shade and unwhite the dialogues"
    version: "0.0.3"
    author: "Akatsumekusa and contributors"
    namespace: "aka.UnwhiteDialogue"
    requireModules: "[{ \"moduleName\": \"aka.config\" }, { \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"aka.unwhite_dialogue\" }]"

if hasDepCtrl
    DepCtrl = DepCtrl {
        name: versioning.name,
        description: versioning.description,
        version: versioning.version,
        author: versioning.author,
        moduleName: versioning.namespace,
        url: "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed: "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/dev/DependencyControl.json",
        {
            { "aka.config" },
            { "aka.outcome" },
            { "ILL.ILL" },
            { "aka.unwhite_dialogue" }
        }
    }
    DepCtrl\requireModules!

config = with require "aka.config"
    .make_editor
        display_name: "UnwhiteDialogue"
        width: 48
        height: 30
        presets:
            "Experimental":
                scenecut:
                    exec: "return L"
                    eval: "return diff > 60"
                colours:
                    exec: "return L + C * 0.08"
                    [1]:
                        eval: "return param <= 55"
                        style: "Default"
                    [2]:
                        exec: "return param > 55"
                        style: "Default - Dark"
        default:
            "Experimental"
with require "aka.outcome"
    ok, err = .ok, .err
import Ass from require "ILL.ILL"
unwhite_dialogue = with require "aka.unwhite_dialogue"
    .workflow

config = nil

main = (sub, sel, act) ->
    unless config
        config = with config\read_and_validate_config_or_else_edit_and_save "aka.UnwhiteDialogue"
            \ifErr -> aegisub.cancel
            \unwrap!

    extra_data =
        wd_ass: Ass sub, sel, act

    return_sel = {}
    for i = #sel,1,-1
        aegisub.progress.task "Unwhitening Dialogue #{#sel - i + 1}/#{#sel}"
        aegisub.progress.set (#sel - i + 1) / #sel
        new_sel, new_act, extra_data = unwhite_dialogue.run sub, { sel[i] }, act, config, extra_data
        for j = 1,#return_sel
            return_sel[j] = return_sel[j] + #new_sel - 1
        for j in 1,#new_sel
            table.insert return_sel, new_sel[j]
        if return_act
            return_act = return_act + #new_sel - 1
        elseif sel[i] == act
            return_act = act

    return return_sel, return_act

edit_config = ->
    config = with config\read_edit_validate_and_save_config "aka.UnwhiteDialogue"
        \ifErr -> aegisub.cancel
        \unwrap!

if hasDepCtrl
    DepCtrl\registerMacros {
        { "UnwhiteDialogue", "Unwhite the selected dialogues", main },
        { "Edit Config", "Edit UnwhiteDialogue config", edit_config }
    }
