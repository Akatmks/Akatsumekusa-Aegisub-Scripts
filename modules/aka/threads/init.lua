-- aka.threads
-- Copyright (c) Akatsumekusa and contributors

------------------------------------------------------------------------------
-- Permission is hereby granted, free of charge, to any person obtaining a
-- copy of this software and associated documentation files (the "Software"),
-- to deal in the Software without restriction, including without limitation
-- the rights to use, copy, modify, merge, publish, distribute, sublicense,
-- and/or sell copies of the Software, and to permit persons to whom the
-- Software is furnished to do so, subject to the following conditions:

-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.

-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
-- FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
-- DEALINGS IN THE SOFTWARE.
------------------------------------------------------------------------------

local versioning = {}

versioning.name = "aka.threads"
versioning.description = "Module aka.threads"
versioning.version = "1.0.4"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.threads"

versioning.requiredModules = "[{ \"moduleName\": \"aka.singlesimple\" }, { \"moduleName\": \"ffi\" }]"

local version = require("l0.DependencyControl")({
    name = versioning.name,
    description = versioning.description,
    version = versioning.version,
    author = versioning.author,
    moduleName = versioning.namespace,
    url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
    feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
    {
        { "aka.singlesimple" },
        { "ffi" }
    }
})
version:requireModules()


local threadsEnum = {}
for i=0,512 do
    table.insert(threadsEnum, i)
end
local ss = require("aka.singlesimple").make_config("aka.threads", threadsEnum, 0)


local getSystemThreads = function()
    local threads

    if jit.os == "Windows" then
        local ffi           = require("ffi")
        ffi.cdef[[
typedef struct {
    uint16_t  wProcessorArchitecture;
    uint16_t  wReserved;
    uint32_t  dwPageSize;
    void*     lpMinimumApplicationAddress;
    void*     lpMaximumApplicationAddress;
    uint32_t* dwActiveProcessorMask;
    uint32_t  dwNumberOfProcessors;
    uint32_t  dwProcessorType;
    uint32_t  dwAllocationGranularity;
    uint16_t  wProcessorLevel;
    uint16_t  wProcessorRevision;
} SYSTEM_INFO, *LPSYSTEM_INFO;
void GetSystemInfo(LPSYSTEM_INFO lpSystemInfo);
        ]]
        local kernel32      = ffi.load("kernel32.dll")
        local lpSystemInfo  = ffi.new("SYSTEM_INFO[1]")

        kernel32.GetSystemInfo(lpSystemInfo)

        threads = tonumber(lpSystemInfo[0].dwNumberOfProcessors)
    elseif jit.os == "OSX" then
        local f
        local threads

        f = assert(io.popen("sysctl -n hw.ncpu", "r"))
        threads = f:read("*number")
        assert(f:close())
    else
        local f
        local threads

        f = assert(io.popen("nproc", "r"))
        threads = f:read("*number")
        assert(f:close())
    end
    
    if threads > 512 then
        threads = 512
    end
    return threads
end
local system_threads


local threads = {}
threads.__index = threads

threads.threads = function()
    local threads

    threads = ss:value()
    if threads == 0 then
        if not system_threads then system_threads = getSystemThreads() end
        threads = system_threads
    end
    return threads
end

-- Set the number of threads to use for all scripts
-- Setting this to any integer or set it to 0 for the number of logical processors on the system
threads.setThreads = function(threads)
    if threads > 512 then threads = 512 end
    ss:setValue(threads)
end

threads.version = version
threads.versioning = versioning

return version:register(threads)
