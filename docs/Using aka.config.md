## Using aka.config

There are several ways to use aka.config.  

### The minimum way to use aka.config

The minimum way to use aka.config, although not recommended, involves two simple functions, `read_config` and `write_config`.  
```lua
config = require("aka.config")
is_success, config_data = config.read_config("aka.MyMacro") -- This will read aka.MyMacro.json in the config directory
```
If everything works out to be fine, this will return `true` as well as the config data as Lua table. In case the config file doesn't exist (for example if the user install the script for the first time), or the config file is not valid JSON and can not be parsed, this will return `false`.  

When you want to save a config, you can do:  
```lua
is_success = config.write_config("aka.MyMacro", config_data = config_data)
```

### Using subfolders

aka.config will normally save configs to the config path specified by DependencyControl. However, you could also specify a subfolder for aka.config to put configs in.  
```lua
config = require("aka.config")
is_success, config_data = config.read_config("numbers", "aka.MyMacro")
is_success = config.write_config("numbers", "aka.MyMacro", config_data)
-- This will create a folder called aka.MyMacro in the config directory and save the data to numbers.json in the aka.MyMacro folder.
```

### Validate the config through aka.config

Additionally, you could pass a custom function to aka.config to validate the config. The minimum requirement for a validation function is simple. It takes in the config data as Lua table, and returns `true` if everything is good.  

For example, if you have `aka.MyMacro/numbers.json` and you want to make sure it contains an table (array) of numbers, you can do:  
```lua
config = require("aka.config")
config_validate = function(config_data)
    if not config_data or table.getn(config_data) ~= 0 then return false end
    for _, v in ipairs(config_data) do
        if type(v) ~= "number" then return false end
    end
    return true
end
is_success, config_data = config.read_config("numbers", "aka.MyMacro", config_validate)
```

### Using `edit_config_gui`

`edit_config_gui` is the third function of aka.config. It gives the user a GUI window to edit config, and supposedly it should be called in these two situations:  
* When `read_config` fails.  
* When the user asks to edit the config.  

`edit_config_gui` is defined as:  
```lua
edit_config_gui = function(config, subfolder, validation_func, ui_func, validation_func_ui, word_name_b, word_config_b, word_template, word_templates_b, config_templates, is_no_gui_init)
```

In its arguments:
* `config` and `subfolder` defines the config file location. This is the same as `config` and `subfolder` in `read_config` and `write_config`.  
* `validation_func` is similar to the validation function introduced in the last section. It takes the config data as Lua table, and it should return `true` if the data is valid. However, the difference is that when using `edit_config_gui`, the validation function must not return `false` if the data is invalid, but it must return error messages in the form an integer as error message count and a table of string as error messages. For example  
```lua
config_validate = function(config_data)
    if not config_data then
        return 1, { "Root array not found" }
    end
    if table.getn(config_data) ~= 0 then
        return 1, { "Root array empty" }
    end

    local error_msg_count local error_msg
    error_msg_count = 0 error_msg = {}
    for v, v in ipairs(config_data) do
        if type(v) ~= "number" then
            error_msg_count = error_msg_count + 1 table.insert(error_msg, "\"" .. w .. "\" at position " .. tostring(k) .. " not a number")
    end end
    if error_msg_count == 0 then return true end
    else return error_msg_count, error_msg end
end
```
* `word_name_b`, `word_config_b`, `word_template` and `word_templates_b` is referring to the texts displayed on the config GUI. `b` stands for bold. For example, you could have `"𝗠𝘆𝗠𝗮𝗰𝗿𝗼"`, `"𝗖𝗼𝗻𝗳𝗶𝗴"`, `"Preset"`, `"𝗣𝗿𝗲𝘀𝗲𝘁𝘀"` for these four arguments. Unfortunately, aka.config is written prior to the implementation of bold characters in Aegisub, and it is achieved using Mathematical Sans-Serif Bold characters from U+1D5D4 to U+1D607.  
* `config_templates` contains the presets for the config. It is provided as a Lua table with the preset name as key and raw JSON string as value. In case `is_no_gui_init`, you also need to have a string at integer key `1` which contains the preset name as the default preset.  
```lua
config_templates = { ["MyMacro Default"] = [[[
    1, 2, 3, 4, 5, 6
]
]],                  ["Another Preset"] = [[[
    1, 2, 3, 4, 5, 6, 7, 8, 9
]
]],                  "MyMacro Default" }
```
* The last `is_no_gui_init` can be set in case you want the user to be given a default preset without opening the GUI the first time they run the automation script.  

`edit_config_gui` will return `true` with config data as Lua table if everything is fine. It will return `false` if the user close or cancel the config GUI.  

Combining all three functions together, we now have a full config setup:  
```lua
config = require("aka.config")

config_validate = function(config_data)
    if not config_data then
        return 1, { "Root array not found" }
    end
    if table.getn(config_data) ~= 0 then
        return 1, { "Root array empty" }
    end

    local error_msg_count local error_msg
    error_msg_count = 0 error_msg = {}
    for v, v in ipairs(config_data) do
        if type(v) ~= "number" then
            error_msg_count = error_msg_count + 1 table.insert(error_msg, "\"" .. w .. "\" at position " .. tostring(k) .. " not a number")
    end end
    if error_msg_count == 0 then return true end
    else return error_msg_count, error_msg end
end
config_templates = { ["MyMacro Default"] = [[[
    1, 2, 3, 4, 5, 6
]
]],                  ["Another Preset"] = [[[
    1, 2, 3, 4, 5, 6, 7, 8, 9
]
]],                  "MyMacro Default" }

aegisub.register_macro("MyMacro/Do Something", "Do Something", function(sub, sel)
    local is_success

    if not config_data then
        is_success, config_data = config.read_config("numbers", "aka.MyMacro", config_validate)
        if not is_success then
            is_success, config_data = config.edit_config_gui("numbers", "aka.MyMacro", config_validate, nil, nil, "𝗠𝘆𝗠𝗮𝗰𝗿𝗼", "𝗖𝗼𝗻𝗳𝗶𝗴", "Preset", "𝗣𝗿𝗲𝘀𝗲𝘁𝘀", config_templates, true)
            if not is_success then aegisub.cancel() end
    end end
    do_something(sub, sel)
end)
aegisub.register_macro("MyMacro/Edit Numbers", "Edit Numbers for MyMacro", function()
    local is_success
    local config_data_

    is_success, config_data_ = config.edit_config_gui("numbers", "aka.MyMacro", config_validate, nil, nil, "𝗠𝘆𝗠𝗮𝗰𝗿𝗼", "𝗖𝗼𝗻𝗳𝗶𝗴", "Preset", "𝗣𝗿𝗲𝘀𝗲𝘁𝘀", config_templates)
    if is_success then config_data = config_data_
    else aegisub.cancel() end
end)
```
