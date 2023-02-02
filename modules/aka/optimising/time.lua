-- aka.optimising
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

local ffi       = require("ffi")
ffi.cdef[[
    bool QueryPerformanceCounter(int64_t* lpPerformanceCount);
    bool QueryPerformanceFrequency(int64_t* lpFrequency);
]]
local kernel32  = ffi.load("kernel32.dll")
local QPC       = ffi.new("int64_t[1]")
local QPF       = ffi.new("int64_t[1]")
      QPF[0]    = 0

local time

time = function()
    kernel32.QueryPerformanceCounter(QPC)
    if QPF[0] == 0 then kernel32.QueryPerformanceFrequency(QPF) end

    return tonumber(QPC[0]) / tonumber(QPF[0])
end

local functions = {}

functions.time = time

return functions
