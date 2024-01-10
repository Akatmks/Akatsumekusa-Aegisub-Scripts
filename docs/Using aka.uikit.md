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

### Basics logic

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
* In the last line, the dialog and buttons are displayed to the user.  

At every stage, you can call `resolve()` to retrieve a result in vanilla Aegisub.  

```lua
vanilla_dialog = dialog:resolve()
vanilla_buttons, vanilla_button_ids = buttons:resolve()
aegisub.dialog.display(vanilla_dialog, vanilla_buttons, vanilla_button_ids)
```
```moon
vanilla_dialog = dialog\resolve!
vanilla_buttons, vanilla_button_ids = buttons\resolve!
aegisub.dialog.display vanilla_dialog, vanilla_buttons, vanilla_button_ids
```

Or use it at the end to retrieve the result from display:  

```lua
button, result = adisplay(dialog, buttons):resolve()
```
```moon
button, result = (adisplay dialog, buttons)\resolve!
```

The usage and functions will be explained separately in following sections.  

### `aka.uikit.dialog`: Autofill `x`, `y` and `width` key

The first feature of `aka.uikit.dialog` is that you don't have to manually fill `x`, `y` and `width` key when creating dialog:  
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
* `dialog:label({ label = "AAE data:" })` creates a label, displaying text `"AAE data:"`. `dialog:label()` and all other class methods do not create a new copy and only returns itself. Both `dialog:label()` and `dialog = dialog:label()` yields the same result.  
* `dialog:textbox({ height = 4, name = "aae_data" })` creates a textbox, with the data name `"aae_data"`. Keys for all vanilla classes is the same as in vanilla dialog table. This also includes `height`, which by default is 1 for all classes. With a multiline class like `textbox`, you need to manually set the `height` key to the intended height.  
* `dialog:checkbox({ name = "expand", label = "Expand", value = true })` creates a checkbox with data name `expand`, `label` as `"Expand data"`, and default value set to `true`.  

The code in the example creates the same dialog table as following code in vanilla:  
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

Note that even if you have modified `x` or `y` key, the space the class originally occupies will still be left for it. If you want the class to be floating without occupying space, you could use the additional `dialog:floatable()` method introduced later in [XXX](XXX) section.  

### Automatically fill data into dialog



