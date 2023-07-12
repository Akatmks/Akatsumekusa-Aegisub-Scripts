--- A simple interface to mmap or MapViewOfFile
--  mmapfile uses `mmap` (on Unix) or `MapViewOfFileEx` (on Windows)  to
--  provide a way of quickly storing and loading data that's already in some
--  kind of in-memory binary format.
--
--  `create` creates a new file and maps new memory to that file.  You can
--  then write to the memory to write to the file.
--
--  `open` opens an existing file and maps its contents to memory, returning
--  a pointer to the memory and the length of the file.
--
--  `close` syncs memory to the file, closes the file, and deletes the
--  mapping between the memory and the file.
--
--  The "gc" variants of `create` and `open` (`gccreate` and `gcopen`) set
--  up a garbage collection callback for the pointer so that the file is
--  correctly closed when the pointer is no longer referenced.  Not
--  appropriate if you might be storing the pointer in C, referencing it from
--  unmanaged memory, or casting it to another type!
--
--  All memory is mapped above 4G to try to keep away from the memory space
--  LuaJIT uses.

-- (c) Copyright 2014-2016 Geoff Leyland.
-- See LICENSE for license information

local ffi = require"ffi"
local platform_mmapfile = (jit.os == "Windows" and require"aka.mmapfile.mmapfile.windows") or
                          require"aka.mmapfile.mmapfile.unix"


------------------------------------------------------------------------------

--- Same as malloc, but set up a GC cleanup for the memory.
--  @treturn pointer: the memory allocated
local function gcmalloc(
  size,         -- integer: number of bytes or `type`s to allocate.
  type,         -- ?string: type to allocate
  data)         -- ?pointer: data to copy to the mapped area.
  return ffi.gc(platform_mmapfile.malloc(size, type, data), platform_mmapfile.free)
end


------------------------------------------------------------------------------

--- Same as create, but set up a GC cleanup for the memory and file.
--  @treturn pointer: the memory allocated
local function gccreate(
  filename,     -- string: name of the file to create.
  size,         -- integer: number of bytes or `type`s to allocate.
  type,         -- ?string: type to allocate
  data)         -- ?pointer: data to copy to the mapped area.
  return ffi.gc(platform_mmapfile.create(filename, size, type, data), platform_mmapfile.close)
end


--- Same as open, but set up a GC cleanup for the memory and file.
--  @treturn pointer: the memory allocated.
--  @treturn int: size of the file, in bytes or `type`s.
local function gcopen(
  filename,     -- string: name of the file to open.
  type,         -- ?string: type to allocate
  mode,         -- ?string: open mode for the file "r" or "rw"
  size,         -- ?integer: size to map (in multiples of type).  Default
                -- is file size
  offset)       -- ?integer: offset into the file (default 0)
  local addr, actual_size = platform_mmapfile.open(filename, type, mode, size, offset)
  return ffi.gc(addr, platform_mmapfile.close), actual_size
end


------------------------------------------------------------------------------

return
{
  free          = platform_mmapfile.free,
  malloc        = platform_mmapfile.malloc,
  gcmalloc      = gcmalloc,
  create        = platform_mmapfile.create,
  gccreate      = gccreate,
  open          = platform_mmapfile.open,
  gcopen        = gcopen,
  close         = platform_mmapfile.close,
}

------------------------------------------------------------------------------

