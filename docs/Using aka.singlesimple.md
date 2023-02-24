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

Note that there are some rare cases when the save will fail, in which case the aka.singlesimple will print a message to `aegisub.debug.out`. If you want to handle it yourself, you can call `config:setValue2` instead which will then return a [`Result`](Using%20aka.outcome.md).  
