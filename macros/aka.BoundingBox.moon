-- aka.BoundingBox
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
    name: "BoundingBox"
    description: "Create a clip of the bounding box of the subtitle line"
    version: "1.0.6"
    author: "Akatsumekusa and contributors"
    namespace: "aka.BoundingBox"
    requiredModules: "[{ \"moduleName\": \"ILL.ILL\" }, { \"moduleName\": \"SubInspector.Inspector\" }, { \"moduleName\": \"aka.outcome\" }]"

export script_name = versioning.name
export script_description = versioning.description
export script_author = versioning.author
export script_version = versioning.version
export script_namespace = versioning.namespace

DepCtrl = (require "l0.DependencyControl") {
    name: versioning.name,
    description: versioning.description,
    version: versioning.version,
    author: versioning.author,
    moduleName: versioning.namespace,
    url: "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
    feed: "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "ILL.ILL" },
        { "SubInspector.Inspector" },
        { "aka.outcome" }
    }
}
DepCtrl\requireModules!

import Ass, Line from require "ILL.ILL"
Inspector = require "SubInspector.Inspector"
import o from require "aka.outcome"

text_extents_main = (sub, sel, act) ->
    ass = Ass sub, sel, act

    for l, line, s, i, n in ass\iterSel true
        ass\progressLine s, i, n
        Line.extend ass, line, i
        with line
            { px, py } = .data.pos
            ox = switch .data.an
                when 1, 4, 7 then px
                when 2, 5, 8 then px - .lines.width / 2
                when 3, 6, 9 then px - .lines.width
            oy = switch .data.an
                when 7, 8, 9 then py
                when 4, 5, 6 then py - .lines.height / 2
                when 1, 2, 3 then py - .lines.height
            .tags\insert { { "clip", { ox, oy, ox + .lines.width, oy + .lines.height } } }
        ass\setLine line, s, true

    return ass\getNewSelection!

inspector_main = (sub, sel, act) ->
    ass = Ass sub, sel, act
    inspector = o(Inspector sub)\unwrap!

    for l, line, s, i, n in ass\iterSel true
        ass\progressLine s, i, n
        Line.process ass, line
        bounds = o(inspector\getBounds { l })\unwrap![1][1]
        if bounds
            with bounds
                line.tags\insert { { "clip", { .x, .y, .x + .w, .y + .h } } }
        else
            aegisub.debug.out 2, "[aka.BoundingBox] Empty bounding box on line " .. tostring(ass\lineNumber(s)) .. " (" .. tostring(i) .. "/" .. tostring(n) .. ")"
        ass\setLine line, s, true

    return ass\getNewSelection!

DepCtrl\registerMacros {
    { "text_extents", "Create a rect clip of the bounding box using aegisub.text_extents", text_extents_main },
    { "SubInspector", "Create a rect clip of the bounding box using SubInspector", inspector_main }
}
