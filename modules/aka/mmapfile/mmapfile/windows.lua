--- A simple interface to MapViewOfFile.
--  mmapfile uses `MapViewOfFileEx` to provide a way of quickly storing and loading data
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
--  All memory is mapped above 4G to try to keep away from the memory space
--  LuaJIT uses.

-- (c) Copyright 2014-2016 Geoff Leyland.
-- See LICENSE for license information

local ffi = require"ffi"

------------------------------------------------------------------------------

ffi.cdef[[
typedef uint32_t DWORD;
typedef const char *LPCTSTR;
typedef void *HANDLE;
typedef int64_t LARGE_INTEGER;
typedef int BOOL;

DWORD GetLastError();
DWORD FormatMessageA(
    DWORD dwFlags,
    const void* lpSource,
    DWORD dwMessageId,
    DWORD dwLanguageId,
    char* lpBuffer,
    DWORD nSize,
    va_list *Arguments);
HANDLE CreateFileA(
    LPCTSTR lpFileName,
    DWORD dwDesiredAccess,
    DWORD dwShareMode,
    void* lpSecurityAttributes,
    DWORD dwCreationDisposition,
    DWORD dwFlagsAndAttributes,
    HANDLE hTemplateFile);
HANDLE CreateFileMappingA(
    HANDLE hFile,
    void* lpAttributes,
    DWORD flProtect,
    DWORD dwMaximumSizeHigh,
    DWORD dwMaximumSizeLow,
    LPCTSTR lpName);
void* MapViewOfFileEx(
    HANDLE hFileMappingObject,
    DWORD dwDesiredAccess,
    DWORD dwFileOffsetHigh,
    DWORD dwFileOffsetLow,
    size_t dwNumberOfBytesToMap,
    void *lpBaseAddress);
long UnmapViewOfFile(void* lpBaseAddress);
long CloseHandle(HANDLE hObject);
BOOL GetFileSizeEx(
    HANDLE hFile,
    LARGE_INTEGER* lpFileSize);

static const DWORD FORMAT_MESSAGE_FROM_SYSTEM        = 0x00001000;
static const DWORD FORMAT_MESSAGE_IGNORE_INSERTS     = 0x00000200;

static const DWORD GENERIC_READ                      = 0x80000000;
static const DWORD GENERIC_WRITE                     = 0x40000000;

static const DWORD OPEN_EXISTING                     = 0x00000003;
static const DWORD CREATE_ALWAYS                     = 0x00000002;

static const DWORD FILE_ATTRIBUTE_ARCHIVE            = 0x00000020;
static const DWORD FILE_FLAG_RANDOM_ACCESS           = 0x10000000;

static const DWORD FILE_MAP_ALL_ACCESS               = 0x000f001f;
static const DWORD FILE_MAP_READ                     = 0x00000004;

static const DWORD PAGE_READWRITE                    = 0x00000004;
static const DWORD PAGE_READONLY                     = 0x00000002;

static const DWORD FILE_SHARE_READ                   = 0x00000001;
]]

local INVALID_HANDLE_VALUE = ffi.cast("HANDLE", -1)  -- I can't work out how to define this in the cdefs.


------------------------------------------------------------------------------

local error_buffer = ffi.new("char[1024]")
local function last_error_string()
  local code = ffi.C.GetLastError()
  local length = ffi.C.FormatMessageA(
    bit.bor(ffi.C.FORMAT_MESSAGE_FROM_SYSTEM, ffi.C.FORMAT_MESSAGE_IGNORE_INSERTS),
    nil, code, 0, error_buffer, 1023, nil)
  return ffi.string(error_buffer, length)
end


local size_buffer = ffi.new("LARGE_INTEGER[1]")
local function get_file_size(file)
  local ok = ffi.C.GetFileSizeEx(file, size_buffer)
  if ok == 0 then
    error(("mmapfile.get_file_size: error getting file size: %s"):format(last_error_string()))
  end
  return tonumber(size_buffer[0])
end


------------------------------------------------------------------------------

--- Call mmap until we get an address higher that 4 gigabytes.
--  mmapping over 4G means we don't step on LuaJIT's toes, and this usually
--  works first time.
--  See `man mmap` for explanation of parameters.
--  @treturn pointer: the memory allocated.
local function mmap_4G(
  map,          -- file map to map to
  size,         -- integer: size to allocate in bytes
  access,       -- string: mmap's prot, as interpreted by syscall
  offset)       -- ?integer: offset into file to map
  offset = offset or 0
  local base = 4 * 1024 * 1024 * 1024
  local step = 0x10000
  local addr
  for _ = 1, 32 do
    addr = ffi.C.MapViewOfFileEx(map, access, 0, offset, size, ffi.cast("void*", base))

    if addr >= ffi.cast("void*", 4 * 1024 * 1024 * 1024) then break end
    if addr ~= nil then
      ffi.C.UnmapViewOfFile(addr)
    end
    base = base + step
    step = math.min(2^26, step * 2) -- 64MB should be a pretty good step, right?
  end
  return addr
end


------------------------------------------------------------------------------

local malloced_maps = {}

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

  local map = ffi.C.CreateFileMappingA(INVALID_HANDLE_VALUE, nil, ffi.C.PAGE_READWRITE, 0, size, nil)
  if map == nil then
    error(("mmapfile.malloc: Error: %s"):format(last_error_string()))
  end

  local addr = mmap_4G(map, size, ffi.C.FILE_MAP_ALL_ACCESS, 0)
  if addr == nil then
    error(("mmapfile.malloc: Error: %s"):format(last_error_string()))
  end

  malloced_maps[tostring(ffi.cast("void*", addr))] = map

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
  local map = assert(malloced_maps[s], "no mmapped block at this address")
  ffi.C.UnmapViewOfFile(addr)
  ffi.C.CloseHandle(map)
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

  ffi.C.UnmapViewOfFile(addr)
  ffi.C.CloseHandle(fd.map)
  ffi.C.CloseHandle(fd.fd)
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
  local fd = ffi.C.CreateFileA(filename,
    bit.bor(ffi.C.GENERIC_READ, ffi.C.GENERIC_WRITE), 0, nil, ffi.C.CREATE_ALWAYS,
    bit.bor(ffi.C.FILE_ATTRIBUTE_ARCHIVE, ffi.C.FILE_FLAG_RANDOM_ACCESS), nil)

  if fd == INVALID_HANDLE_VALUE then
    error(("mmapfile.create: Error creating '%s': %s"):format(filename, last_error_string()))
  end

  if type then
    size = size * ffi.sizeof(type)
  end

  local map = ffi.C.CreateFileMappingA(fd, nil, ffi.C.PAGE_READWRITE, 0, size, nil)
  if map == nil then
    error(("mmapfile.create: Error creating %s: %s"):format(filename, last_error_string()))
  end

  local addr = mmap_4G(map, size, ffi.C.FILE_MAP_ALL_ACCESS, 0)
  if addr == nil then
    error(("mmapfile.create: Error creating %s: %s"):format(filename, last_error_string()))
  end

  open_fds[tostring(ffi.cast("void*", addr))] = { fd = fd, map = map }

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
  local filemode, sharemode, mapmode, ptrmode
  if mode == "r" then
    filemode = ffi.C.GENERIC_READ
    sharemode = ffi.C.FILE_SHARE_READ
    mapmode = ffi.C.PAGE_READONLY
    ptrmode = ffi.C.FILE_MAP_READ
  elseif mode == "rw" then
    filemode = bit.bor(ffi.C.GENERIC_READ, ffi.C.GENERIC_WRITE)
    sharemode = 0
    mapmode = ffi.C.PAGE_READWRITE
    ptrmode = ffi.C.FILE_MAP_ALL_ACCESS
  else
    return nil, "unknown read/write mode"
  end

  local fd = ffi.C.CreateFileA(filename,
    filemode, sharemode, nil, ffi.C.OPEN_EXISTING,
    bit.bor(ffi.C.FILE_ATTRIBUTE_ARCHIVE, ffi.C.FILE_FLAG_RANDOM_ACCESS), nil)
  if fd == INVALID_HANDLE_VALUE then
    error(("mmapfile.open: Error opening %s: %s"):format(filename, last_error_string()))
  end

  if not size then
    size = get_file_size(fd)
  elseif type then
    size = size * ffi.sizeof(type)
  end

  local map = ffi.C.CreateFileMappingA(fd, nil, mapmode, 0, size, nil)
  if map == nil then
    error(("mmapfile.open: Error opening %s: %s"):format(filename, last_error_string()))
  end

  local addr = mmap_4G(map, 0, ptrmode, offset)
  if addr == nil then
    error(("mmapfile.open: Error opening %s: %s"):format(filename, last_error_string()))
  end

  open_fds[tostring(ffi.cast("void*", addr))] = { fd = fd, map = map }

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

