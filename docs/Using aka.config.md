## Using aka.config

There are several ways to use aka.config.  

### The basic of basic 

The basic of aka.config involves two simple functions, `read_config` and `write_config`.  
```lua
config = require("aka.config")
is_success, config_data = config.read_config("aka.MyMacro") -- This will read the config from aka.MyMacro.json in the config directory
```
If everything works out to be fine, this will return `true` as well as the config data as Lua table. In case the config file doesn't exist (for example if the user install the script for the first time), or the config file is not valid JSON and can not be parsed, this will return `false` and `nil`.  

When you want to save a config, you can do:  
```lua
is_success = config.write_config("aka.MyMacro", config_data) -- This will save the table to aka.MyMacro.json in the config directory
```

### Using subfolders

aka.config will normally save configs to the config path specified by DependencyControl. However, you could also specify a subfolder for aka.config to put configs in.  
```lua
config = require("aka.config")
-- This will read the config from numbers.json in the aka.MyMacro directory in the config directory.
is_success, config_data = config.read_config("numbers", "aka.MyMacro")
-- This will create a folder called aka.MyMacro in the config directory and save the data to numbers.json in the aka.MyMacro folder.
is_success = config.write_config("numbers", "aka.MyMacro", config_data)
```

By this point, some of you may be wondering why subfolder is placed as the second argument of `write_config`, while in the previous section the second argument of `write_config` is `config_data`. If you are familiar with C/C++, you can understand it as function overloading. `subfolder` should be a string while `config_data` should be a table. Otherwise, you can just understand it as omitting optional arguments in place. This applies to `read_config`, `write_config` and also the `edit_config_gui` function you will learn about later in this tutorial.  

### Validate the config through aka.config

You could pass a custom function to aka.config to validate your config. The minimum requirement for a validation function is simple. It takes in the config data as Lua table, and returns `true` if everything is good.  

For example, if you have `aka.MyMacro/numbers.json` and you want to make sure it contains an table (array) of numbers, you can do:  
```lua
config = require("aka.config")
config_validate = function(config_data) -- You could also write it as `function config_validate(config_data)` if you are more familiar with that
    if not config_data or table.getn(config_data) ~= 0 then return false end
    for _, v in ipairs(config_data) do
        if type(v) ~= "number" then return false end
    end
    return true
end
is_success, config_data = config.read_config("numbers", "aka.MyMacro", config_validate)
```

### Using `edit_config_gui`

`edit_config_gui` is the third function of aka.config. It will open up a GUI window with current config in raw JSON on the left and the templates or presets on the right for the user to edit. The idea is that you should call this function when:  
* `read_config` fails.  
    * It could be the case that the user has just opened the automation script for the first time. If you want to generate a default config without opening the GUI, you will later find an option to let you to that.  
    * It could also the case that the user has manually edited the config outside Aegisub and it either fails to parse or fails to pass the validation function.  
* the user asks to edit the config.  

`edit_config_gui` is defined as:  
```lua
function(config, subfolder, validation_func, ui_func, validation_func_ui, words, config_templates, is_no_gui_init)
```

In its arguments:
* `config` and `subfolder` defines the config file location. This is the same as `config` and `subfolder` in `read_config` and `write_config`.  
* `validation_func` is similar to the validation function introduced in the last section. It takes the config data as Lua table, and it should return `true` if the data is valid. However, the difference is that when using `edit_config_gui`, the validation function must not return `false` if the data is invalid, but it must return error messages in the form an integer as error message count and a table of string as error messages. For example:  
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
* `ui_func` and `validation_func_ui` will be introduced in the next section.   
* The `words` argument is a table of English words to be displayed in the config GUI.  
    * `name_b` is the name of your automation script in bold, for example `"𝗠𝘆𝗠𝗮𝗰𝗿𝗼"`.  
    * `config_b` is the English word config in bold. The default value is `"𝗖𝗼𝗻𝗳𝗶𝗴"`, but you may also want to put in words like `"𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀"`.  
    * `template` is the English word template. The default value is `Template`, but you can use `Preset` if that describes better.  
    * `templates_b` is the English word templates. This should match the word you used for `template`. The default value is `"𝗧𝗲𝗺𝗽𝗹𝗮𝘁𝗲𝘀"`, but you can use `𝗣𝗿𝗲𝘀𝗲𝘁𝘀`.  
    Note that bold in aka.config is achieved using Mathematical Sans-Serif Bold characters from U+1D5D4 to U+1D607. arch1t3cht has recently added support for real bold in Aegisub and Akatsumekusa may move to that solution one day.  
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
* `is_no_gui_init` is the argument we mentioned before. If the config file doesn't exist or is empty, the default preset specified in `config_templates` will be applied automatically without opening the GUI if `is_no_gui_init` is set to `true`.  

Among all the arguments, these are optional:  
```lua
function(config, subfolder, validation_func, ui_func, validation_func_ui, words, config_templates, is_no_gui_init)
-- Optional:     ^          ^                ^        ^                                            ^
```
As explained in previous sections, all optional arguments can be omitted in place when calling the function.  

`edit_config_gui` will save the applied config and then return `true` with config data as Lua table if everything works out. It will return `false` if the user close or cancel the config GUI.  

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
            error_msg_count = error_msg_count + 1 table.insert(error_msg, "\"" .. to_string(w) .. "\" at position " .. tostring(k) .. " not a number")
        if v % 1 ~= 0 then
            error_msg_count = error_msg_count + 1 table.insert(error_msg, "The number " .. to_string(w) .. " at position " .. tostring(k) .. " not an integer")
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
    local config_data_

    if not config_data then
        is_success, config_data_ = config.read_config("numbers", "aka.MyMacro", config_validate)
        if is_success then config_data = config_data_
        else
            is_success, config_data_ = config.edit_config_gui("numbers", "aka.MyMacro", config_validate, nil, nil, "𝗠𝘆𝗠𝗮𝗰𝗿𝗼", "𝗖𝗼𝗻𝗳𝗶𝗴", "Preset", "𝗣𝗿𝗲𝘀𝗲𝘁𝘀", config_templates, true)
            if is_success then config_data = config_data_
            else aegisub.cancel() end
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

### Using custom config UI
