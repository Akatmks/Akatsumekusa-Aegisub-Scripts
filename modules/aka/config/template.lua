-- aka.config
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

local config2 = require("aka.config2")
local outcome = require("aka.outcome")
local ok, err, = outcome.ok, outcome.err

local selected_template_keys do
    selected_template_keys = config2.read_config("aka.config.template")
        :andThen(function(config)
            local it

            if type(config.key) ~= string then
                return ok(nil)
            else
                it = config
                while it.next ~= nil do
                    if type(it.next.key) ~= string then
                        it.next = nil
                        break
                    else
                        it = it.next
                end end
                return ok(config)
            end end)
        :unwrapOr(nil)
end

local log_template_key
local get_template_key_from_list
local get_template_from_table

log_template_key = function(template_key)
    local it

    selected_template_keys = { ["key"] = template_key, ["next"] = selected_template_keys }
    it = selected_template_keys
    while it.next ~= nil do
        if it.next.key == template_key then
            it.next = it.next.next
        else
            it = it.next
    end end
    config2.write_config("aka.config.template", selected_template_keys)
        :ifErr(function(err)
            aegisub.debug.out(1, "[aka.config.template] Failed to save template to file\n" .. err) end)
end
get_template_key_from_list = function(template_keys)
    local fake_table

    for _, v in ipairs(template_keys) do
        fake_table[v] = v
    end
    return get_template_from_table(fake_table)
end
get_template_from_table = function(templates)
    local it
    local swap

    if selected_template_keys then
        it = selected_template_keys
        if templates[it.key] then
            return templates[it.key]
        end
        while it.next ~= nil do
            if templates[it.next.key] then
                return templates[it.next.key]
            end

            it = it.next
    end end
    
    if templates[1] then return templates[templates[1]] end
    if templates["Default"] then return templates["Default"] end
    if templates["default"] then return templates["default"] end
    for _, v in pairs(templates) do
        return v
end end

local functions = {}

functions.log_template_key = log_template_key
functions.get_template_key_from_list = get_template_key_from_list
functions.get_template_from_table = get_template_from_table

return functions
