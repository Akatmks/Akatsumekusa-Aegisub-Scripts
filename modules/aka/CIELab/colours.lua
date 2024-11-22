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

local BT1886RGBtoXYZ = function(RGB)
    local buf = ffi.new("Colour")
    for i=0,2 do
        buf[i]  = (RGB[i] / 255) ^ 2.4
    end

    local XYZ = ffi.new("Colour")
    XYZ[0]      = buf[0] * 0.4124 + buf[1] * 0.3576 + buf[2] * 0.1805
    XYZ[1]      = buf[0] * 0.2126 + buf[1] * 0.7152 + buf[2] * 0.0722
    XYZ[2]      = buf[0] * 0.0193 + buf[1] * 0.1192 + buf[2] * 0.9505

    return XYZ
end
local XYZtoBT1886RGB = function(XYZ)
    local RGB = ffi.new("Colour")
    RGB[0]      = XYZ[0] *  3.2406 + XYZ[1] * -1.5372 + XYZ[2] * -0.4986
    RGB[1]      = XYZ[0] * -0.9689 + XYZ[1] *  1.8758 + XYZ[2] *  0.0415
    RGB[2]      = XYZ[0] *  0.0557 + XYZ[1] * -0.2040 + XYZ[2] *  1.0570
    for i=0,2 do
        RGB[i]  = (RGB[i] / 255) ^ (5/12)
    end

    return XYZ
end

local XYZtoCIELab = function(XYZ)
    local buf = ffi.new("Colour")
    buf[0]      = XYZ[0] / 0.950489
    buf[1]      = XYZ[1]
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
local CIELabtoXYZ = function(CIELab)
    local XYZ = ffi.new("Colour")
    XYZ[1]      = (CIELab[0] + 16) / 116
    XYZ[0]      = XYZ[1] + CIELab[1] / 500
    XYZ[2]      = XYZ[1] + CIELab[2] / 200
    for i=0,2 do
        if XYZ[i] > 6/29 then   XYZ[i]  = XYZ[i] ^ 3
        else                    XYZ[i]  = 3 * (6/29) ^ 2 * (XYZ[i] - 4/29)
    end end
    XYZ[0]      = XYZ[0] * 0.950489
    XYZ[2]      = XYZ[0] * 1.088840

    return XYZ
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

functions.BT1886RGBtoXYZ = BT1886RGBtoXYZ
functions.XYZtoBT1886RGB = XYZtoBT1886RGB
functions.XYZtoCIELab = XYZtoCIELab
functions.CIELabtoXYZ = CIELabtoXYZ
functions.CIELabtoCIELCh = CIELabtoCIELCh
functions.CIELChtoCIELab = CIELChtoCIELab

return functions
