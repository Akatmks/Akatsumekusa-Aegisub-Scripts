-- aka.outcome
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

versioning.name = "aka.outcome"
versioning.description = "Module aka.outcome"
versioning.version = "0.1.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.outcome"

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
    })
end

local outcome = require("aka.outcome.outcome")

local o

o = function(...)
    local result

    result = table.pack(pcall(...))
    if result[1] == true and #result == 1 then
        return outcome.ok(result[1])
    elseif result[1] == true and #result == 2 then
        return outcome.ok(result[2])
    elseif result[1] == true then
        table.remove(result, 1)
        return outcome.ok(result)
    elseif (result[1] == false or result[1] == nil) and #result == 1 then
        return outcome.err("[aka.outcome] Error message not provided")
    elseif (result[1] == false or result[1] == nil) and (#result == 2 or type(result[2]) == "string") then
        return outcome.err(result[2])
    elseif (result[1] == false or result[1] == nil) then
        table.remove(result, 1)
        return outcome.err(result)
    else
        return outcome.ok(result)
end end

outcome.o = o

return outcome
