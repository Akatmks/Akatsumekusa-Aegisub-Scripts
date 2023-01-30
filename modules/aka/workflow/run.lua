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

local wconfig = require("aka.workflow.config")
local config

local run
local run_chooseAnotherFlow

run = function (sub, sel, act, workflow, next_workflow, extra_data)
    local is_success
    local work
    local flow
    local worker
    local subs_
    local sel_
    local act_
    local extra_data_

    if not config then config = wconfig.config() end

    repeat
        if workflow and workflow["work"] then
            work = workflow["work"]
            flow = workflow["flow"]

            if type(flow) == "string" then
                then aegisub.progress.title("Work " .. work .. " Flow " .. flow)
            end

            is_success, worker = pcall(require, work)
            if not is_success then
                aegisub.debug.out(0, "[aka.workflow]\nAutomation module " .. work .. " is not found.\nPlease make sure every script used in the workflow is installed.\n")
                return false
            end
            if type(flow) == "string" then
                while not config[work] or not config[work][flow] do
                    flow = run_chooseAnotherFlow(work, flow)
                end
                flow = config[work][flow]["flow"]

                next_workflow = config[work][flow]["next_workflow"]
            end

            workflow = next_workflow
            next_workflow = nil

            subs_, sel_, act_, extra_data_ = worker.workflow.run(subs, sel, act, flow, extra_data)
            if subs_ then subs = subs_ end
            if sel_ then sel = sel_ end
            if act_ then act = act_ end
            if extra_data_ then extra_data = extra_data_ end
        else
            aegisub.progress.title("Null Workflow")

            workflow = next_workflow
            next_workflow = nil
        end
    until not workflow or
          not workflow["work"]

    return subs, sel, act
end

run_chooseAnotherFlow = function (work, current_flow)
    local dialog
    local buttons
    local button_ids
    local button
    local result_table

    -- TODO
end

local functions

functions.run = run

functions.config = config

return functions
