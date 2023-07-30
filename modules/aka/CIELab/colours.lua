-- aka.CIELab
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

local ffi = require("ffi")

ffi.cdef[[
typedef double Colour[3];
]]

local BT709RGBtoXYZ = function(RGB)
    for i=0,2 do
        RGB[i]                          = RGB[i] / 255
        if RGB[i] < 0.081 then  RGB[i]  = RGB[i] / 4.5
        else                    RGB[i]  = ((RGB[i] + 0.099) / 1.099) ^ 2.2
    end end

    local XYZ = ffi.new("Colour")
    XYZ[0]      = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
    XYZ[1]      = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
    XYZ[2]      = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505

    return XYZ
end
local XYZtoCIELab = function(XYZ)
    local buf = ffi.new("Colour")
    buf[0]      = XYZ[0] / 0.950489
    buf[1]      = XYZ[1] / 1.000000
    buf[2]      = XYZ[2] / 1.088840
    for i=0,2 do
        if buf[i] > (6/29) ^ 3 then buf[i]  = buf[i] ^ (1/3)
        else                        buf[i]  = buf[i] / 3 * (6/29) ^ 2 + 4/29
    end end

    local CIELab = ffi.new("Colour")
    CIELab[0]   = 116 * buf[1] - 16
    CIELab[1]   = 500 * (buf[0] - buf[1])
    CIELab[2]   = 200 * (buf[1] - buf[2])

    return CIELab
end

local CIELabtoCIELCh = function(CIELab)
    local CIELCh = ffi.new("Colour")
    CIELCh[0]   = CIELab[0]
    CIELCh[1]   = math.sqrt(CIELab[1] ^ 2 + CIELab[2] ^ 2)
    CIELCh[2]   = math.atan2(CIELab[2], CIELab[1]) / math.pi * 180

    return CIELCh
end
local CIELChtoCIELab = function(CIELCh)
    local CIELab = ffi.new("Colour")
    CIELab[0]   = CIELCh[0]
    CIELab[1]   = CIELCh[1] * math.cos(CIELCh[2] / 180 * math.pi)
    CIELab[2]   = CIELCh[1] * math.sin(CIELCh[2] / 180 * math.pi)

    return CIELab
end

local functions = {}

functions.BT709RGBtoXYZ = BT709RGBtoXYZ
functions.XYZtoCIELab = XYZtoCIELab
functions.CIELabtoCIELCh = CIELabtoCIELCh
functions.CIELChtoCIELab = CIELChtoCIELab

return functions
