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
local util = require("aegisub.util")
local colours = require("aka.CIELab.colours")

local Colour = {}
Colour.__index = Colour

-- Thanks to Chortos-2 and arch1t3cht for clearing the details regarding
-- pure 2.4 and BT.709. I assume I did everything alright?
local ColourType = { BT1886RGB = "0", XYZ = "10", CIELab = "11", CIELCh = "12" }

Colour.fromBT1886RGB = function(R, G, B)
    local self = setmetatable({}, Colour)
    self.type = ColourType.BT1886RGB
    self.colour = ffi.new("Colour")
    self.colour[0] = R
    self.colour[1] = G
    self.colour[2] = B
    return self
end
Colour.fromPixel = function(colour)
    return Colour.fromBT1886RGB(util.extract_color(colour))
end
Colour.fromXYZ = function(X, Y, Z)
    local self = setmetatable({}, Colour)
    self.type = ColourType.XYZ
    self.colour = ffi.new("Colour")
    self.colour[0] = X
    self.colour[1] = Y
    self.colour[2] = Z
    return self
end
Colour.fromCIELab = function(L, a, b)
    local self = setmetatable({}, Colour)
    self.type = ColourType.CIELab
    self.colour = ffi.new("Colour")
    self.colour[0] = L
    self.colour[1] = a
    self.colour[2] = b
    return self
end
Colour.fromCIELCh = function(L, C, h)
    local self = setmetatable({}, Colour)
    self.type = ColourType.CIELCh
    self.colour = ffi.new("Colour")
    self.colour[0] = L
    self.colour[1] = C
    self.colour[2] = h
    return self
end

Colour.toBT1886RGB = function(self)
    local colour

    if self.type == ColourType.BT1886RGB then
        return self.colour[0], self.colour[1], self.colour[2]
    elseif self.type == ColourType.XYZ then
        colour = colours.XYZtoBT1886RGB(self.colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.CIELab then
        colour = colours.CIELabtoXYZ(self.colour)
        colour = colours.XYZtoBT1886RGB(colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.CIELCh then
        colour = colours.CIELChtoCIELab(self.colour)
        colour = colours.CIELabtoXYZ(colour)
        colour = colours.XYZtoBT1886RGB(colour)
        return colour[0], colour[1], colour[2]
end end
Colour.toXYZ = function(self)
    local colour

    if self.type == ColourType.BT1886RGB then
        colour = colours.BT1886RGBtoXYZ(self.colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.XYZ then
        return self.colour[0], self.colour[1], self.colour[2]
    elseif self.type == ColourType.CIELab then
        colour = colours.CIELabtoXYZ(self.colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.CIELCh then
        colour = colours.CIELChtoCIELab(self.colour)
        colour = colours.CIELabtoXYZ(colour)
        return colour[0], colour[1], colour[2]
end end
Colour.toCIELab = function(self)
    local colour

    if self.type == ColourType.BT1886RGB then
        colour = colours.BT1886RGBtoXYZ(self.colour)
        colour = colours.XYZtoCIELab(colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.XYZ then
        colour = colours.XYZtoCIELab(self.colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.CIELab then
        return self.colour[0], self.colour[1], self.colour[2]
    elseif self.type == ColourType.CIELCh then
        colour = colours.CIELChtoCIELab(self.colour)
        return colour[0], colour[1], colour[2]
end end
Colour.toCIELCh = function(self)
    local colour

    if self.type == ColourType.BT1886RGB then
        colour = colours.BT1886RGBtoXYZ(self.colour)
        colour = colours.XYZtoCIELab(colour)
        colour = colours.CIELabtoCIELCh(colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.XYZ then
        colour = colours.XYZtoCIELab(self.colour)
        colour = colours.CIELabtoCIELCh(colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.CIELab then
        colour = colours.CIELabtoCIELCh(self.colour)
        return colour[0], colour[1], colour[2]
    elseif self.type == ColourType.CIELch then
        return self.colour[0], self.colour[1], self.colour[2]
end end

local functions = {}

functions.Colour = Colour
functions.ColourType = ColourType

return functions
