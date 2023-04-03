-- aka.unwhite_dialogue
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

local ILL = require("ILL.ILL")
local Table, Util = ILL.Table, ILL.Util
local acolours = require("aka.CIELab")

local prepare
local prepare__point
local prepare__exec
local prepare__average
local do_nothing
local iter_scenecut
local iter_scenecut__eval
local set_colour
local set_colour__eval

prepare = function(line, config, parsed_config)
    local subtitle_samples
    local background_samples
    local subtitle_scenecut
    local background_scenecut
    local subtitle_colours
    local background_colours

    subtitle_samples = {}
    background_samples = {}
    subtitle_scenecut = {}
    background_scenecut = {}
    subtitle_colours = {}
    background_colours = {}
    for frame=aegisub.frame_from_ms(line.start_time),aegisub.frame_from_ms(line.end_time) do
        frame = aegisub.get_frame(frame)

        subtitle_samples[frame] = {}
        subtitle_scenecut[frame] = {}
        subtitle_colours[frame] = {}
        prepare__point(frame,   line.left + 5,          line.top + 5,           subtitle_samples[frame])
        prepare__point(frame,   line.center,            line.top + 5,           subtitle_samples[frame])
        prepare__point(frame,   line.right - 5,         line.top + 5,           subtitle_samples[frame])
        prepare__point(frame,   line.left + 5,          line.bottom - 5,        subtitle_samples[frame])
        prepare__point(frame,   line.center,            line.bottom - 5,        subtitle_samples[frame])
        prepare__point(frame,   line.right - 5,         line.bottom - 5,        subtitle_samples[frame])
        if config.scenecut then
            prepare__exec(subtitle_samples[frame], subtitle_scenecut[frame], parsed_config[config.scenecut.exec])
            subtitle_scenecut[frame] = prepare__average(subtitle_scenecut[frame])
        end
        prepare__exec(subtitle_samples[frame], subtitle_colours[frame], parsed_config[config.colours.exec])
        subtitle_colours[frame] = prepare__average(subtitle_colours[frame])

        background_samples[frame] = {}
        background_scenecut[frame] = {}
        background_colours[frame] = {}
        prepare__point(frame,   50,                     50,                     background_samples[frame])
        prepare__point(frame,   frame:width() - 50,     50,                     background_samples[frame])
        prepare__point(frame,   50,                     frame:height() - 50,    background_samples[frame])
        prepare__point(frame,   frame:width() - 50,     frame:height() - 50,    background_samples[frame])
        prepare__point(frame,   120,                    120,                    background_samples[frame])
        prepare__point(frame,   frame:width() - 120,    120,                    background_samples[frame])
        prepare__point(frame,   120,                    frame:height() - 120,   background_samples[frame])
        prepare__point(frame,   frame:width() - 120,    frame:height() - 120,   background_samples[frame])
        if config.scenecut then
            prepare__exec(background_samples[frame], background_scenecut[frame], parsed_config[config.scenecut.exec])
            background_scenecut[frame] = prepare__average(background_scenecut[frame])
        end
        prepare__exec(background_samples[frame], background_colours[frame], parsed_config[config.colours.exec])
        background_colours[frame] = prepare__average(background_colours[frame])
    end

    return subtitle_scenecut, background_scenecut, subtitle_colours, background_colours
end

prepare__point = function(frame, x, y, samples_table)
    local swap_table
    local sort_table

    swap_table = {}
    for i=x-1,x+1 do
        for j=y-1,y+1 do
        table.insert(swap_table, table.pack(acolours.fromPixel(frame:getPixel(i, j)):toCIELCh()))
    end end

    sort_table = {}
    for i=1,9 do
        for j=1,i do
            if not sort_table[j] then
                table.insert(sort_table, swap_table[i])
                break
            elseif sort_table[j][1] > swap_table[i][1] then
                table.insert(sort_table, j, swap_table[i])
                break
            elseif sort_table[j][1] == swap_table[i][1] then
                if j < i / 2 then
                    table.insert(sort_table, j + 1, swap_table[i])
                    break
                else
                    table.insert(sort_table, j, swap_table[i])
                    break
    end end end end

    for i=3,7 do
        table.insert(samples_table, sort_table[i])
end end

prepare__exec = function(wd_samples_table, wd_target_table, wd_exec)
    local Y
    local C
    local h

    for wd_i=1,#wd_samples_table do
        Y, C, h = table.unpack(wd_samples_table[wd_i])
        table.insert(wd_target_table, wd_exec())
end end

prepare__average = function(processed_table)
    local sum

    for i=1,#processed_table do
        sum = sum + processed_table[i]
    end
    return sum / #processed_table
end


do_nothing = function(value)
    return value
end


iter_scenecut = function(line, subtitle_scenecut, background_scenecut, subtitle_colours, background_colours, config, parsed_config)
    local i

    i = 0
    return function()
        local return_line
        local return_subtitle_colours
        local return_background_colours

        while i < #subtitle_scenecut - 1 do
            i = i + 1

            if i == #subtitle_scenecut - 1 then
                return line, subtitle_colours, background_colours
            else
                if config.scenecut and 
                   iter_scenecut__eval(math.abs(background_scenecut[i] * 0.7 + subtitle_scenecut[i] * 0.3 -
                                                background_scenecut[i + 1] * 0.7 - subtitle_scenecut[i + 1] * 0.3), parsed_config[config.scenecut.eval]) then
                    return_line = Table.deepcopy(line)
                    return_line.end_time = aegisub.ms_from_frame(aegisub.frame_from_ms(line.start_time) + i - 1)
                    line.start_time = aegisub.ms_from_frame(aegisub.frame_from_ms(line.start_time) + i)
                    for j=1,i do
                        table.remove(subtitle_scenecut, 1)
                        table.insert(return_subtitle_colours, table.remove(subtitle_colours, 1))
                        table.remove(background_scenecut, 1)
                        table.insert(return_background_colours, table.remove(background_colours, 1))
                    end
                    return return_line, return_subtitle_colours, return_background_colours
end end end end end

iter_scenecut__eval = function(diff, wd_eval)
    return wd_eval()
end


set_colour = function(line, subtitle_colours, background_colours, config, parsed_config)
    local subtitle_param
    local background_param
    local param

    if type(subtitle_colours[1] == "number") then
        subtitle_param = 0
        background_param = 0
        for i=1,#subtitle_colours do
            subtitle_param = subtitle_param + subtitle_colours[i]
            background_param = background_param + background_colours[i]
        end
        subtitle_param = subtitle_param / #subtitle_colours
        background_param = background_param / #subtitle_colours
        param = subtitle_param * 0.8 + background_param * 0.2
    elseif type(subtitle_colours[1] == "table") then
        subtitle_param = {}
        background_param = {}
        param = {}
        for k,v in pairs(subtitle_colours[1]) do
            for i=1,#subtitle_colours do
                subtitle_param[k] = subtitle_param[k] + subtitle_colours[i][k]
                background_param[k] = background_param[k] + background_colours[i][k]
            end
            subtitle_param[k] = subtitle_param[k] / #subtitle_colours
            background_param[k] = background_param[k] / #subtitle_colours
            param[k] = subtitle_param[k] * 0.8 + background_param[k] * 0.2
        end
    else
        error("[aka.unwhite_dialogue] param for colours is neither a number or a table")
    end

    for i,v in ipairs(config.colours) do
        if set_colour__eval(param, parsed_config[v.eval]) then
            line.style = v.style
            return
    end end
    error("[aka.unwhite_dialogue] Line matches no colours in config")
end

set_colour__eval = function(param, wd_eval)
    return wd_eval()
end
