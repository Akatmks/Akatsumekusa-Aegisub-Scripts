--[[
LuaJIT-Request
Lucien Greathouse, slightly altered by Akatsumekusa
Wrapper for LuaJIT-cURL for easy HTTP(S) requests.

Copyright (c) 2016 Lucien Greathouse

This software is provided 'as-is', without any express
or implied warranty. In no event will the authors be held
liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, andto alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
claim that you wrote the original software. If you use this software
in a product, an acknowledgment in the product documentation would be
appreciated but is not required.

2. Altered source versions must be plainly marked as such, and must
not be misrepresented as being the original software.

3. This notice may not be removed or altered from any source distribution.
]]

local versioning = {}

versioning.name = "aka.request"
versioning.description = "Module aka.request"
versioning.version = "1.0.5"
versioning.author = "Lucien Greathouse, slightly altered by Akatsumekusa"
versioning.namespace = "aka.request"

versioning.requireModules = "[{ \"moduleName\": \"ffi\" }, { \"moduleName\": \"requireffi.requireffi\", \"version\": \"0.1.2\" }]"

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl({
        name = versioning.name,
        description = versioning.description,
        version = versioning.version,
        author = versioning.author,
        moduleName = versioning.namespace,
        url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/dev/DependencyControl.json",
        {
            { "ffi" },
            { "requireffi.requireffi", version = "0.1.2" }
        }
    }):requireModules()
end

local request = require("aka.request.luajit-request")

request.versioning = versioning

return request
