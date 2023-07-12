-- this puts everything into one table ready to use

local require, print, error, assert, tonumber, tostring,
setmetatable, pairs, ipairs, unpack, rawget, rawset,
pcall, type, table, string, math = 
require, print, error, assert, tonumber, tostring,
setmetatable, pairs, ipairs, unpack, rawget, rawset,
pcall, type, table, string, math

local abi = require "aka.ljsyscall.syscall.abi"

if abi.rump and abi.types then abi.os = abi.types end -- pretend to be NetBSD for normal rump, Linux for rumplinux

if abi.os == "netbsd" then
  -- TODO merge
  require("aka.ljsyscall.syscall.netbsd.ffitypes")
  if not abi.rump then
    require("aka.ljsyscall.syscall.netbsd.ffifunctions")
  end
else
  require("aka.ljsyscall.syscall." .. abi.os .. ".ffi")
end

local c = require("aka.ljsyscall.syscall." .. abi.os .. ".constants")

local ostypes = require("aka.ljsyscall.syscall." .. abi.os .. ".types")
local bsdtypes
if (abi.rump and abi.types == "netbsd") or (not abi.rump and abi.bsd) then
  bsdtypes = require("aka.ljsyscall.syscall.bsd.types")
end
local types = require "aka.ljsyscall.syscall.types".init(c, ostypes, bsdtypes)

local C
if abi.rump then -- TODO merge these with conditionals
  C = require("aka.ljsyscall.syscall.rump.c")
else
  C = require("aka.ljsyscall.syscall." .. abi.os .. ".c")
end

-- cannot put in S, needed for tests, cannot be put in c earlier due to deps TODO remove see #94
c.IOCTL = require("aka.ljsyscall.syscall." .. abi.os .. ".ioctl").init(types)

local S = require "aka.ljsyscall.syscall.syscalls".init(C, c, types)

S.abi, S.types, S.t, S.c = abi, types, types.t, c -- add to main table returned

-- add compatibility code
S = require "aka.ljsyscall.syscall.compat".init(S)

-- add functions from libc
S = require "aka.ljsyscall.syscall.libc".init(S)

-- add methods
S = require "aka.ljsyscall.syscall.methods".init(S)

-- add utils
S.util = require "aka.ljsyscall.syscall.util".init(S)

if abi.os == "linux" then
  S.cgroup = require "aka.ljsyscall.syscall.linux.cgroup".init(S)
  S.nl = require "aka.ljsyscall.syscall.linux.nl".init(S)
  -- TODO add the other Linux specific modules here
end

S._VERSION = "v0.11pre"
S._DESCRIPTION = "ljsyscall: A Unix system call API for LuaJIT"
S._COPYRIGHT = "Copyright (C) 2011-2014 Justin Cormack. MIT licensed."

return S

