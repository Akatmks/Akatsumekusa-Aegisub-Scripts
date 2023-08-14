-- aka.effil
-- Copyright (c) Akatsumekusa and contributors

-- Copyright (c) 2017 Mikhail Kupriyanov <mihakuper@gmail.com>, Ilia Udalov <UdalovIlia@gmail.com>
-- 
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
-- 
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
-- 
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

local versioning = {}

versioning.name = "effil"
versioning.description = "Module effil"
versioning.version = "1.0.8"
versioning.author = "Mikhail Kupriyanov, Ilia Udalov"
versioning.namespace = "aka.effil"

versioning.requiredModules = "[{ \"moduleName\": \"ffi\" }, { \"moduleName\": \"requireffi.requireffi\", \"version\": \"0.1.2\" }]"

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl({
        name = versioning.name,
        description = versioning.description,
        version = versioning.version,
        author = versioning.author,
        moduleName = versioning.namespace,
        url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
        {
            { "ffi" },
            { "requireffi.requireffi", version = "0.1.2" }
        }
    }):requireModules()
end
local ffi = require("ffi")
local requireffi = require("requireffi.requireffi")

local effil
if ffi.os == "OSX" then
    effil = requireffi("aka.effil.effil-osx")
else
    effil = requireffi("aka.effil.effil")
end

return function() return effil end
