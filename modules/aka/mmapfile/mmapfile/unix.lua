--- A simple interface to mmap.
--  mmapfile uses `mmap` to provide a way of quickly storing and loading data
--  that's already in some kind of in-memory binary format.
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

local S = require"aka.ljsyscall"
local ffi = require"ffi"


------------------------------------------------------------------------------

local function assert(condition, message)
  if condition then return condition end
  message = message or "assertion failed"
  error(tostring(message), 2)
end


------------------------------------------------------------------------------

--- Call mmap until we get an address higher that 4 gigabytes.
--  mmapping over 4G means we don't step on LuaJIT's toes, and this usually
--  works first time.
--  See `man mmap` for explanation of parameters.
--  @treturn pointer: the memory allocated.
local function mmap_4G(
  size,         -- integer: size to allocate in bytes
  prot,         -- string: mmap's prot, as interpreted by syscall
  flags,        -- string: mmap's flags, as interpreted by syscall
  fd,           -- integer: file descriptor to map to
  offset)       -- ?integer: offset into file to map
  offset = offset or 0
  local base = 4 * 1024 * 1024 * 1024
  local step = 2^math.floor(math.log(tonumber(size)) / math.log(2))
  local addr
  for _ = 1, 1024 do
    addr = S.mmap(ffi.cast("void*", base), size, prot, flags, fd, offset)
    if addr >= ffi.cast("void*", 4 * 1024 * 1024 * 1024) then break end
    S.munmap(addr, size)
    base = base + step
  end
  return addr
end


------------------------------------------------------------------------------

local malloced_sizes = {}


--- "Map" some anonymous memory that's not mapped to a file.
--  This makes mmap behave a bit like malloc, except that we can persuade it
--  to give us memory above 4G, and malloc will be a very, very slow allocator
--  so only use it infrequently on big blocks of memory.
--  This is really just a hack to get us memory above 4G.  There's probably a
--  better solution.
--  @treturn pointer: the memory allocated.
local function malloc(
  size,         -- integer: number of bytes or `type`s to allocate.
  type,         -- ?string: type to allocate
  data)         -- ?pointer: data to copy to the mapped area.

  if type then
    size = size * ffi.sizeof(type)
  end

  local addr = assert(mmap_4G(size, "read, write", "anon, shared"))

  malloced_sizes[tostring(ffi.cast("void*", addr))] = size

  if data then
    ffi.copy(addr, data, size)
  end

  if type then
    return ffi.cast(type.."*", addr)
  else
    return addr
  end
end


--- Free memory mapped with mmapfile.malloc
--  Just munmaps the memory.
local function free(
  addr)         -- pointer: the mapped address to unmap.
  local s = tostring(ffi.cast("void*", addr))
  local size = assert(malloced_sizes[s], "no mmapped block at this address")
  assert(S.munmap(addr, size))
end

------------------------------------------------------------------------------

local open_fds = {}


--- Close a mapping between a file and an address.
--  `msync` the memory to its associated file, `munmap` the memory, and close
--  the file.
local function close(
  addr)         -- pointer: the mapped address to unmap.
  local s = tostring(ffi.cast("void*", addr))
  local fd = assert(open_fds[s], "no file open for this address")
  open_fds[s] = nil

  -- it seems that file descriptors get closed before final __gc calls in
  -- some exit scenarios, so we don't worry too much if we can't
  -- stat the fd
  local st = fd:stat()
  if st then
    assert(S.msync(addr, st.size, "sync"))
    assert(S.munmap(addr, st.size))
    assert(fd:close())
  end
end


--- Allocate memory and create a new file mapped to it.
--  Use create to set aside an area of memory to write to a file.
--  If `type` is supplied then the pointer to the allocated memory is cast
--  to the correct type, and `size` is the number of `type`, not bytes,
--  to allocate.
--  If `data` is supplied, then the data at `data` is copied into the mapped
--  memory (and so written to the file).  It might make more sense just to
--  map the pointer `data` directly to the file, but that might require `data`
--  to be on a page boundary.
--  The file descriptor is saved in a table keyed to the address allocated
--  so that close can find the write fd to close when the memory is unmapped.
--  @treturn pointer: the memory allocated.
local function create(
  filename,     -- string: name of the file to create.
  size,         -- integer: number of bytes or `type`s to allocate.
  type,         -- ?string: type to allocate
  data)         -- ?pointer: data to copy to the mapped area.
  local fd, message = S.open(filename, "RDWR, CREAT", "RUSR, WUSR, RGRP, ROTH")

  if not fd then
    error(("mmapfile.create: Error creating '%s': %s"):format(filename, message))
  end

  if type then
    size = size * ffi.sizeof(type)
  end

  -- lseek gets stroppy if we try to seek the -1th byte, so let's just say
  -- all files are at least one byte, even if theres's no actual data.
  size = math.max(size, 1)
  assert(fd:lseek(size-1, "set"))
  assert(fd:write(ffi.new("char[1]", 0), 1))

  local addr = assert(mmap_4G(size, "read, write", "file, shared", fd))

  open_fds[tostring(ffi.cast("void*", addr))] = fd

  if data then
    ffi.copy(addr, data, size)
  end

  if type then
    return ffi.cast(type.."*", addr)
  else
    return addr
  end
end


--- Map an existing file to an area of memory.
--  If `type` is present, the the pointer returned is cast to the `type*` and
--  the size returned is the number of `types`, not bytes.
--  @treturn pointer: the memory allocated.
--  @treturn int: size of the file, in bytes or `type`s.
local function open(
  filename,     -- string: name of the file to open.
  type,         -- ?string: type to allocate (default void*)
  mode,         -- ?string: open mode for the file "r" or "rw" (default "r")
  size,         -- ?integer: size to map (in multiples of type).  Default
                -- is file size
  offset)       -- ?integer: offset into the file (default 0)
  offset = offset or 0

  mode = mode or "r"
  local filemode, mapmode
  if mode == "r" then
    filemode = "rdonly"
    mapmode = "read"
  elseif mode == "rw" then
    filemode = "rdwr"
    mapmode = "read, write"
  else
    return nil, "unknown read/write mode"
  end

  local fd, message = S.open(filename, filemode, 0)
  if not fd then
    error(("mmapfile.open: Error opening %s: %s"):format(filename, message))
  end

  if not size then
    local st = assert(fd:stat())
    size = st.size
  elseif type then
    size = size * ffi.sizeof(type)
  end

  local addr = assert(mmap_4G(size, mapmode, "file, shared", fd, offset))

  open_fds[tostring(ffi.cast("void*", addr))] = fd

  if type then
    return ffi.cast(type.."*", addr), math.floor(size / ffi.sizeof(type))
  else
    return addr, size
  end
end


------------------------------------------------------------------------------

return
{
  free          = free,
  malloc        = malloc,
  create        = create,
  open          = open,
  close         = close,
}

------------------------------------------------------------------------------

