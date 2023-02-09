-- aka.template
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

local selected_template_keys
local get_template_key
local select_template_key

selected_template_keys = nil do
    local is_successs

    is_successs, selected_template_keys = config2.read_config("aka.template")
    if not is_successs then selected_template_keys = nil end
end

get_template_key = function(config_templates)
    local it
    local swap

    if selected_template_keys then
        if config_templates[selected_template_keys.key] then
            return selected_template_keys.key
        end
        it = selected_template_keys
        while it.next ~= nil do
            if config_templates[it.next.key] then
                swap = it.next.next
                it.next.next = selected_template_keys
                selected_template_keys = it.next
                it.next = swap
                return selected_template_keys.key
            end
            it = it.next
    end end

    for k in pairs(config_templates) do
        selected_template_keys = { key = k, next = selected_template_keys }
        config2.write_config("aka.template", selected_template_keys)
        return k
end end
select_template_key = function(template_key)
    local fake_templates

    fake_templates = {}
    fake_templates[template_key] = ""
    get_template_key(fake_templates)
end

local functions = {}

functions.get_template_key = get_template_key
functions.select_template_key = select_template_key

return functions
