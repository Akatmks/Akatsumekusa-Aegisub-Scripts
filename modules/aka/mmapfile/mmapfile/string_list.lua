-- (c) Copyright 2014-2016 Geoff Leyland.
-- See LICENSE for license information

local ffi = require"ffi"
local mmapfile = require"aka.mmapfile.mmapfile"


------------------------------------------------------------------------------

local string_list = {}
string_list.__index = string_list


function string_list:new()
  return setmetatable({ count = 0, size = 0, strings = {}, map = {} }, self)
end


function string_list:add(s)
  if not self.map[s] then
    self.count = self.count + 1
    self.strings[self.count] = s
    self.map[s] = self.size
    self.size = self.size + #s + 1
  end
end


function string_list:write(filename)
  table.sort(self.strings)

  local string_ptr = mmapfile.gccreate(filename, self.size, "char")

  local offset = 0
  for _, s in ipairs(self.strings) do
    self.map[s] = offset
    ffi.copy(string_ptr + offset, s)
    offset = offset + #s + 1
  end

  return string_ptr
end


function string_list:offset(s)
  return self.map[s]
end


------------------------------------------------------------------------------

local string_file = {}
string_file.__index = string_file

function string_list.read(filename)
  local o = { string_ptr = mmapfile.gcopen(filename, "char") }
  return setmetatable(o, string_file)
end


function string_file:get(index)
  return ffi.string(self.string_ptr + index)
end


------------------------------------------------------------------------------

return string_list

------------------------------------------------------------------------------
