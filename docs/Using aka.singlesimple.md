## Using aka.singlesimple

aka.singlesimple introduces a much simpler config interface than [aka.config](Using%20aka.config.md) to deal with the simplest case when only one config field is required.  

To use the aka.singlesimple, you can simple call `make_config` at the start of your script:
```lua
ss = require("aka.singlesimple")
config = ss.make_config("aka.actor", { "Style", "Actor", "Effect" }, "Actor")
```
・ The first parameter to `make_config` specify the config name. In this example, we use the name `aka.actor` so the config will be stored at `?config/aka.actor.json`.  
・ The second parameter is a table of all the possible values, in this example, that is `"Style"`, `"Actor"` and `"Effect"`.  
・ The third parameter is a table of the default value if the user runs the script for the first time, or if the value read from config is invalid.  

After that, you can use `Config.value` whenever you need to get the config:  
```lua
aegisub.debug.out(tostring(config:value()))
```

When you need to change the config, you can call `Config.setValue`:  
```lua
config:setValue("Effect")
```
This will be automatically saved to disk.  

There are some rare cases when the save fails so `Config.setValue` will actually return an `Result` for you to handle. It's probably okay 99% of the time not to worry about it, but if you want, you can at least make the user aware that something has gone wrong:  
```lua
config:setValue("Effect"):ifErr(function(error_message)
    aegisub.debug.out("[aka.actor] Failed to save the set value to disk\n" .. error_message) end)
```
Or if you are using MoonScript since this is a little bit complicated:  
```moon
with config
    \setValue "Effect"
    \ifErr (error_message) ->
        aegisub.debug.out("[aka.actor] Failed to save the set value to disk\n" .. error_message)
```
Or Akatsumekusa's Lua transpiler:  
```lua
config:setValue("Effect"):ifErr(|error_message|
    aegisub.debug.out("[aka.actor] Failed to save the set value to disk\n" .. error_message))
```
