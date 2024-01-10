-- aka.uikit
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


local re = require("aegisub.re")
local Table = require("ILL.ILL.Table")


-- Inheritance:
-- subdialog_resolver
--    ↑
--    ↑ dialog_resolver
--    ↑     ↑
--    ↑  dialog
--    ↑     ↑
--   subdialog
local subdialog_resolver = {}
subdialog_resolver.resolve = function(self, dialog, x, y, width)
    for i, v in ipairs(self) do
        y = v:resolve(dialog, x, y, width)
    end
    return y
end

local dialog_resolver = {}
-----------------------------------------------------------------------
-- Resolve a dialog instance and return a vanilla dialog table.
-- This does not consume the original dialog instance.
--
-- @return  dialog  The resulting dialog table
-----------------------------------------------------------------------
dialog_resolver.resolve = function(self)
    local result = setmetatable({}, { __index = self })
    for k, v in ipairs(self) do
        if type(k) ~= "number" then
            result[k] = self[k]
    end end
    
    subdialog_resolver.resolve(self, result, 0, 0, result.width)
    
    return setmetatable(result, {})
end

local dialog = setmetatable({}, { __index = dialog_resolver })
-----------------------------------------------------------------------
-- Create a dialog instance.  
--
-- This function passes parameters in a table:
-- @key     "width" Width of the dialog
-- 
-- @return  self    The newly created dialog instance
-----------------------------------------------------------------------
dialog.new = function(dialog_base)
    setmetatable(dialog_base, { __index = dialog })
    dialog_base["class"] = "_au_dialog"
    dialog_base["data"] = dialog_base["data"] or {}
    return dialog_base
end
dialog.copy = function(self)
    return Table.deepcopy(self)
end

local subdialog_mt = {}
subdialog_mt.__index = function(self, key)
    if key == "resolve" then
        return subdialog_resolver["resolve"]
    else
        return dialog[key]
end end
local subdialog = setmetatable({}, subdialog_mt)
subdialog.new = function()
    local self = setmetatable({}, { __index = subdialog })
    self.class = "_au_subdialog"
    return self
end


-----------------------------------------------------------------------
-- Load name-value data into the dialog.
-- If classes in dialog has default data, this will override them.
-- This can be called both before adding the classes to the dialog and
-- after adding the classes.
-- Data from later calls to this method will override data from
-- previous calls.
--
-- @param   data    A name-value table in the same format as the second
--                  return of aegisub.dialog.display()
-- @return  self
-----------------------------------------------------------------------
dialog.load_data = function(self, data)
    for k, v in pairs(data) do
        self["data"][k] = v
    end
    return self
end


-----------------------------------------------------------------------
-- All vanilla classes are left as is. aka.uikit automates x, y, and
-- width key, while all other keys need to be filled by the user
-- manually.
-- x, y, width can be overrided by passing a new value, or by passing
-- a function to modify the value from aka.uikit. 
-----------------------------------------------------------------------
local vanilla_resolver = {}
vanilla_resolver.base = function(item, x, y, width)
    item.class = re.split(item.class, "_")
    item.class = item.class[#item.class]

    if type(item.x) == "number" then
        do end
    elseif type(item.x) == "function" then
        item.x = item.x(x)
    else
        item.x = x
    end

    if type(item.y) == "number" then
        do end
    elseif type(item.y) == "function" then
        item.y = item.y(y)
    else
        item.y = y
    end

    if type(item.width) == "number" then
        do end
    elseif type(item.width) == "function" then
        item.width = item.width(width)
    else
        item.width = width
    end

    item.height = item.height and item.height or 1
end
vanilla_resolver.resolve = function(item, dialog, x, y, width)
    vanilla_resolver.base(item, x, y, width)
    table.insert(dialog, item)
    return y + item.height
end
local vanilla_value_resolver = {}
vanilla_value_resolver.resolve = function(item, dialog, x, y, width)
    vanilla_resolver.base(item, x, y, width)
    if item["name"] then
        item["value"] = dialog["data"]["name"] and dialog["data"]["name"] or item["value"]
    end
    table.insert(dialog, item)
    return y + item.height
end
local vanilla_text_resolver = {}
vanilla_text_resolver.resolve = function(item, dialog, x, y, width)
    vanilla_resolver.base(item, x, y, width)
    if item["name"] then
        item["text"] = dialog["data"]["name"] and dialog["data"]["name"] or item["text"]
    end
    table.insert(dialog, item)
    return y + item.height
end
-----------------------------------------------------------------------
-- Create a label.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.label = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_resolver })
    item.class = "_au_label"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create an edit.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.edit = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_text_resolver })
    item.class = "_au_edit"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create an intedit.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.intedit = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_resolver })
    item.class = "_au_intedit"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create a floatedit.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.floatedit = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_resolver })
    item.class = "_au_floatedit"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create a textbox.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.textbox = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_text_resolver })
    item.class = "_au_textbox"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create a dropdown.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.dropdown = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_resolver })
    item.class = "_au_dropdown"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create a checkbox.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.checkbox = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_resolver })
    item.class = "_au_checkbox"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create a color.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.color = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_resolver })
    item.class = "_au_color"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create a coloralpha.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.coloralpha = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_resolver })
    item.class = "_au_coloralpha"
    table.insert(self, item)
    return self
end
-----------------------------------------------------------------------
-- Create an alpha.  
--
-- This method receives parameters in a table. All keys are the same as
-- in vanilla Aegisub documentation. `x`, `y`, and `width` are
-- optional.
--
-- @return  self
-----------------------------------------------------------------------
dialog.alpha = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_resolver })
    item.class = "_au_alpha"
    table.insert(self, item)
    return self
end


local separator_resolver = {}
separator_resolver.resolve = function(item, dialog, x, y, width)
    item.height = item.height and item.height or 1
    return y + item.height
end
-----------------------------------------------------------------------
-- Create a separator or an empty space on the dialog.
-- Note that if there is no more classes below separator, the separator
-- will not have any effect. To create an empty space at the bottom of
-- dialog, use an empty label.
--
-- This method receives parameters in a table.
-- @key     [height=1]  vertical height of the separator
--
-- @return  self
-----------------------------------------------------------------------
dialog.separator = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = separator_resolver })
    table.insert(self, item)
    return self
end


local floatable_resolver = {}
floatable_resolver.resolve = function(item, dialog, x, y, width)
    return item.subdialog:resolve(dialog, x, y, width)
end
local floatable_subdialog_resolver = {}
floatable_subdialog_resolver.resolve = function(item, dialog, x, y, width)
    for _, v in ipairs(item) do
        v:resolve(dialog, x, y, width)
    end
    return y
end
local floatable_subdialog_mt = {}
floatable_subdialog_mt.__index = function(self, key)
    if key == "resolve" then
        return floatable_subdialog_resolver["resolve"]
    else
        return subdialog[key]
end end
local floatable_subdialog = setmetatable({}, floatable_subdialog_mt)
floatable_subdialog.new = function()
    local self = setmetatable({}, { __index = floatable_subdialog })
    self.class = "_au_floatable_subdialog"
    return self
end
-----------------------------------------------------------------------
-- Create a subdialog for floating classes
--
-- @return  subdialog   Call methods such as `label` from this
--                      subdialog to add floating classes.
--                      All floating classes should specify their `x`,
--                      `y` and `width` keys.
-----------------------------------------------------------------------
dialog.floatable = function(self)
    local item = setmetatable({}, { __index = floatable_resolver })
    item.class = "_au_floatable"
    item.subdialog = floatable_subdialog.new()
    table.insert(self, item)
    return item.subdialog
end


local columns_resolver = {}
columns_resolver.resolve = function(item, dialog, x, y, width)
    local current_width
    local current_x = x
    local current_y
    local max_y = 0
    for i, v in ipairs(item.widths) do
        if type(v) == "number" then
            current_width = v
        elseif type(v) == "function" then
            current_width = v(width)
        else
            error("[aka.uikit] Invalid key widths passed to dialog.columns()\n[aka.uikit] width should either be a number or function")
        end

        current_y = item.columns[i]:resolve(dialog, current_x, y, current_width)

        max_y = math.max(max_y, current_y)
        current_x = current_x + current_width
    end
    return max_y
end
-----------------------------------------------------------------------
-- Create columns to arrange classes side by side
--
-- This method receives parameters in a table.
-- @key     widths      A table of widths for each columns. The number
--                      of widths in this table determines the number
--                      of columns created.
--                      For example, to create three equally divided
--                      columns in a dialog with a total width of 12:
--                          dialog:columns({ widths = { 4, 4, 4 } })
--                      Accepts both number and function. 
--
-- @return  subdialogs  For each width in widths param, return a
--                      subdialog. Call methods such as `label` from
--                      these subdialog to add classes to each column.
-----------------------------------------------------------------------
dialog.columns = function(self, base)
    setmetatable(base, { __index = columns_resolver })
    base.class = "_au_columns"
    base.columns = {}
    for _, _ in ipairs(base.widths) do
        table.insert(base.columns, subdialog.new())
    end
    table.insert(self, base)
    return table.unpack(base.columns)
end


local functions = {}

functions.subdialog_resolver = subdialog_resolver
functions.dialog_resolver = dialog_resolver
functions.dialog = dialog
functions.subdialog = subdialog
functions.vanilla_resolver = vanilla_resolver
functions.vanilla_value_resolver = vanilla_value_resolver
functions.vanilla_text_resolver = vanilla_text_resolver
functions.separator_resolver = separator_resolver
functions.floatable_resolver = floatable_resolver
functions.floatable_subdialog_resolver = floatable_subdialog_resolver
functions.floatable_subdialog = floatable_subdialog
functions.columns_resolver = columns_resolver

return functions
