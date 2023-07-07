-- aka.workflow
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

------------------------------------------------------------------------------
-- Workflow table
-- A module need to have a workflow table in the root table:
-- ```
-- local functions = {}
-- functions.versioning = versioning
-- functions.workflow = workflow
-- return functions
-- ```
-- The workflow table:
-- ```
-- workflow = {
--     display_name = "BackupProto"
--
--     -- The main function
--     run = function(subs, sel, act, config, work, extra)
--         return sel, act, extra
--     end
--
--     -- If you are processing subtitles line by line, you should set both values to 1;
--     -- If, for example, you are doing gradient and you need lines to be grouped by 2, you should set both values to 2;
--     -- If can accept any arbitrary numbers of lines, you can set both values to 0;
--     min_lines_per_section = 1 -- Setting this to 0 is the same as 1
--     max_lines_per_section = 1 -- Setting this to 0 means inf
--
--     -- There are 4 possible values for multithreading
--     -- true if each line section is processed independent of each other,
--     -- "aggressive" if you expect your process to be slower than 100 ms per line section and
--     --                 each line section is processed independent of each other
--     -- false if you multithreading is not possible (the line sections will still be fed one by one)
--     -- "manual" if you will need all the lines to be fed to you at once
--     multithreading = true
-- }
-- ```
------------------------------------------------------------------------------

local outcome = require("aka.outcome")
local ok, err, o = outcome.ok, outcome.err, outcome.o

local info
local info_table

info_table = {}
info = function(script)
    return o(info_table[script])
        :unwrapOrElse(||
            info_table[script] = o(pcall(require, script))
                :ifErr(||
                    error("[aka.workflow] Module not found with name „" .. script .. "“"))
                :andThen(|scr|
                    o(scr.workflow))
                :andThen(|workflow|
                    if type(workflow) == "table" then ok(workflow)
                    else err() end)
                :ifErr(||
                    error("[aka.workflow] No workflow table found in module „" .. script .. "“"))
                :map(|workflow|
                    workflow.display_name = o(workflow.display_name)
                        :andThen(|display_name|
                            if type(display_name) == "string" then ok(display_name)
                            else err() end)
                        :unwrapOr(script)
                    workflow)
                :map(|workflow|
                    if type(workflow.run) == "function" then workflow
                    else error("[aka.workflow] Invalid workflow table for module „" .. script .. "“\n[aka.workflow] `workflow.run` not found") end)
                :map(|workflow|
                    workflow.min_lines_per_section = o(workflow.min_lines_per_section)
                        :orOther(ok(1))
                        :andThen(|lines|
                            if type(lines) == "number" and lines >= 0 then ok(lines)
                            else err() end)
                        :map(|lines|
                            if lines == 0 then 1 else lines end)
                        :expect("[aka.workflow] Invalid workflow table for module „" .. script .. "“\n[aka.workflow] Invalid `workflow.min_lines_per_section`")
                    workflow)
                :map(|workflow|
                    workflow.max_lines_per_section = o(workflow.max_lines_per_section)
                        :orOther(ok(1))
                        :andThen(|lines|
                            if type(lines) == "number" and lines >= 0 then ok(lines)
                            else err() end)
                        :map(|lines|
                            if lines == 0 then 1/0 else lines end)
                        :expect("[aka.workflow] Invalid workflow table for module „" .. script .. "“\n[aka.workflow] Invalid `workflow.max_lines_per_section`")
                    workflow)
                :map(|workflow|
                    workflow.multithreading = ok(workflow.multithreading)
                        :andThen(|multithreading|
                            if multithreading == true or
                               multithreading == "aggressive" or
                               multithreading == false or
                               multithreading == "manual" then ok(multithreading)
                            elseif multithreading == nil then ok("manual")
                            else err() end)
                        :expect("[aka.workflow] Invalid workflow table for module „" .. script .. "“\n[aka.workflow] Invalid `workflow.multithreading`")
                    workflow)
                :unwrap()
            info_table[script])
end
