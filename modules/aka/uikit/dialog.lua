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
local Table = require("ILL.ILL.Table").Table


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
    subdialog_resolver.resolve(self, result, 0, 0, result.width)
    return setmetatable(result, {})
end

local dialog = {}
-----------------------------------------------------------------------
-- Create a dialog instance.  
--
-- This function passes parameters in a table:
-- @key     "width" Width of the dialog
-- 
-- @return  self    The newly created dialog instance
-----------------------------------------------------------------------
dialog.new = function(dialog_base)
    dialog_base["class"] = "_au_dialog"
    dialog_base["data"] = dialog_base["data"] or {}
    setmetatable(dialog_base, { __index = dialog })
    return dialog_base
end
dialog.copy = function(self)
    return Table.deepcopy(self)
end
local dialog_mt = {}
dialog_mt.__index = dialog_resolver
dialog_mt.__call = function(cls, ...) return cls.new(...) end
setmetatable(dialog, dialog_mt)

local subdialog_mt = {}
subdialog_mt.__index = function(self, key)
    local target = rawget(subdialog_resolver, key)
    if target then return target
    else return dialog[key] end
end
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
    if type(data) == "table" then
        for k, v in pairs(data) do
            self["data"][k] = v
    end end
    return self
end


local last_class = re.compile([[.*_([^_]+)$]])
-----------------------------------------------------------------------
-- All vanilla classes are left as is. aka.uikit automates x, y, and
-- width key, while all other keys need to be filled by the user
-- manually.
-- x, y, width can be overrided by passing a new value, or by passing
-- a function to modify the value from aka.uikit. 
-----------------------------------------------------------------------
local vanilla_label_resolver = {}
vanilla_label_resolver.base = function(item, x, y, width)
    item.class = last_class:match(item.class)[2]["str"]

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
vanilla_label_resolver.resolve = function(item, dialog, x, y, width)
    item = Table.copy(item)
    vanilla_label_resolver.base(item, x, y, width)
    if item["name_label"] then
        item["label"] = dialog["data"][item["name_label"]] ~= nil and dialog["data"][item["name_label"]] or item["label"]
        item["name_label"] = nil
    end
    table.insert(dialog, item)
    return y + item.height
end
local vanilla_value_resolver = {}
vanilla_value_resolver.resolve = function(item, dialog, x, y, width)
    item = Table.copy(item)
    vanilla_label_resolver.base(item, x, y, width)
    if item["name"] then
        item["value"] = dialog["data"][item["name"]] ~= nil and dialog["data"][item["name"]] or item["value"]
    end
    table.insert(dialog, item)
    return y + item.height
end
local vanilla_value_items_resolver = {}
vanilla_value_items_resolver.resolve = function(item, dialog, x, y, width)
    item = Table.copy(item)
    vanilla_label_resolver.base(item, x, y, width)
    if item["name"] then
        item["value"] = dialog["data"][item["name"]] ~= nil and dialog["data"][item["name"]] or item["value"]
    end
    if item["name_items"] then
        item["items"] = dialog["data"][item["name_items"]] ~= nil and dialog["data"][item["name_items"]] or item["items"]
        item["name_items"] = nil
    end
    table.insert(dialog, item)
    return y + item.height
end
local vanilla_value_label_resolver = {}
vanilla_value_label_resolver.resolve = function(item, dialog, x, y, width)
    item = Table.copy(item)
    vanilla_label_resolver.base(item, x, y, width)
    if item["name"] then
        item["value"] = dialog["data"][item["name"]] ~= nil and dialog["data"][item["name"]] or item["value"]
    end
    if item["name_label"] then
        item["label"] = dialog["data"][item["name_label"]] ~= nil and dialog["data"][item["name_label"]] or item["label"]
        item["name_label"] = nil
    end
    table.insert(dialog, item)
    return y + item.height
end
local vanilla_text_resolver = {}
vanilla_text_resolver.resolve = function(item, dialog, x, y, width)
    item = Table.copy(item)
    vanilla_label_resolver.base(item, x, y, width)
    if item["name"] then
        item["text"] = dialog["data"][item["name"]] ~= nil and dialog["data"][item["name"]] or item["text"]
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
-- Additionally:
-- @key     name_label  Change the label dynamically
--
-- @return  self
-----------------------------------------------------------------------
dialog.label = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_label_resolver })
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
-- Additionally:
-- @key     name_items  Change the item list dynamically
--
-- @return  self
-----------------------------------------------------------------------
dialog.dropdown = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_items_resolver })
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
-- Additionally:
-- @key     name_label  Change the label dynamically
--
-- @return  self
-----------------------------------------------------------------------
dialog.checkbox = function(self, item)
    if item == nil then item = {} end
    setmetatable(item, { __index = vanilla_value_label_resolver })
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
    return y + item.height and item.height or 1
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
    local target = rawget(floatable_subdialog_resolver, key)
    if target then return target
    else return subdialog[key] end
end
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


local ifable_resolver = {}
ifable_resolver.resolve = function(item, dialog, x, y, width)
    if item["name"] and
       ((item["value"] ~= nil and dialog["data"][item["name"]] == item["value"]) or
        (item["value"] == nil and dialog["data"][item["name"]])) then
        return item.subdialog:resolve(dialog, x, y, width)
    else
        return y
end end
-----------------------------------------------------------------------
-- Create a subdialog only when value with the name in dialog data is
-- truthy or equal to the value provided.
--
-- This method receives parameters in a table.
-- @key     name        The name for the value in the dialog data.
-- @key     value       If this key is not provided, classes in the
--                      subdialog will be displayed if value for the
--                      name is truthy.
--                      If this key is provided, classes in the
--                      subdialog will be displayed if value for the
--                      name equals to this key
--
-- @return  subdialog   Call methods such as `label` from this
--                      subdialog to add to ifable.
-----------------------------------------------------------------------
dialog.ifable = function(self, item)
    setmetatable(item, { __index = ifable_resolver })
    item.class = "_au_ifable"
    item.subdialog = subdialog.new()
    table.insert(self, item)
    return item.subdialog
end

local unlessable_resolver = {}
unlessable_resolver.resolve = function(item, dialog, x, y, width)
    if item["name"] and
       ((item["value"] ~= nil and dialog["data"][item["name"]] == item["value"]) or
        (item["value"] == nil and dialog["data"][item["name"]])) then
        return y
    else
        return item.subdialog:resolve(dialog, x, y, width)
end end
-----------------------------------------------------------------------
-- Create a subdialog only when value with the name in dialog data is
-- falsy or not equal to the value provided.
--
-- This method receives parameters in a table.
-- @key     name        The name for the value in the dialog data.
-- @key     value       If this key is not provided, classes in the
--                      subdialog will be displayed if value for the
--                      name is falsey.
--                      If this key is provided, classes in the
--                      subdialog will be displayed if value for the
--                      name does not equal to this key
--
-- @return  subdialog   Call methods such as `label` from this
--                      subdialog to add to unlessable.
-----------------------------------------------------------------------
dialog.unlessable = function(self, item)
    setmetatable(item, { __index = unlessable_resolver })
    item.class = "_au_unlessable"
    item.subdialog = subdialog.new()
    table.insert(self, item)
    return item.subdialog
end


-----------------------------------------------------------------------
-- Join another dialog
--
-- @param   dialog  Note that only classes in the dialog will be joined
--                  and other information such as data and width will
--                  be discarded.
--                  The dialog will be copied inside the function so
--                  later modification of the parameter dialog won't
--                  affect the dialog joined.
--
-- @return  self
-----------------------------------------------------------------------
dialog.join_dialog = function(self, dialog)
    dialog = dialog:copy()
    dialog.class = "_au_subdialog"
    setmetatable(dialog, { __index = subdialog })
    table.insert(self, dialog)
    return self
end


local columns_resolver = {}
columns_resolver.resolve = function(item, dialog, x, y, width)
    local current_width
    local current_x = x
    local new_y
    local max_y = 0

    for i, v in ipairs(item.widths) do
        if type(v) == "number" then
            current_width = v
        elseif type(v) == "function" then
            current_width = v(width)
        else
            error("[aka.uikit] Invalid key widths passed to dialog.columns()\n[aka.uikit] widths should either be a table of number or function")
        end
        new_y = item.columns[i]:resolve(dialog, current_x, y, current_width)
        max_y = math.max(max_y, new_y)
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
dialog.row = dialog.columns


-----------------------------------------------------------------------
-- Create an edit with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for edit are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  \fn  [ Arial ]
-- Calls:
--  dialog:label_edit({ label = "\\fn", name = "fn", text = "Arial" })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_edit = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:edit(item)
    return self
end
-----------------------------------------------------------------------
-- Create an intedit with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for intedit are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  \frz  [  0.  ]
-- Calls:
--  dialog:label_floatedit({ label = "\\frz", name = "frz", value = 0 })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_intedit = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:intedit(item)
    return self
end
-----------------------------------------------------------------------
-- Create a floatedit with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for floatedit are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  \frz  [  0.  ]
-- Calls:
--  dialog:label_floatedit({ label = "\\frz", name = "frz", value = 0 })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_floatedit = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:floatedit(item)
    return self
end
-----------------------------------------------------------------------
-- Create a textbox with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for textbox are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  Data: [ Multiline ]
--        [ Content   ]
-- Calls:
--  dialog:label_textbox({ label = "Data:",
--                         height = 2,
--                         name = "data",
--                         text = "Multiline\nContent" })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_textbox = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:textbox(item)
    return self
end
-----------------------------------------------------------------------
-- Create a dropdown with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for dropdown are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     name_items  Change the item list dynamically
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  \frz  [  0.  ]
-- Calls:
--  dialog:label_floatedit({ label = "\\frz", name = "frz", value = 0 })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_dropdown = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:dropdown(item)
    return self
end
-----------------------------------------------------------------------
-- Create a checkbox with a label on the left instead of on the right.
--
-- This method receives parameters in a table.
-- All keys for checkbox are the same as in vanilla Aegisub, except
-- `label` are now for the label on the left.
-- `x`, `y`, and `width` are optional.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  Expand [x]
-- Calls:
--  dialog:label_checkbox({ label = "Expand",
--                          name = "expand",
--                          value = true })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_checkbox = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:checkbox(item)
    return self
end
-----------------------------------------------------------------------
-- Create a color with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for color are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  \frz  [  0.  ]
-- Calls:
--  dialog:label_floatedit({ label = "\\frz", name = "frz", value = 0 })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_color = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:color(item)
    return self
end
-----------------------------------------------------------------------
-- Create a coloralpha with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for coloralpha are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  \frz  [  0.  ]
-- Calls:
--  dialog:label_floatedit({ label = "\\frz", name = "frz", value = 0 })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_coloralpha = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:coloralpha(item)
    return self
end
-----------------------------------------------------------------------
-- Create an alpha with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for alpha are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key     label       Text to display for the label.
-- @key     name_label  Change the label dynamically.
-- @key     widths      By default, label and edit each takes up half
--                      of the width available. Change the widths of
--                      two classes using this key.
--
-- To create this dialog:
--  \frz  [  0.  ]
-- Calls:
--  dialog:label_floatedit({ label = "\\frz", name = "frz", value = 0 })
--
-- @return  self
-----------------------------------------------------------------------
dialog.label_alpha = function(self, item)
    if item.widths == nil then
        item.widths = { function(width) return math.ceil(width / 2) end,
                        function(width) return math.floor(width / 2) end }
    end
    local left, right = self:columns({ x = item.x, y = item.y, width = item.width, widths = item.widths })
    item.x = nil item.y = nil item.width = nil item.widths = nil

    left:label({ label = item.label })
    item.label = nil
    right:alpha(item)
    return self
end


local functions = {}

functions.subdialog_resolver = subdialog_resolver
functions.dialog_resolver = dialog_resolver
functions.dialog = dialog
functions.subdialog = subdialog
functions.vanilla_label_resolver = vanilla_label_resolver
functions.vanilla_value_resolver = vanilla_value_resolver
functions.vanilla_value_items_resolver = vanilla_value_items_resolver
functions.vanilla_value_label_resolver = vanilla_value_label_resolver
functions.vanilla_text_resolver = vanilla_text_resolver
functions.separator_resolver = separator_resolver
functions.floatable_resolver = floatable_resolver
functions.floatable_subdialog_resolver = floatable_subdialog_resolver
functions.floatable_subdialog = floatable_subdialog
functions.ifable_resolver = floatable_subdialog
functions.unlessable_resolver = floatable_subdialog
functions.columns_resolver = columns_resolver

return functions
