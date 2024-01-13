## Using aka.uikit

aka.uikit is a collection of different automation function for creating UI in Aegisub dialog.  

Imports aka.uikit to the scope:  
```lua
local uikit = require("aka.uikit")
local adialog, abuttons, adisplay = uikit.dialog, uikit.buttons, uikit.display
```
```moon
with require "aka.uikit"
    adialog = .dialog
    abuttons = .buttons
    adisplay = .display
```

In this tutorial, what's known otherwise as widgets or controls in Aegisub dialog will be referred to as classes, including vanilla classes such as `edit`, `floatedit` and `dropdown` as well as classes unique to aka.uikit such as `separator` and `grid`. All the options for classes such as `x`, `y`, `name`, `label`, `value` will be referred to as keys.  

If you want a glance at a complete example using aka.uikit, see [aka.Sandbox](../macros/aka.Sandbox.lua).  

### Table of Contents

– [Basic components](#basic-components)  
– [`aka.uikit.dialog`: Autofill `x`, `y` and `width` key](#akauikitdialog-autofill-x-y-and-width-key)  
– [`aka.uikit.dialog`: Additional classes](#akauikitdialog-additional-classes)  
– [`aka.uikit.dialog`: Automatically filling data into dialog](#akauikitdialog-automatically-filling-data-into-dialog)  
– [`aka.uikit.buttons`: Create buttons with button_ids](#akauikitbuttons-create-buttons-with-button_ids)  
– [`aka.uikit.display`: Basic use and `display.repeatUntil()`](#akauikitdisplay-basic-use-and-displayrepeatuntil)  

### Basic components

aka.uikit has three main components, `aka.uikit.dialog`, `aka.uikit.buttons` and `aka.uikit.display`:  

```lua
dialog = adialog.new({ width = 6 })
                :label({ label = "Hello World!" })
buttons = abuttons.new()
                  :ok("OK")
                  :close("Cancel")
display = adisplay(dialog, buttons)
```
```moon
with dialog = adialog { width = 6 }
    \label { label = "Hello World!" }
with buttons = abuttons!
    \ok "OK"
    \close "Cancel"
display = adisplay dialog, buttons
```
* In the first two lines, a dialog is created with width of 6, containing only one class, a label that will display "Hello World!".  
* In the following three lines, an `"OK"` and a `"Cancel"` button are created.  
* In the last line, the dialog and buttons are (ready to be) displayed to the user.  

At every stage, you can call `resolve()` to retrieve a result in vanilla Aegisub.  

```lua
vanilla_dialog = dialog:resolve()
vanilla_buttons, vanilla_button_ids = buttons:resolve()
```
```moon
vanilla_dialog = dialog\resolve!
vanilla_buttons, vanilla_button_ids = buttons\resolve!
```

Or use it at the end to display the dialog to the user and retrieve the result:  

```lua
button, result = adisplay(dialog, buttons):resolve()
```
```moon
button, result = (adisplay dialog, buttons)\resolve!
```

The usage and functions of each component will be explained separately in following sections.  

### `aka.uikit.dialog`: Autofill `x`, `y` and `width` key

The first feature of `aka.uikit.dialog` is to autofill `x`, `y` and `width` key when creating dialog:  
```lua
dialog = adialog.new({ width = 5 })
                :label({ label = "AAE data:" })
                :textbox({ height = 4, name = "aae_data" })
                :checkbox({ name = "expand", label = "Expand", value = true })
```
```moon
with dialog = adialog { width: 5 }
  \label { label: "AAE data:" }
  \textbox { height: 4, name: "aae_data" }
  \checkbox { name: "expand", label: "Expand", value: true }
```
* `adialog.new({ width = 5 })`: A new dialog table is created with the width of 5. All three child classes will thus have a `width` of 5 and arranged top down in the order they are called. `adialog.new({ width = 5 })` is the same as `adialog({ width = 5 })`.  
* `dialog:label({ label = "AAE data:" })` creates a label, displaying text `"AAE data:"`. `dialog:label` and all other class methods do not create a new copy and only returns itself. Both `dialog:label()` and `dialog = dialog:label()` yields the same result.  
* `dialog:textbox({ height = 4, name = "aae_data" })` creates a textbox, with the data name `"aae_data"`. Keys for all vanilla classes is the same as in vanilla dialog table. This also includes `height`, which by default is 1 for all classes. With a multiline class like `textbox`, you need to manually set the `height` key to the intended height.  
* `dialog:checkbox({ name = "expand", label = "Expand", value = true })` creates a checkbox with data name `expand`, `label` as `"Expand data"`, and default value set to `true`.  

The code in the example creates the same dialog as following dialog table created in vanilla:  
```lua
dialog = { { class = "label", x = 0, y = 0, width = 5, label = "AAE data" },
           { class = "textbox", x = 0, y = 1, width = 5, height = 4, name = "aae_data" },
           { class = "checkbox", x = 0, y = 5, width = 5, name = "expand", label = "Expand", value = true } }
```

You could also manually override the `x`, `y` or `width` key:  
```lua
dialog:checkbox({ x = 1, width = 4, name = "expand", label = "Expand", value = true })
```
```moon
dialog\checkbox { x: 1, width: 4 name: "expand", label: "Expand", value: true }
```

You can also a function to modify the `x`, `y` or `width` key. The function will receive the key's natural value as parameter:  
```lua
dialog:checkbox({ x = function(x) return x + 1 end,
                  width = function(width) return width - 1 end,
                  name = "expand",
                  label = "Expand",
                  value = true })
```
```moon
dialog\checkbox
    x: (x) -> x + 1
    width: (width) -> width - 1
    name: "expand"
    label: "Expand"
    value: true
```

Note that even if you have modified `x` or `y` key, the space the class originally occupies will still be left for it. If you want the class to be floating without occupying space, you could use [`dialog:floatable`](#dialogfloatable) class. 

### `aka.uikit.dialog`: Additional classes

`aka.uikit.dialog` introduces additional classes in addition to vanilla ones.  

#### `dialog.separator`

```lua
-- Create a separator or an empty space on the dialog.
-- Note that if there is no more classes below separator, the separator
-- will not have any effect. To create an empty space at the bottom of
-- dialog, use an empty label.
--
-- This method receives parameters in a table.
-- @key     [height=1]  vertical height of the separator
--
-- @return  self
```

Example:  
```lua
dialog:separator({ height = 2 })
```
```moon
dialog\separator { height: 2 }
```

#### `dialog.floatable`

Classes inside a floatable class does not occupy spaces in the main dialog.  

```lua
-- Create a subdialog for floating classes
--
-- @return  subdialog   Call methods such as `label` from this
--                      subdialog to add floating classes.
--                      All floating classes should specify their `x`,
--                      `y` and `width` keys.
```

Example:
```lua
subdialog = dialog:floatable()
subdialog:label({ x = 10, y = 10, width = 3, label = "Floating" })
subdialog:label({ x = 10, y = 11, width = 3, label = "Floating" })
```
```moon
subdialog = dialog\floatable!
subdialog\label { x: 10, y: 10, width: 3, label: "Floating" }
subdialog\label { x: 10, y: 11, width: 3, label: "Floating" }
```

#### `dialog.ifable` and `dialog.unlessable`

Classes inside an ifable class will only display if the value specified by the name in ifable is truthy.

```lua
-- Create a subdialog only when value with the name in dialog data is
-- truthy
--
-- This method receives parameters in a table.
-- @key     name        The name for the value in the dialog data.
--                      If the value is truthy, classes in the
--                      subdialog will be displayed.
--
-- @return  subdialog   Call methods such as `label` from this
--                      subdialog to add to ifable.
```

Classes inside an unlessable class will only display if the value specified by the name in unlessable is falsy.

```lua
-- Create a subdialog only when value with the name in dialog data is
-- falsy
--
-- This method receives parameters in a table.
-- @key     name        The name for the value in the dialog data.
--                      If the value is falsy, classes in the
--                      subdialog will be displayed.
--
-- @return  subdialog   Call methods such as `label` from this
--                      subdialog to add to unlessable.
```

An example of using `dialog.ifable` with `display.repeatUntil()` is as below:  
```lua
dialog = adialog.new({ width = 5 })
                :load_data(previous_data)
-- If err_msg is truely, the label_edit will be displayed with text of err_msg
subdialog = dialog:ifable({ name = "err_msg" })
subdialog = subdialog:label_edit({ label = "Error occuried", name = "err_msg" })
dialog = dialog:label_edit({ label = "URL", name = "url" })

buttons = abuttons.ok("Connect"):close("Cancel")

result = adisplay(dialog, buttons)
    :repeatUntil(function(button, result)
        response, err, msg = request.send(result["url"], { method = "GET" })
        if not response then
            result["err_msg"] = "No response"
            return err(result)
        elseif response.code ~= 200 then
            result["err_msg"] = "Target responded with code " .. tostring(response.code)
            return err(result)
        else
            return ok(result)
        end end)
```
```moon
with dialog = adialog.new { width: 5 }
  \load_data previous_data
  -- If err_msg is truely, the label_edit will be displayed with text of err_msg
  with subdialog = \ifable { name: "err_msg" }
    \label_edit { label: "Error occuried", name: "err_msg" }
  \label_edit { label: "URL", name: "url" }

with buttons = abuttons.ok "Connect"
  \close "Cancel"

with result = adisplay display, buttons
  \repeatUntil (button, result) ->
    response, err, msg = request.send result["url"], { method: "GET" }
    if not response
      result["err_msg"] = "No response"
      return err result
    elseif response.code ~= 200
      result["err_msg"] = "Target responded with code " .. tostring response.code
      return err result
    else
      return ok result
```

#### `dialog.columns` or `dialog.row`

By default, `aka.uikit.dialog` arranges classes from top to bottom. This method creates columns and enables arranging classes side by side.  

```lua
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
```

Example:
```lua
left, middle, right = dialog:columns({ widths = { 2, 2, 3 } })
left:label({ label = "Left" })
middle:label({ label = "Middle" })
right:edit({ name = "edit", text = "Right" })
```
```moon
left, middle, right = dialog\columns { widths = { 2, 2, 3 } }
left\label { label: "Left" }
middle\label { label: "Middle" }
right\edit { name: "edit", text: "Right" }
```

#### `label_edit`, `label_intedit`, `label_floatedit`, `label_textbox`, `label_dropdown`, `label_checkbox`, `label_color`, `label_coloralpha` and `label_alpha`

It's common for automation scripts to have a edit, intedit, floatedit, etc with a label on the left. This class is a oneliner combining `dialog:columns` and respected classes.  

```lua
-- Create an <edit> with a label on the left.
--
-- This method receives parameters in a table.
-- All keys for <edit> are the same as in vanilla Aegisub.
-- `x`, `y`, and `width` are optional.
-- Additionally:
-- @key label   Text to display for the label
-- @key widths  By default, label and <edit> each takes up half of the
--              width available.
--
-- @return  self
```

Examples:
```lua
dialog:label_edit({ label = "\\fn", name = "fn", text = "Arial" })
dialog:label_floatedit({ label = "\\frz", name = "frz", value = 0 })
dialog:label_textbox({ label = "Data:", height = 2, name = "data", text = "Multiline\nContent" })
dialog:label_checkbox({ label = "Expand", name = "expand", value = true })
```
```moon
dialog\label_edit { label: "\\fn", name: "fn", text: "Arial" }
dialog\label_floatedit { label: "\\frz", name: "frz", value: 0 }
dialog\label_textbox { label: "Data:", height: 2, name: "data", text: "Multiline\nContent" }
dialog\label_checkbox { label: "Expand", name: "expand", value: true }
```

### `aka.uikit.dialog`: Automatically filling data into dialog

It's common for scripts to prefill the dialog with contents, either data from the active subtitle line, or settings from previous run. In vanilla, this is often performed as below:  
```lua
dialog = { { class = "floatedit",   x = 0, y = 0, width = 5,
                                    name = "frz", value = line_data["frz"] },
           { class = "textbox",     x = 0, y = 1, width = 5, height = 3,
                                    name = "command", value = previous_data["command"] } }
```

`aka.uikit.dialog` makes it easy using the `dialog:load_data()` method:  
```lua
dialog = adialog.new({ width = 5 }
                :load_data(line_data)
                :load_data(previous_data)
                :floatedit({ name = "frz" })
                :textbox({ height = 3, name = "command" })
)
```
```moon
with dialog = adialog { width: 5 }
  \load_data line_data
  \load_data previous_data
  \floatedit { name: "frz" }
  \textbox { height: 3, name: "command" }
```

The data should be in key-value pairs, in the same format as the second return from vanilla `aegisub.dialog.display`.  

`dialog:load_data()` overrides the default values set in the dialog or values from previous call of `dialog:load_data()`. That means if you want to use values from previous run but also need a default value when the user runs the script for the first time, you can write the default value directly to each classes:  
```lua
dialog = adialog.new({ width = 4 })
                :load_data(previous_data) -- could be nil
                :label_floatedit({ label = "Strength", name = "strength", min = 0, value = 2 }) -- Default value
```
```moon
dialog = adialog.new { width: 4 }
dialog\load_data previous_data -- could be nil
dialog\label_floatedit { label: "Strength", name: "strength", min: 0, value: 2 } -- Default value
```

Or have a separate default table:  
```lua
default_data = { "strength" = 2 }

dialog = adialog.new({ width = 4 })
                :load_data(default_data)
                :load_data(previous_data) -- could be nil
                :label_floatedit({ label = "Strength", name = "strength", min = 0 })
```
```moon
default_data =
  strength: 2

dialog = adialog.new { width: 4 }
dialog\load_data default_data
dialog\load_data previous_data -- could be nil
dialog\label_floatedit { label: "Strength", name: "strength", min: 0, value: 2 } -- Default value
```

### `aka.uikit.buttons`: Create buttons with button_ids

`aka.uikit.buttons` automates the process of writing button_ids. Instead of this code in vanilla:  

```lua
buttons = { "Apply", "&Validate", "&Help", "Close" }
button_ids = { ["ok"] = "Apply", ["close"] = "Close", ["help"] = "&Help" }
```

You can create buttons with `aka.uikit.buttons` as below:  

```lua
buttons = abuttons.ok("Apply")
                  :regular("&Validate")
                  :help("&Help")
                  :close("Close")
```
```moon
buttons = abuttons!
buttons\ok "Apply"
buttons "&Validate"
buttons\help "&Help"
buttons\close "Close"
```

#### `buttons.new()` and `buttons.__call()`

To create a `aka.uikit.buttons` instance, call `new`, call `aka.uikit.buttons` itself, or call any of the buttons using `.` instead of `:` or `\`:  

```lua
buttons1 = abuttons.new()
buttons2 = abuttons()
buttons3 = abuttons.ok("Apply")
buttons4 = abuttons.regular("L&eft")
```
```moon
buttons1 = abuttons.new!
buttons2 = abuttons!
buttons3 = abuttons.ok "Apply"
buttons4 = abuttons.regular "L&eft"
```

#### `buttons.ok()`, `buttons.close()`, `buttons.cancel()` and `buttons.help()`

These are special buttons in Aegisub that they have `button_ids` and will be triggers when the user presses keys such as Enter, return or escape on keyboard, in addition to clicking the button using mouse. For main functional buttons, these should be preferred over regular buttons explained in the next section.  
– `buttons.ok()` triggers when the user presses Enter or return.  
– `buttons.close()` triggers when the user presses escape.  
– `buttons.cancel()` is mutually exclusive with `buttons.close()`. The difference between the two is that when the user presses escape, in `buttons.close()` the display returns the name of the close button, but in `buttons.cancel()` the display returns `false`.  
– `buttons.help()` displays a special help button on Mac.  

Buttons are arranged in the order the methods are called.  

```lua
buttons:ok("Apply")
buttons:close("Close")
```
```lua
buttons\ok "Apply"
buttons\close "Close"
```

#### `buttons.regular()`, `buttons.extra()`, and `buttons.__call()`

To create a regular button, call `buttons.regular()`, `buttons.extra()`, or just call the instance itself.  

```lua
buttons:regular("Configurate")
buttons:extra("Configurate")
buttons("Configurate")
```
```moon
buttons\regular "Configurate"
buttons\extra "Configurate"
buttons "Configurate"
```

Note that direct calling of the instance itself is only available after the instance is initialised. Which means:  
```lua
-- This is valid.
buttons1 = aka.uikit.buttons.ok("Confirm")
buttons1("Extra Button")
-- This is invalid.
-- This is not calling a buttons instance but calling the buttons class.
-- This only creates a buttons instance but do not add any buttons to the instance.
buttons2 = aka.uikit.buttons("Left Button")
-- This is valid.
buttons3 = aka.uikit.buttons.regular("Left button")
```
```moon
-- This is valid.
buttons1 = aka.uikit.buttons.ok "Confirm"
buttons1 "Extra Button"
-- This is invalid.
-- This is not calling a buttons instance but calling the buttons class.
-- This only creates a buttons instance but do not add any buttons to the instance.
buttons2 = aka.uikit.buttons "Left Button"
-- This is valid.
buttons3 = aka.uikit.buttons.regular "Left button"
```

### `aka.uikit.display`: Basic use and `display.repeatUntil()`

#### `display.resolve()`

To start a display, call `aka.uikit.display` or `aka.uikit.display.new`:  

```moon
-- Start a display
--
-- @param   dialog  dialog from aka.uikit.dialog
-- @param   buttons buttons from aka.uikit.buttons
--
-- @return  display
```

To get a `button` and `result` similar to vanilla in `aka.uikit.display`, use `display.resolve()`:  

```moon
-- Display and dialog and get button and result
--
-- @return  button  Same as in vanilla aegisub.dialog.display
-- @return  result  Same as in vanilla aegisub.dialog.display
```

Examples:  
```lua
button, result = adisplay(dialog, buttons):resolve()
```
```moon
button, result = (adisplay dialog, buttons)\resolve!
```

#### `display.repeatUntil()`

```moon
-- Repeatly display the dialog until f returns ok(result)
-- 
-- @param   f       function that takes in button and result.
--                  It shall returns ok() if the dialog is accepted.
--                  Any contents in the ok() is returns out of
--                  `repeatUntil()` so you could possibly preprocess
--                  the data inside this function.
--                  It shall returns err() if the dialog is rejected
--                  and the dialog is redisplayed to the user.
--                  If you want to display an error message or modify
--                  the dialog, you can pass data inside err() and it
--                  will be loaded using `dialog:loadData()`.
--
-- @return  Result  Ok if the dialog is accepted by f. Contains the
--                  data returned from f.
--                  Err if the user cancel the operation.
```

Examples:  
```lua
dialog = adialog.new({ width = 5 })
                :load_data(previous_data)
subdialog = dialog:ifable({ name = "err_msg" })
subdialog = subdialog:label_edit({ label = "Error occuried", name = "err_msg" })
dialog = dialog:label_edit({ label = "URL", name = "url" })

buttons = abuttons.ok("Connect"):close("Cancel")

result = adisplay(dialog, buttons)
    :repeatUntil(function(button, result)
        -- If the user clicked "Cancel", `repeatUntil()`` will return
        -- without calling this function
        response, err, msg = request.send(result["url"], { method = "GET" })
        if not response then
            result["err_msg"] = "No response"
            return err(result)
        elseif response.code ~= 200 then
            result["err_msg"] = "Target responded with code " .. tostring(response.code)
            return err(result)
        else
            return ok(result)
        end end)
```
```moon
with dialog = adialog.new { width: 5 }
  \load_data previous_data
  with subdialog = \ifable { name: "err_msg" }
    \label_edit { label: "Error occuried", name: "err_msg" }
  \label_edit { label: "URL", name: "url" }

with buttons = abuttons.ok "Connect"
  \close "Cancel"

with result = adisplay dialog, buttons
  \repeatUntil (button, result) ->
    -- If the user clicked "Cancel", `repeatUntil()`` will return
    -- without calling this function
    response, err, msg = request.send result["url"], { method: "GET" }
    if not response
      result["err_msg"] = "No response"
      return err result
    elseif response.code ~= 200
      result["err_msg"] = "Target responded with code " .. tostring response.code
      return err result
    else
      return ok result
```

#### `display.loadResolveAndSave()`

```moon
-- Load the content from previous run, display the dialog and save
-- the content for next run.
-- This will only save the content if a button other than close or
-- cancel is triggered.
--
-- @param   [name]    The subfolder you would want to put the config
-- @param   name_supp The name for the config file without the file
--                    extension.
--                    The subfolder name is an optional parameter and
--                    can be ommited in place. Calling the method as
--                    `display\loadResolveAndSave filename` is A-OK.
--
-- @return  button    Same as in vanilla aegisub.dialog.display
-- @return  result    Same as in vanilla aegisub.dialog.display
```

This will automatically „Recall last“ in every run. However, this won't work if the dialog contains data unique to active or selected lines since the previous data is loaded at the very last, in which case you should write it manually with `dialog.load_data()`. You won't need this function either if you want to write an advanced preset system as in a lot of lyger's scripts.  

#### `display.loadRepeatUntilAndSave()`

```moon
-- Load the contents from previous run, repeatly display the dialog
-- until f returns ok(result), and then save the result for next run.
-- 
-- @param   [name]    The subfolder you would want to put the config
-- @param   name_supp The name for the config file without the file
--                    extension.
--                    The subfolder name is an optional parameter and
--                    can be ommited in place. Calling the method as
--                    `display\loadRepeatUntilAndSave filename, f` is
--                    A-OK.
-- @param   f         Function that takes in button and result.
--                    It shall returns ok(result) if the dialog is
--                    You may preprocess the data for further use since
--                    the contents inside ok() will be returned out of
--                    `loadRepeatUntilAndSave`. However, you also need
--                    to return the key-value pairs necessay for the
--                    next dialog run.
--                    It shall returns err() if the dialog is rejected
--                    and the dialog is redisplayed to the user.
--                    If you want to display an error message or modify
--                    the dialog, you can pass data inside err() and it
--                    will be loaded using `dialog:loadData()`.
--
-- @return  Result    Ok if the dialog is accepted by f. Contains the
--                    data returned from f.
--                    Err if the user cancel the operation.
```

An example of a complete use of aka.uikit is available at [aka.Sandbox](../macros/aka.Sandbox.lua).  
