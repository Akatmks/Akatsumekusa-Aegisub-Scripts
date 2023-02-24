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

local effil = require("aka.effil")

local Backend = {}
Backend.__index = Backend

setmetatable(Backend, { __call = function(cls, ...) return cls.new(...) end })
Backend.new = function(subs)
    local self = setmetatable({}, Backend)
    self.subs = subs

    self.remains_list = {}
    self.remains_channel = effil.channel()
    self.remains_thread = (effil.thread(function()
        local operation, data
        local poppable

        repeat
            operation, data = self.remains_channel:pop()

            if operation == "New" then
                if #self.remains_list == 0 then
                    table.insert(self.remains_list, data)
                else
                    for i=1,#self.remains_list do
                        if type(self.remains_list[i]) == "number" and self.remains_list[i] > data or
                           type(self.remains_list[i]) == "table" and self.remains_list[i].start_pos > data then
                            table.insert(self.remains_list, i, data)
                            break
                end end end

            elseif operation == "Complete" then
                poppable = true

                for i=#self.remains_list,1,-1 do
                    if data.start_pos ~= self.remains_list[i] then
                        if type(self.remains_list[i]) == "number" then
                            poppable = false
                        end
                    else -- data.start_pos == self.remains_list[i] then
                        self.remains_list[i] = data
    
                        if poppable then
                            for j=#self.remains_list,i,-1 do
                                self:join_frontend(table.remove(self.remains_list))
                                break
            end end end end end

        until #self.remains_list == 0 and
              self.remains_channel:size() == 0 end))()
    
    return self
end

Backend.spawn_subs = function(self, sel)
    self.remains_list:push("New", sel[1])

    local Frontend = {}

    Frontend.data = {}
    Frontend.data.start_pos = sel[1]
    Frontend.data.end_pos = sel[#sel]
    for i=1,#sel do
        Frontend.data[i] = self.subs[sel[i]]
    end

    Frontend.n = "[aka.workflow] Retrieving the number of lines in the subtitle object is not supported when multithreading"

    Frontend.read = function(index)
        if Frontend.data[index - Frontend.data.start_pos + 1] == nil then
            error("[aka.workflow] Retrieving subtitle lines outside provided line group is not supported when multithreading")
        end

        return Frontend.data[index - Frontend.data.start_pos + 1]
    end
    Frontend.append = function(_)
        error("[aka.workflow] Appending to subtitle object is not supported when multithreading")
    end
    Frontend.insert = function(index, line, ...)
        local lines
        lines = table.pack(...)
        table.insert(lines, 1, line)

        if index < Frontend.data.start_pos or index > Frontend.data.end_pos + 1 then
            error("[aka.workflow] Inserting subtitle lines outside provided line group is not supported when multithreading")
        end

        for j=#lines,1,-1 do
            table.insert(Frontend.data, index - Frontend.data.start_pos + 1, lines[j])
    end end
    Frontend.replace = function(index, line)
        if Frontend.data[index - Frontend.data.start_pos + 1] == nil then
            error("[aka.workflow] Retrieving subtitle lines outside provided line group is not supported when multithreading")
        end

        if line ~= nil then
            Frontend.data[index - Frontend.data.start_pos + 1] = line
        else
            table.remove(Frontend.data, index - Frontend.data.start_pos + 1)
    end end
    Frontend.delete = function(index, ...)
        local indexes
        if type(index) == "table" then
            indexes = index
        else
            indexes = table.pack(...)
            table.insert(indexes, 1, index)
        end
        table.sort(indexes)

        for i=#indexes,1,-1 do
            Frontend.replace(indexes[i])
    end end
    Frontend.deleterange = function(first, last)
        for i=last,first,-1 do
            Frontend.replace(i)
    end end

    Frontend.join = function()
        self.remains_list:push("Complete", Frontend.data)
    end

    local Metatable = {}

    Metatable.__index = function(cls, index)
        return Frontend.read(index)
    end
    Metatable.__newindex = function(cls, index, value)
        if index < 0 then
            Frontend.insert(-index, value)
        elseif index == 0 then
            Frontend.append(value)
        else -- index > 0 then
            Frontend.replace(index, value)
    end end
    Metatable.__len = function(cls)
        error(Frontend.n)
    end

    setmetatable(Frontend, Metatable)
    return Frontend
end
Backend.spawn_sub = Backend.spawn_subs

Backend.join_frontend = function(self, Frontend)
    for i=1,Frontend.data.end_pos-Frontend.data.start_pos+1 do
        self.subs[Frontend.data.start_pos + i - 1] = Frontend.data[i]
    end
    for i=Frontend.data.end_pos-Frontend.data.start_pos+2,#Frontend.data do
        self.subs[-(Frontend.data.start_pos + i)] = Frontend.data[i]
    end
end

Backend.join = function(self)
    local status, err, stacktrace

    status, err, stacktrace = self.remains_thread:wait()
    if status == "failed" then
        error(err .. "\n\n" .. stacktrace)
end end
