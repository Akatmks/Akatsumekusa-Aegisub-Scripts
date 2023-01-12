-- aka.actor
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

versioning.name = "aka.actor"
versioning.description = "Module aka.actor"
versioning.version = "0.1.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.actor"

versioning.requireModules = "[{ \"moduleName\": \"aka.config2\" }, { \"moduleName\": \"aegisub.re\" }]"

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
            { "aka.config2" },
            { "aegisub.re" },
        }
    }):requireModules()
end

local field = require("aka.actor.config")
local re = require("aegisub.re")

local exp
local flags
local setFlags

local flag_
local setFlag
local clearFlag
local toggleFlag
local onemoreFlag
local onelessFlag

--                (?<=[^\\]\s|^\s|^)([^\s\\]*(?:\\.[^\s\\]*)*)(\s+)
-- Since this is a gmatch from start to end with every match followed by another, the lookbehind part could be omitted
--                ([^\s\\]*(?:\\.[^\s\\]*)*)(\s+)
exp = re.compile("([^\\s\\\\]*(?:\\\\.[^\\s\\\\]*)*)(\\s+)")

flags = function(line, flag)
    local _flag
    local flags
    local matches

    flags = {}
    matches = {}

    for match in exp:gmatch(line[field:field()]) do
        _flag = {}
        _flag["body"] = match[2]["str"]
        _flag["tail"] = match[3]["str"]
        table.insert(flags, _flag)

        if _flag["body"] == flag then table.insert(matches, #flags) end
    end

    return flags, matches
end
setFlags = function(line, flags)
    line[field:field()] = ""

    -- nil body will not be included but "" body will
    -- Both nil and "" tail will be treated as " "
    for i = 1, #flags do
        repeat
            if not flags[i]["body"] then break end
            if not flags[i]["tail"] or flags[i]["tail"] == "" then
                if i ~= #flags then flags[i]["tail"] = " "
                else flags[i]["tail"] = "" end
            end

            line[field:field()] = line[field:field()] + flags[i]["body"] + flags[i]["tail"]
        until true
    end
end

flag_ = function(line, flag)
    local matches
    
    _, matches = flags(line, flag)

    if #matches == 0 then return false
    else return #matches end
end
setFlag = function(line, flag)
    local _flags
    local matches
    
    _flags, matches = flags(line, flag)

    if #matches == 0 then
        table.insert(_flags, { ["head"] = flag })
    end

    setFlags(line, _flags)
end
clearFlag = function(line, flag)
    local _flags
    local matches
    
    _flags, matches = flags(line, flag)

    for _, match in ipairs(matches) do
        _flags[match]["head"] = nil
    end

    setFlags(line, _flags)
end
toggleFlag = function(line, flag)
    local _flags
    local matches
    
    _flags, matches = flags(line, flag)

    if #matches ~= 0 then
        for _, match in ipairs(matches) do
            _flags[match]["head"] = nil
        end
    else
        table.insert(_flags, { ["head"] = flag })
    end

    setFlags(line, _flags)
end
onemoreFlag = function(line, flag)
    local _flags
    
    _flags = flags(line, flag)

    table.insert(_flags, { ["head"] = flag })

    setFlags(line, _flags)
end
onelessFlag = function(line, flag)
    local _flags
    
    _flags = flags(line, flag)

    _flags[#flags]["head"] = nil

    setFlags(line, _flags)
end

local functions = {}

functions.versioning = versioning

functions.flag = flag_
functions.setFlag = setFlag
functions.clearFlag = clearFlag
functions.toggleFlag = toggleFlag
functions.onemoreFlag = onemoreFlag
functions.onelessFlag = onelessFlag

-- Note that this field is shared between all scripts using aka.actor
functions.field = field

return functions
