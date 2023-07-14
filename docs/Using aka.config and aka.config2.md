## Using aka.config and aka.config2

aka.config is a config module that features a builtin JSON editor with pretty JSON. aka.config2 provides the base JSON and file system functions while aka.config implements three readytouse config functions with GUI.  

A quick glance at the list of functions give you an idea about the script:  
```lua
-- Some of the functions available after requiring aka.config
aconfig = require("aka.config")
aconfig.read_config(config, config_supp)
aconfig.write_config(config, config_supp, config_data)

-- Some of the functions available after setting up builtin JSON editor
aconfig = aconfig.make_editor(param)
aconfig.read_and_validate_config_if_empty_then_default_or_else_edit_and_save(self, config, config_supp, validation_func)
aconfig.read_and_validate_config_or_else_edit_and_save(self, config, config_supp, validation_func)
aconfig.read_edit_validate_and_save_config(self, config, config_supp, validation_func)
```

The first two functions, `read_config` and `write_config`, are introduced in the [Saving Dialog table](#introduction-1-saving-dialog-table) chapter, while the three functions, `read_and_validate_config_if_empty_then_default_or_else_edit_and_save`, `read_and_validate_config_or_else_edit_and_save` and `read_edit_validate_and_save_config`, and introduced in the [Saving script configuration](#introduction-3-saving-script-configuration) chapter.  

aka.config are built around the `Result` table introduced in aka.outcome. You could use it by simply copying the code examples but you could give a brief look at [aka.outcome's document](Using%20aka.outcome.md).  

Also, if everything you need is storing a single enum, and you want an interface that is slightly simpler, or you want a config that could be synced across all scripts requesting the same config, there is also [aka.singlesimple](Using%20aka.singlesimple.md) module which is designed to to achieve just that.  

Imports aka.config and aka.outcome to the scope:  
```lua
local aconfig = require("aka.config")
local outcome = require("aka.outcome")
local ok, err = outcome.ok, outcome.err
```
```moon
aconfig = require "aka.config"
outcome = require "aka.outcome"
ok = outcome.ok
err = outcome.err
```

### Introduction 1: Saving Dialog table

This chapter introduces the basic `aconfig.read_config` and `aconfig.write_config` functions without GUI.  

To read config file or use a default config when error occurs:  
```lua
local config = aconfig.read_config("aka.TestMacro")
    :unwrapOr({ key1 = "Value", key2 = 0 })
```
```moon
with aconfig.read_config "aka.TestMacro"
    config = \unwrapOr { key1: "Value", key2: 0 }
```
* `aconfig.read_config` takes two parameters. The first parameter specify the subfolder for config file and is optional. The second parameter specify the filename for the config file as is shown in the code example below:  
    ```lua
    -- The config file will be read from "?config/aka.TestMacro.json"
    -- "?config" refers to `configDir`` in DependencyControl's config
    aconfig.read_config("aka.TestMacro")
    -- The config file will be read from "?config/aka.TestMacro2/Config.json"
    aconfig.read_config("aka.TestMacro2", "Config")
    ```
    ```moon
    -- The config file will be read from "?config/aka.TestMacro.json"
    -- "?config" refers to `configDir`` in DependencyControl's config
    aconfig.read_config "aka.TestMacro"
    -- The config file will be read from "?config/aka.TestMacro2/Config.json"
    aconfig.read_config "aka.TestMacro2", "Config"
    ```
* `aconfig.read_config` returns a `Result` table which could contains an `Ok` with the config table or an `Err` with an error message. In the case of Dialog table, you can unwrap the `Result` if it is `Ok`, or ignore the error message and use a default config with `Result.unwrapOr`.  

To save the Dialog table to file:  
```lua
aconfig.write_config("aka.TestMacro", config)
```
```moon
aconfig\write_config "aka.TestMacro", config
```
* Similar to `aconfig.read_config`, the first two parameters of `aconfig.write_config` specify the subfolder and filename for the config file. The first parameter is optional and can be omitted in place.  
* `aconfig.write_config` also returns a `Result` table, either an `Ok` with the config table, or an `Err` with an error message. You could use `Result.ifErr` to `aegisub.debug.out` a message when the save fails:  
    ```lua
    aconfig.write_config("aka.TestMacro", config)
        :ifErr(function(err)
            aegisub.debug.out(3, "[aka.TestMacro] Failed to save config to file\n")
            aegisub.debug.out(3, "[aka.TestMacro] " .. err .. "\n") end)
    ```
    ```lua
    aconfig.write_config("aka.TestMacro", config)
        :ifErr(|err|
            aegisub.debug.out(3, "[aka.TestMacro] Failed to save config to file\n")
            aegisub.debug.out(3, "[aka.TestMacro] " .. err .. "\n"))
    ```
    ```moon
    with aconfig\write_config "aka.TestMacro", config
        \ifErr (err) ->
            aegisub.debug.out 3, "[aka.TestMacro] Failed to save config to file\n"
            aegisub.debug.out 3, "[aka.TestMacro] " .. err .. "\n"
    ```

### Introduction 2: Validate your save

The last chapter introduces the basic use of `aconfig.read_config`:  
```lua
local config = aconfig.read_config("aka.TestMacro")
    :unwrapOr({ key1 = "Value", key2 = 0 })
```
```moon
with aconfig.read_config "aka.TestMacro"
    config = \unwrapOr { key1: "Value", key2: 0 }
```
The default value will be used if the read fails. Additional, you can validate the config and make sure it contains the right keys and right values. Create a validation function:  
```lua
local function validation_func(config_data)
    if type(config_data.key1) ~= "string" then
        return err("Invalid key1")
    elseif type(config_data.key2) ~= "number" or
           config_data.key2 < 0 then
        return err("Invalid key2")
    else
        return ok(config_data)
end end
```
```moon
validation_func = (config_data) ->
    if (type config_data.key1) ~= "string"
        err "Invalid key1"
    elseif (type config_data.key2) ~= "number" or
           config_data.key2 < 0
        err "Invalid key2"
    else
        ok config_data
```
In this example, key1 and key2 are checked and an `Err` is returned if the check fails. An `Ok` with config_data is returned when all the checks pass. By returning a `Result` table with config data, you will keep the `Result` going for further processes.  

Add the validation function to validate the config after `aka.read_config`:  
```lua
local config = aconfig.read_config("aka.TestMacro")
    :andThen(validation_func)
    :unwrapOr({ key1 = "Value", key2 = 0 })
```
```moon
local config
with aconfig.read_config "aka.TestMacro"
    with \andThen validation_func
        config = \unwrapOr { key1: "Value", key2: 0 }
```
・ `aconfig.read_config` reads config from `?config/aka.TestMacro`. It could return an `Ok` with config or an `Err` with an error message.  
・ If `Result.andThen` receives an `Ok` value, it sends the config to `validation_func` and collect the new `Result`. If `Result.andThen` receives an `Err` value, it passed the `Err` value down without invoking `validation_func`.  
・ `Result.unwrapOr` unwrap the `Ok` to get the config, or return the default value if `Result.andThen` gives it an `Err`. The value from `Result.unwrapOr` is then assigned to `config`.  

### Introduction 3: Saving script configuration

aka.config comes with three readytouse functions for saving script configurations. To use these function, you will first need to set up the JSON editor.  
Config presets need to be prepared for the user to choose from or reference including one selected as default. Create your config_preset either in Lua table or JSON string:  
```lua
local preset_1 = { 1, 2, 3, 4, 5 }
local preset_2 = "[2, 4, 6, 8, 10]"
```
```moon
preset_1 = { 1, 2, 3, 4, 5 }
preset_2 = "[2, 4, 6, 8, 10]"
```

Set up the JSON editor using the presets:  
```lua
local aconfig = aconfig.make_editor({
    display_name = "TestMacro",
    presets = {
        ["Amazing"] = preset_1,
        ["Brilliant"] = preset_2
    },
    default = "Amazing"
})
```
```moon
aconfig = aconfig.make_editor
    display_name: "TestMacro"
    presets:
        ["Amazing"]: preset_1
        ["Brilliant"]: preset_2
    default: "Amazing"
```
・ `TestMacro` is set as the display name of the config in the editor.  
・ The editor will have two presets, `"Amazing"` and `"Brilliant"` for the user to choose from or reference.  
・ `"Amazing"` is selected as the default preset and default config.  

With the editor set up, the three functions are available:  
```lua
aconfig.read_and_validate_config_if_empty_then_default_or_else_edit_and_save(self, config, config_supp, validation_func)
aconfig.read_and_validate_config_or_else_edit_and_save(self, config, config_supp, validation_func)
aconfig.read_edit_validate_and_save_config(self, config, config_supp, validation_func)
```
– `aconfig.read_and_validate_config_if_empty_then_default_or_else_edit_and_save` reads, validates and returns the config. If the config is not created or empty, the default preset specified in `make_editor` will be used. If other errors occurs or the validation fails, it will open the JSON editor for the user to figure out.  
– `aconfig.read_and_validate_config_or_else_edit_and_save` reads, validates and returns the config. If any errors occurs during the process, including creating the config for the first time, it will open the JSON editor for the user to either edit their config or apply a preset.  
– `aconfig.read_edit_validate_and_save_config` opens the JSON editor for the user to edit their config.  

The three functions can be invoked with the three paramters. Similar to `aconfig.read_config` introduced in the [first chapter](#introduction-1-saving-dialog-table), the first two parameters specify the subfolder and filename for the config file. The third parameter is for the validation function introduced in the [second chapter](#introduction-2-validate-your-save). Both the first and the third parameter is optional.  
```lua
-- The config file will be stored at "?config/aka.TestMacro.json"
-- "?config" refers to `configDir`` in DependencyControl's config
aconfig:read_edit_validate_and_save_config("aka.TestMacro", validation_func)
-- The config file will be stored at "?config/aka.TestMacro2/Config.json"
aconfig:read_edit_validate_and_save_config("aka.TestMacro2", "Config", validation_func)
```
```moon
-- The config file will be stored at "?config/aka.TestMacro.json"
-- "?config" refers to `configDir`` in DependencyControl's config
aconfig\read_and_and_config "aka.TestMacro", validation_func
-- The config file will be stored at "?config/aka.TestMacro2/Config.json"
aconfig\read_and_and_config "aka.TestMacro2", "Config", validation_func
```

The three functions requires `aegisub.dialog.display` for the JSON editor so they can only be called at script execution instead of initialisation. You can local a `config` outside macro processing function and assign to it inside the function:  
```lua
local config

config = nil
local function main(sub, sel, act)
    if not config
        config = aconfig:read_and_validate_config_if_empty_then_default_or_else_edit_and_save("aka.TestMacro", validation_func)
            :ifErr(aegisub.cancel)
            :unwrap()

    -- Main logic
end
```
```moon
local config
main = (sub, sel, act) ->
    if not config
        with aconfig\read_and_validate_config_if_empty_then_default_or_else_edit_and_save "aka.TestMacro", validation_func
            with \ifErr aegisub.cancel
                config = \unwrap!

    -- Main logic
```
・ A variable named `config` is set up outside the macro processing function. If it is nil, `aconfig.read_and_validate_config_if_empty_then_default_or_else_edit_and_save` is called at the start of the macro processing function to read config to that variable. 
・ `aconfig.read_and_validate_config_if_empty_then_default_or_else_edit_and_save` returns `Ok` with the config either when the config is read and validated successfully, or the user creates a config that's successfullly validated.
It will only return `Err` when the user close the config editor.  
・ When the user closes the config editor and cancels, `Result.ifErr` captures the `Err` and invokes `aegisub.cancel`. Similar to the validation function in [chapter 2](#introduction-2-validate-your-save), you pass the function to `Result.ifErr` instead of `Result.ifErr(aegisub.cancel())`.  
・ After that, you can `unwrap` the `Result` and save it to the `config` variable outside macro processing function.  

Additionally, you can also create a macro processing function to let the user open the config editor at any time using `read_edit_validate_and_save_config`:  
```lua
local config

config = nil
local function edit_config(sub, sel, act)
    config = aconfig:read_edit_validate_and_save_config("aka.TestMacro", validation_func)
        :ifErr(aegisub.cancel)
        :unwrap()
end
```
```moon
local config
edit_config = (sub, sel, act) ->
    with aconfig\read_edit_validate_and_save_config "aka.TestMacro", validation_func
        with \ifErr aegisub.cancel
            config = \unwrap!
```
・ This is the same idea as the previous example. One detail to notice is that if `aegisub.cancel` is invoked at `Result.ifErr`, the assignment to `config` will not happen. This is the same in Lua and MoonScript, although MoonScript makes it more obvious that it is the case.  

This is a complete example of a macro using aka.config:  
```lua
local DepCtrl = require("l0.DependencyControl")
DepCtrl = DepCtrl({
    feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "aka.config" },
        { "aka.outcome" }
    }
})
local aconfig, outcome = DepCtrl:requireModules()
local ok, err = outcome.ok, outcome.err


local aconfig = aconfig.make_editor({
    display_name = "TestMacro",
    presets = {
        ["Amazing"] = { 1, 2, 3, 4, 5 },
        ["Brilliant"] = { 2, 4, 6, 8, 10 }
    },
    default = "Amazing"
})
local validation_func = function(config_data)
    for i, v in ipairs(config_data) do
        if type(v) ~= "number" then
            return err("[aka.Testing] Invalid value at position " .. tostring(i))
    end
    return ok(config_data)
end

local config = nil


function main(sub, sel, act)
    if not config then
        config = aconfig:read_and_validate_config_if_empty_then_default_or_else_edit_and_save("aka.TestMacro", validation_func)
            :ifErr(aegisub.cancel)
            :unwrap()
    end

    -- The macro's main logic
    return sel, act
end

function edit_config()
    config = aconfig:read_edit_validate_and_save_config("aka.TestMacro", validation_func)
        :ifErr(aegisub.cancel)
        :unwrap()
end


DepCtrl:registerMacros({
    { "TestMacro", "TestMacro", main },
    { "Edit config", "Edit config for TestMacro", edit_config }
})
```
```moon
DepCtrl = require "l0.DependencyControl"
DepCtrl = DepCtrl {
    feed: "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "aka.config" },
        { "aka.outcome" }
    }
}

aconfig, outcome = DepCtrl\requireModules!
ok = outcome.ok
err = outcome.err


aconfig = aconfig.make_editor
    display_name: "TestMacro"
    presets:
        ["Amazing"]: { 1, 2, 3, 4, 5 }
        ["Brilliant"]: { 2, 4, 6, 8, 10 }
    default: "Amazing"

validation_func = (config_data) ->
    for i, v in ipairs config_data
        if (type v) ~= "number"
            return err "[aka.Testing] Invalid value at position " .. tostring i
    ok config_data

local config


main = (sub, sel, act) ->
    if not config
        with aconfig\read_and_validate_config_if_empty_then_default_or_else_edit_and_save "aka.TestMacro", validation_func
            with \ifErr aegisub.cancel
                config = \unwrap!

    -- The macro's main logic
    sel, act

edit_config = () ->
    with aconfig.read_edit_validate_and_save_config "aka.TestMacro", validation_func
        with \ifErr aegisub.cancel
            config = \unwrap!


DepCtrl:registerMacros {
    { "TestMacro", "TestMacro", main },
    { "Edit config", "Edit config for TestMacro", edit_config }
}
```

There are also many functions exposed in aka.config, for example `aconfig.json.encode3`, `aconfig.json.decode3`, `aconfig.config_dir`, `aconfig.read_config_string` and `aconfig.write_config_string`. These are available after requiring aka.config. There is also `aconfig.edit_config` which is the function for the builtin JSON editor. You could build a better config window with switches instead of raw JSON and only fall back to the builtin JSON editor when the config fails to deserialise.  
