-- aka.unwhite_dialogue
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

versioning.name = "aka.unwhite_dialogue"
versioning.description = "Module aka.unwhite_dialogue"
versioning.version = "0.0.3"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.unwhite_dialogue"

versioning.requireModules = "[{ \"moduleName\": \"ILL.ILL\" }, { \"moduleName\": \"aka.CIELab\" }, { \"moduleName\": \"aka.outcome\" }]"

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl({
        name = versioning.name,
        description = versioning.description,
        version = versioning.version,
        author = versioning.author,
        moduleName = versioning.namespace,
        url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/dev/DependencyControl.json",
        {
            { "ILL.ILL" },
            { "aka.CIELab" },
            { "aka.outcome" }
        }
    }):requireModules()
end
local ILL = require("ILL.ILL")
local Line, Text, Util = ILL.Line, ILL.Text, ILL.Util
local outcome = require("aka.outcome")
local ok, err, o = outcome.ok, outcome.err, outcome.o

local samples = require("aka.unwhite_dialogue.samples")

local workflow

workflow = {}

workflow.run = function(sub, sel, act, config, extra_data)
    local line
    local subtitle_scenecut
    local background_scenecut
    local subtitle_colours
    local background_colours
    local i

    if not extra_data or type(extra_data) ~= "table" then extra_data = {} end
    if not extra_data.wd_ass then error("[aka.unwhite_dialogue] Unspecified Error") end
    line = sub[sel[1]]
    line.isShape = Util.isShape(line.text)
    line.text = Text(line.text, line.isShape)
    line = Line.process(extra_data.wd_ass, line)
    if line.width == 0 then
        return sel, act, extra_data
    end
    if not extra_data.wd_parsed_config then
        extra_data.wd_parsed_config = {}
        if config.scenecut then
            extra_data.wd_parsed_config[config.scenecut.exec] = loadstring(config.scenecut.exec)
            extra_data.wd_parsed_config[config.scenecut.eval] = loadstring(config.scenecut.eval)
        end
        extra_data.wd_parsed_config[config.colours.exec] = loadstring(config.colours.exec)
        for _, t in ipairs(config.colours) do
            extra_data.wd_parsed_config[t.eval] = loadstring(t.eval)
    end end

    subtitle_scenecut, background_scenecut, subtitle_colours, background_colours = samples.prepare(line, config, extra_data.wd_parsed_config)
    subtitle_scenecut = samples.do_nothing(subtitle_scenecut)
    i = 1
    for line, subtitle_colours, background_colours in samples.iter_scenecut(line, subtitle_scenecut, background_scenecut, subtitle_colours, background_colours, config, extra_data.wd_parsed_config) do
        samples.set_colour(line, subtitle_colours, background_colours, config, extra_data.wd_parsed_config)
        line.text = tostring(line.text)
        if i == 1 then
            sub[sel[1]] = line
        else
            sub.insert(sel[1] + i - 1, line)
            table.insert(sel, sel[1] + i - 1)
    end end
    return sel, act, extra_data
end

local functions = {}

functions.versioning = versioning
functions.workflow = workflow

return functions
