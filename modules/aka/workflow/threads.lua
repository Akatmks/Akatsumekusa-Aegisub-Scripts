-- aka.workflow
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

local aconfig = require("aka.config2")

local _threads
local threads
local setThreads

local is_success
local config_data

is_success, config_data = aconfig.read_config("aka.workflow.threads", function(config_data)
    return type(config_data[1]) == "number"
end)
if is_success then _threads = config_data[1] else setThreads(-1) end
if _threads == -1 then
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

        _threads = tonumber(lpSystemInfo[0].dwNumberOfProcessors)
    elseif jit.os == "OSX" then
        local f

        f = assert(io.popen("sysctl -n hw.ncpu", "r"))
        _threads = f:read("*number")
        assert(f:close())
    else
        local f

        f = assert(io.popen("nproc", "r"))
        _threads = f:read("*number")
        assert(f:close())
end end

threads = function()
    return _threads
end

setThreads = function(threads)
    assert(type(threads) == "number")
    _threads = threads
    return aconfig.write_config("aka.workflow.threads", { threads })
end

local functions = {}

functions._threads = _threads
functions.threads = threads
functions.setThreads = setThreads

return functions
