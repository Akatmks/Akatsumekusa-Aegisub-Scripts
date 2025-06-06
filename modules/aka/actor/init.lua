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

-- A list of functions are at the bottom

local versioning = {}

versioning.name = "aka.actor"
versioning.description = "Module aka.actor"
versioning.version = "1.0.9"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.actor"

versioning.requiredModules = "[{ \"moduleName\": \"aka.singlesimple\" }, { \"moduleName\": \"aegisub.re\" }]"

local version = require("l0.DependencyControl")({
    name = versioning.name,
    description = versioning.description,
    version = versioning.version,
    author = versioning.author,
    moduleName = versioning.namespace,
    url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
    feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "aka.singlesimple", version = "1.0.0" },
        { "aegisub.re" }
    }
})
version:requireModules()

local field = require("aka.singlesimple").make_config("aka.actor", { "actor", "effect", "style" }, "actor")
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

--                (?<=[^\\]\s|^\s|^)([^\s\\]*(?:\\.[^\s\\]*)*)(\s+|$)
-- Since this is a gmatch from start to end with every match followed by another, the lookbehind part could be omitted
--                ([^\s\\]*(?:\\.[^\s\\]*)*)(\s+|$)
exp = re.compile("([^\\s\\\\]*(?:\\\\.[^\\s\\\\]*)*)(\\s+|$)")

flags = function(line, flag)
    local flags
    local matches
    local match
    local last_tail
    local text
    local _flag

    flags = {}
    matches = {}
    last_tail = ""

    text = line[field:value()]
    while string.len(text) ~= 0 do
        match = exp:match(text)
        if match[1]["first"] == 1 then
            _flag = {}
            _flag["body"] = match[2]["str"] or ""
            _flag["tail"] = match[3]["str"] or ""
            table.insert(flags, _flag)

            if _flag["body"] == flag then table.insert(matches, #flags) end
            last_tail = _flag["tail"]

            text = string.sub(text, match[1]["last"] + 1)
        else -- Due to escaping EOL
            text = text .. " "
        end
    end

    return flags, matches, last_tail
end
setFlags = function(line, flags, last_tail)
    line[field:value()] = ""

    -- nil body will not be included but "" body will
    -- Both nil and "" tail will be treated as " "
    for i = 1, #flags do
        repeat
            if not flags[i]["body"] then break end
            if not flags[i]["tail"] or flags[i]["tail"] == "" then flags[i]["tail"] = " " end

            line[field:value()] = line[field:value()] .. flags[i]["body"] .. flags[i]["tail"]
        until true
    end
    line[field:value()] = string.gsub(line[field:value()], "%s*$", last_tail)
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
    local last_tail
    
    _flags, matches, last_tail = flags(line, flag)

    if #matches == 0 then
        table.insert(_flags, { ["body"] = flag })
    end

    setFlags(line, _flags, last_tail)
end
clearFlag = function(line, flag)
    local _flags
    local matches
    local last_tail
    
    _flags, matches, last_tail = flags(line, flag)

    for _, match in ipairs(matches) do
        _flags[match]["body"] = nil
    end

    setFlags(line, _flags, last_tail)
end
toggleFlag = function(line, flag)
    local _flags
    local matches
    local last_tail
    
    _flags, matches, last_tail = flags(line, flag)

    if #matches ~= 0 then
        for _, match in ipairs(matches) do
            _flags[match]["body"] = nil
        end
    else
        table.insert(_flags, { ["body"] = flag })
    end

    setFlags(line, _flags, last_tail)
end
onemoreFlag = function(line, flag)
    local _flags
    local last_tail
    
    _flags, _, last_tail = flags(line, flag)

    table.insert(_flags, { ["body"] = flag })

    setFlags(line, _flags, last_tail)
end
onelessFlag = function(line, flag)
    local _flags
    local last_tail
    
    _flags, _, last_tail = flags(line, flag)

    _flags[#flags]["body"] = nil

    setFlags(line, _flags, last_tail)
end

local functions = {}

-- Check if a flag is set
-- Return false if the flag is not set,
-- Or return an integer for the times the flag is set
functions.flag = flag_
-- If flag is not set, set flag to 1
functions.setFlag = setFlag
-- If flag is set, unset the flag
functions.clearFlag = clearFlag
-- If flag is set, unset the flag,
-- Otherwise if flag is not set, set flag to 1
functions.toggleFlag = toggleFlag
-- Append one more flag
functions.onemoreFlag = onemoreFlag
-- Remove one flag
functions.onelessFlag = onelessFlag

-- Note that this field is shared between all scripts using aka.actor
-- Use field:value() to get the field using,
-- Use field:setValue() to set the field to either "actor", "effect" or "style"
functions.field = field

functions._flags = flags

functions.version = version
functions.versioning = versioning

return version:register(functions)
