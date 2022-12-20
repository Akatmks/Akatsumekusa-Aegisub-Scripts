-- aka.TimeLine.lua
-- Copyright (c) Akatsumekusa

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

script_name = "TimeLine"
script_description = "Functions for timing including join, split, snap and more"
script_version = "1.0~a"
script_author = "Akatsumekusa"
script_namespace = "aka.TimeLine"




function runGUI(subtitles, selected_lines, active_line)
    -- loadSettings()
    -- inline renderGUI()
    -- saveSettings()

    process()
    -- inline setUndoPoint()
end
function runLastClockwise(subtitles, selected_lines, active_line)
    -- loadSettings()
    -- inline setChirarity()

    process()
    -- inline setUndoPoint()
end
function runLastCounterwise(subtitles, selected_lines, active_line)
    -- loadSettings()
    -- inline setChirarity()

    process()
    -- inline setUndoPoint()
end

function process(settings, subtitles, selected_lines, active_line)
    -- for line in selected_lines do
    --     preprocess() -- count the nodes and add the marks
    --     validate() -- isCounterwise isComplete
    --     parse()
    --     interpret()
    --     postprocess()
    -- end
end

aegisub.register_macro(script_name .. "/" .. script_name, script_description, runGUI)
aegisub.register_macro(script_name .. "/Run the last commands clockwise", "Run the last used commands clockwise", runLastClockwise)
aegisub.register_macro(script_name .. "/Run the last commands counterwise", "Run the last used commands counterwise", runLastCounterwise)
