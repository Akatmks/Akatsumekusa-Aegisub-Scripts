## Using aka.singlesimple

aka.singlesimple introduces a much simpler config interface than [aka.config](Using%20aka.config%20and%20aka.config2.md). It stores one enum per config and the enum is synced across all scrips requesting the same config.  

To use the aka.singlesimple, you can call `make_config` at the start of your script:
```lua
ss = require("aka.singlesimple")
config = ss.make_config("aka.actor", { "Style", "Actor", "Effect" }, "Actor")
```
```moon
ss = require "aka.singlesimple"
config = ss.make_config "aka.actor", { "Style", "Actor", "Effect" }, "Actor"
```
* The first parameter to `make_config` specifies the config name. In this example, we use the name `aka.actor` and the config will be stored at `?config/aka.actor.json`. `?config` is linked to `configDir` specified in DependencyControl's config.  
* The second parameter is a table listing all the possible values.  
* The third parameter is the default value and the fallback value for the enum. It must be one of the values specified in the second parameter.  

After that, you can use `Config.value` to get the value:  
```lua
aegisub.debug.out(tostring(config:value()))
```  
```moon
aegisub.debug.out tostring config\value!
```

When you need to change the value, you can call `Config.setValue`:  
```lua
config:setValue("Effect")
```
```moon
config\setValue "Effect"
```

Note that there are some rare situations when some procedures may fail, in which case aka.singlesimple will print a message to `aegisub.debug.out` and occasionally `aegisub.cancel`. If you want to handle the error yourself, you can call `Config.value2` and `Config.setValue2`, which will return a `Result` table from [aka.outcome](Using%20aka.outcome.md).  
