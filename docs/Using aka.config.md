## Using aka.config

aka.config is an Aegisub module to handle config. It is built around the `Result` table introduced in aka.outcome. You may be able to get around by just copying the code examples below but you are suggested to give a brief look at aka.outcome's [document](Using%20aka.outcome.md).  

Also, if everything you need is storing a single value, and you want an interface that is as simple as possible. There is also [aka.singlesimple](Using%20aka.singlesimple.md) which is designed to to achieve just that.  

```lua
local aconfig = require("aka.config")
local outcome = require("aka.outcome")
local ok, err = outcome.ok, outcome.err
```
```moon
aconfig = require "aka.config"
outcome = require "aka.outcome"
ok, err = outcome.ok, outcome.err
```

### Loading and saving Dialog table

Let's start with the most basic scenario, dealing with the dialog table. You read from the config to see if previous config is available, or you use the default setting if no previous config is found. This can be achieved using the following Lua and MoonScript code:    
```lua
local config = aconfig.read_config("aka.TestScript")
    :unwrapOr({ index = "Value" })
```
```moon
config = aconfig.read_config "aka.TestScript"\unwrapOr
    index: "Value"
```
This code calls `aconfig.read_config` with `aka.TestScript`, which tells aka.config to look for a config in `?config/aka.TestScript.json`. `aconfig.read_config` returns a [`Result` object](Understanding%20aka.outcome), containing either an Ok with the config data or an Err with an error message. We want to use the default settings if config is not available, so we use `unwrapOr` to unwrap the `Result` object with default config table `{ index = "Value" }`.  

After you've displayed the dialog to the user, and you want to save the new dialog table to config:  
```lua
aconfig.write_config("aka.TestScript", config)
    :ifErr(function(err)
        aegisub.debug.out(1, "[aka.TestScript] Failed to save config to file\n" .. err) end)
```
```lua
aconfig.write_config("aka.TestScript", config)
    :ifErr(|err| aegisub.debug.out(1, "[aka.TestScript] Failed to save config to file\n" .. err))
```
```moon
with aconfig\write_config "aka.TestScript", config
    \ifErr (err) ->
        aegisub.debug.out 1, "[aka.TestScript] Failed to save config to file\n" .. err
```
This code calls `aconfig.save_config` with `aka.TestScript` and `config`, which tells aka.config to save the `config` table to `?config/aka.TestScript.json`. `aconfig.write_config` also returns a `Result` table. We want to make sure the config is saved so we use `unwrap` to raise an error in case of Err.  

### Loading and saving automation script settings

Instead of separating the load and save calls as in the case of dialog table, we want to perform this in one go—read the script setting from config, or use a default setting and save it to file if read fails—in case of script settings.  

This can be achieved using the following Lua, al and MoonScript code:  
```lua
local config = aconfig.read_config("aka.TestScript", "Settings")
    :andThen(function(config)
        if type(config[1]) == number then return
            ok(config)
        else return
            err("[aka.TestScript] Invalid config")
        end end)
    :orElseOther(function(_) return
        aconfig.write_config("aka.TestScript", "Settings", { 20 }) end)
    :unwrap()
```
```lua
local config = aconfig.read_config("aka.TestScript", "Settings")
    :andThen(|config|
        if type(config[1]) == number then
            rtn ok(config)
        else
            rtn err("[aka.TestScript] Invalid config")
        end)
    :orElseOther(||
        aconfig.write_config("aka.TestScript", "Settings", { 20 }))
    :unwrap()
```
```moon
config = with aconfig.read_config "aka.TestScript", "Settings"
    \andThen (config) ->
        if type(config[1]) == number
            ok config
        else
            err "[aka.TestScript] Invalid config"
    \orElseOther ->
        aconfig.write_config "aka.TestScript", "Settings", { 20 }
    \unwrap!
```
This code will first calls `aconfig.read_config` with `aka.TestScript` and `Settings`. When you call aka.config functions with two strings, aka.config will treat the first string as the folder name, so the config file in this case will be `?config/aka.TestScript/Settings.json`.  
And then if the config read successfully (literally `:andThen`), it will validate if the config is malformatted. `function(config) if type(config[1]) == number then return ok(config) else return err("[aka.TestScript] Invalid config") end end` checks if the first item in the config table is a number and then return either an Ok with the config table, or an Err with the error message.  
If any error occurs during the previous two steps, this `:orElseOther` will capture it, and call `aconfig.write_config` with `aka.TestScript`, `Settings`, and the default setting which in this case is `{ 20 }` to save the default setting to file. `aconfig.write_config` will return Ok with the config written if it runs successfully, which conveniently is what we exatly want.  
At last, we will `unwrap` the `Result` object either from the validation step or from the `aconfig.write_config` step, assigning the final config table to `config`.  

### Builtin JSON editor

```lua
local aconfig = require("aka.config").make_editor({
    display_name = "TestScript",
    presets = {
        "Twenty": { 20 },
        "Thirty": { 30 },
        "Twenty"
    }
})
```
```moon
aconfig = require("aka.config").make_editor
    display_name: "TestScript"
    presets:
        Twenty: { 20 }
        Thirty: { 30 }
        [1]: "Twenty"
```

```lua
local config = aconfig.read_and_validate_config_if_empty_then_default_or_else_edit("aka.TestScript", "Settings", validation_func)
    :ifErr(|| aegisub.cancel())
    :unwrap()
```
```moon
config = with aconfig.read_and_validate_config_if_empty_then_default_or_else_edit "aka.TestScript", "Settings", validation_func
    \ifErr -> aegisub.cancel!
    \unwrap!
```

```lua
local config = aconfig.read_and_validate_config_or_else_edit("aka.TestScript", "Settings", validation_func)
    :ifErr(|| aegisub.cancel())
    :unwrap()
```
```moon
config = with aconfig.read_and_validate_config_or_else_edit "aka.TestScript", "Settings", validation_func
    \ifErr -> aegisub.cancel!
    \unwrap!
```

```lua
local config = aconfig.edit_and_validate_config(config, validation_func)
    :ifErr(|| aegisub.cancel())
    :unwrap()
```
```moon
config = with aconfig.edit_and_validate_config "aka.TestScript", "Settings", validation_func
    \ifErr -> aegisub.cancel!
    \unwrap!
```

