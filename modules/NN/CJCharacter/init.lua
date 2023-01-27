-- NN.cjk_unicode
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

versioning.name = "NN.CJCharacter"
versioning.description = "Module NN.CJCharacter"
versioning.version = "0.1.4"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "NN.CJCharacter"

versioning.requireModules = "[{ \"moduleName\": \"aegisub.unicode\" }]"

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
            { "aegisub.unicode" }
        }
    }):requireModules()
end
local unicode = require("aegisub.unicode")

local range

range = function(char)
    char = unicode.codepoint(char)

    --[[ 漢字/Hanzi/Kanji 𡨸喃/Chữ Nôm ]]
    if --[[ CJK Unified Ideographs             ]] ( 0x4E00  <= char and char <= 0x9FFF  ) or
       --[[ CJK Unified Ideographs Extension A ]] ( 0x3400  <= char and char <= 0x4DBF  ) or
       --[[ CJK Unified Ideographs Extension B ]] ( 0x20000 <= char and char <= 0x2A6DF ) or
       --[[ CJK Unified Ideographs Extension C ]] ( 0x2A700 <= char and char <= 0x2B73F ) or
       --[[ CJK Unified Ideographs Extension D ]] ( 0x2B740 <= char and char <= 0x2B81F ) or
       --[[ CJK Unified Ideographs Extension E ]] ( 0x2B820 <= char and char <= 0x2CEAF ) or
       --[[ CJK Unified Ideographs Extension F ]] ( 0x2CEB0 <= char and char <= 0x2EBEF ) or
       --[[ CJK Unified Ideographs Extension G ]] ( 0x30000 <= char and char <= 0x3134F ) or
       --[[ CJK Unified Ideographs Extension H ]] ( 0x31350 <= char and char <= 0x323AF ) or
       --[[ CJK Compatibility Ideographs       ]] ( 0xF900  <= char and char <= 0xFAFF  ) or
       --[[ Enclosed Ideographic Supplement    ]] ( 0x1F200 <= char and char <= 0x1F2FF )
    then return "CJK Character"

    elseif --[[  ]] ( 0x3000 <= char and char <= 0x303F ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x )
    then return "CJK Symbol"

    elseif --[[ CJK Radicals Supplement ]] ( 0x2E80 <= char and char <= 0x2EFF ) or
           --[[ Kangxi Radicals         ]] ( 0x2F00 <= char and char <= 0x2FDF )
    then return "CJK Radical"

    elseif --[[ CJK Strokes ]] ( 0x31C0 <= char and char <= 0x31EF ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x )
    then return "CJK Stroke"

    elseif --[[ CJK Symbols and Punctuation ]] ( 0x3000 <= char and char <= 0x303F ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x ) or
           --[[  ]] ( 0x <= char and char <= 0x )
    then return "CJK Punctuation"

    else return "Unspecified" end
end end
