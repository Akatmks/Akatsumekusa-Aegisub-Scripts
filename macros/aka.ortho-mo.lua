-- aka.ortho-mo
-- Copyright (c) Akatsumekusa

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

local versioning = {}

versioning.name = "Aegisub-Orthographic-Motion"
versioning.description = "Apply frz fax motion"
versioning.version = "1.0.1"
versioning.author = "Akatsumekusa and contributors"
versioning.namespace = "aka.ortho-mo"

versioning.requireModules = "[{ \"moduleName\": \"aka.outcome\" }, { \"moduleName\": \"aegisub.clipboard\" }, { \"moduleName\": \"lpeg\" }]"

script_name = versioning.name
script_description = versioning.description
script_version = versioning.version
script_author = versioning.author
script_namespace = versioning.namespace

local hasDepCtrl, DepCtrl = pcall(require, "l0.DependencyControl")
if hasDepCtrl then
    DepCtrl({
        name = versioning.name,
        description = versioning.description,
        version = versioning.version,
        author = versioning.author,
        moduleName = versioning.namespace,
        url = "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
        feed = "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
        {
            { "aka.outcome" },
            { "aegisub.clipboard" },
            { "lpeg" }
        }
    }):requireModules()
end
local outcome = require("aka.outcome")
local ok, err, some, none, o = outcome.ok, outcome.err, outcome.some, outcome.none, outcome.o
local clipboard = require("aegisub.clipboard")
local lpeg = require("lpeg")
local P, S, R = lpeg.P, lpeg.S, lpeg.R

local get_clipboard
local parse_AAE
local ortho_mo
local apply_AAE
local apply_AAE_line
local apply_AAE_style_cache



get_clipboard = function()
    if jit.os == "Windows" or jit.os == "OSX" then
        return o(clipboard.get())
            :andThen(function(AAE)
                if type(AAE) == "string" then return ok(AAE)
                else return err() end end)
            :okOption()
    else
        return none()
end end



parse_AAE = function(AAE)
    local data
    local power_pin_frame_start
    local power_pin_frame_end
    local frz_fax_frame_start
    local frz_fax_frame_end
    local mode
    local data_head
    local frame
    local x
    local y

    -- [1]: frz array
    -- [2]: fax array
    -- [3]: Power Pin-0002 x array
    -- [4]: Power Pin-0002 y array
    -- [5]: Power Pin-0003 x array
    -- [6]: Power Pin-0003 y array
    -- [7]: Power Pin-0004 x array
    -- [8]: Power Pin-0004 y array
    -- [9]: Power Pin-0005 x array
    -- [10]: Power Pin-0005 y array
    data = {}
    for i=1,10 do data[i] = {} end
    power_pin_frame_start = nil
    power_pin_frame_end = nil
    frz_fax_frame_start = nil
    frz_fax_frame_end = nil

    -- "detecting": Not capturing headers yet
    -- "detected": Header captured, awaiting "Frame	X pixels	Y pixels"
    -- "logging": Logging data
    mode = "detecting"
    data_head = nil
    for line in AAE:gmatch("[^\n]+") do
        ::backagain::
        if mode == "detecting" then
            if line:find("Aegisub%-Orthographic%-Motion Data") then
                mode = "detected" data_head = 1
            elseif line:find("Power Pin%-0002") then
                mode = "detected" data_head = 3
            elseif line:find("Power Pin%-0003") then
                mode = "detected" data_head = 5
            elseif line:find("Power Pin%-0004") then
                mode = "detected" data_head = 7
            elseif line:find("Power Pin%-0005") then
                mode = "detected" data_head = 9
            end
        
        elseif mode == "detected" or mode == "logging" then
            if line:find("^\t") then -- line with indent
                frame, x, y = line:match("^\t(%d+)\t([%d.]+)\t([%d.]+)")
                frame = tonumber(frame) x = tonumber(x) y = tonumber(y)

                if frame and x and y then -- valid data
                    if data_head == 1 then -- frz fax
                        if not frz_fax_frame_start or frame < frz_fax_frame_start then frz_fax_frame_start = frame end
                        if not frz_fax_frame_end or frame > frz_fax_frame_end then frz_fax_frame_end = frame end
                    else -- Power Pin
                        if not power_pin_frame_start or frame < power_pin_frame_start then power_pin_frame_start = frame end
                        if not power_pin_frame_end or frame > power_pin_frame_end then power_pin_frame_end = frame end
                    end

                    data[data_head][frame] = x
                    data[data_head + 1][frame] = y

                else -- invalid data
                    if mode == "detected" then
                        -- It may be the "Frame	X pixels	Y pixels" line so let it pass once
                        mode = "logging"
                    elseif mode == "logging" then
                        -- It could be the start of the next section so send it back to detect again
                        mode = "detecting" data_head = nil
                        goto backagain
                end end

            else -- line without indent
                if mode == "detected" then
                    return err("[aka.ortho-mo] Malformatted AAE data")
                elseif mode == "logging" then
                    -- It could be the start of the next section so send it back to detect again
                    mode = "detecting" data_head = nil
                    goto backagain
    end end end end

    if frz_fax_frame_start then
        for frame=frz_fax_frame_start,frz_fax_frame_end do
            if data[1][frame] then
                x               = data[1][frame]
                y               = data[2][frame]
            end
            data[1][frame]      = nil
            data[2][frame]      = nil
            data[1][frame - frz_fax_frame_start + 1]    = x
            data[2][frame - frz_fax_frame_start + 1]    = y
    end end

    if power_pin_frame_start then
        x = {}
        for frame=power_pin_frame_start,power_pin_frame_end do
            if data[3][frame] then
                x[3]            = data[3][frame]
                x[4]            = data[4][frame]
            elseif not data[3][frame] and not x[3] then
                for grame=frame,power_pin_frame_end do
                    if data[3][grame] then
                        x[3]    = data[3][grame]
                        x[4]    = data[4][grame]
                        break
                end end
                return err("[aka.ortho-mo] Missing Power Pin-0002")
            end
            if data[5][frame] then
                x[5]            = data[5][frame]
                x[6]            = data[6][frame]
            elseif not data[5][frame] and not x[5] then
                for grame=frame,power_pin_frame_end do
                    if data[5][grame] then
                        x[5]    = data[5][grame]
                        x[6]    = data[6][grame]
                        break
                end end
                return err("[aka.ortho-mo] Missing Power Pin-0003")
            end
            if data[7][frame] then
                x[7]            = data[7][frame]
                x[8]            = data[8][frame]
            elseif not data[7][frame] and not x[7] then
                for grame=frame,power_pin_frame_end do
                    if data[7][grame] then
                        x[7]    = data[7][grame]
                        x[8]    = data[8][grame]
                        break
                end end
                return err("[aka.ortho-mo] Missing Power Pin-0004")
            end
            if data[9][frame] then
                x[9]            = data[9][frame]
                x[10]           = data[10][frame]
            elseif not data[9][frame] and not x[9] then
                for grame=frame,power_pin_frame_end do
                    if data[9][grame] then
                        x[9]    = data[9][grame]
                        x[10]   = data[10][grame]
                        break
                end end
                return err("[aka.ortho-mo] Missing Power Pin-0005")
            end

            data[3][frame]      = nil
            data[4][frame]      = nil
            data[5][frame]      = nil
            data[6][frame]      = nil
            data[7][frame]      = nil
            data[8][frame]      = nil
            data[9][frame]      = nil
            data[10][frame]     = nil
            data[3][frame - power_pin_frame_start + 1]  = x[3]
            data[4][frame - power_pin_frame_end + 1]    = x[4]
            data[5][frame - power_pin_frame_start + 1]  = x[5]
            data[6][frame - power_pin_frame_end + 1]    = x[6]
            data[7][frame - power_pin_frame_start + 1]  = x[7]
            data[8][frame - power_pin_frame_end + 1]    = x[8]
            data[9][frame - power_pin_frame_start + 1]  = x[9]
            data[10][frame - power_pin_frame_end + 1]   = x[10]
    end end

    if not frz_fax_frame_start and not power_pin_frame_start then
        return err("[aka.ortho-mo] ortho-mo requires either Aegisub-Orthographic-Motion Data or Power Pin data to work")
    end

    return ok(data)
end



ortho_mo = function(sub, sel, act)
    local data
    local sels
    local dialog
    local buttons
    local button_ids
    local button
    local result_table
    
    data = get_clipboard()
        :okOr()
        :andThen(parse_AAE)
        :andThen(function(data)
            if data[1][1] then return ok(data)
            else return err() end end)
    if data:isOk() then
        return apply_AAE(sub, sel, act, data:unwrap())
    end

    aegisub.debug.out("Catch")
end



local ILL = require("ILL.ILL")
apply_AAE_style_cache = nil
apply_AAE = function(sub, sel, act, data)
    local error
    local more_error
    local sel_initial_len
    local head
    local line
    local frame_start
    local frame_end

    error = none()
    more_error = function(text)
        error = error:mapOr(text, function(existing_text) return existing_text .. "\n" .. text end)
    end

    apply_AAE_style_cache = {}

    sel_initial_len = #sel
    head = 1
    for i=1,sel_initial_len do
        line = sub[sel[i]]
        frame_start = aegisub.frame_from_ms(line.start_time)
        frame_end = aegisub.frame_from_ms(line.end_time)

        if frame_end - frame_start == 1 then
            apply_AAE_line(sub, line, data[1][head], data[2][head])
            if head >= #data[1] then head = 1 else head = head + 1 end

            sub[sel[i]] = line
        elseif frame_end - frame_start > 1 then
            -- Yay no explaining what happens here
            line.start_time = aegisub.ms_from_frame(frame_start)
            line.end_time = aegisub.ms_from_frame(frame_start + 1)
            
            apply_AAE_line(sub, line, data[1][head], data[2][head])
            if head >= #data[1] then head = 1 else head = head + 1 end

            sub[sel[i]] = line
            for j=1,frame_end-frame_start-1 do
                line.start_time = aegisub.ms_from_frame(frame_start + j)
                line.end_time = aegisub.ms_from_frame(frame_start + j + 1)

                apply_AAE_line(sub, line, data[1][head], data[2][head])
                if head >= #data[1] then head = 1 else head = head + 1 end

                sub.insert(sel[i] + 1, line)
                table.insert(sel, sel[i])
                if act >= sel[i] then act = act + 1 end
                for k=i,sel_initial_len do sel[k] = sel[k] + 1 end
            end
        else -- frame_end - frame_start < 1
            aegisub.debug.out(2, "[aka.ortho-mo] Skipping line of 0 frame long")
    end end
    if head ~= 1 then
        aegisub.debug.out(1, "[aka.ortho-mo] The length of selected lines mismatches the length of AAE data")
    end

    return sel, act
end
apply_AAE_line = function(sub, line, x_radian, y_radian)
    local clearTag
    local setTagSingle
    local cleanTag
    local getTagSingle
    local to_write
    local fscx
    local fscy

    clearTag = function(line, tag)
        repeat
            --                                        ^(.*{[^}]*)\\frz[%-%d%.%(%) ]*([^}]*}.*)$
            local match_1, match_2 = line.text:match("^(.*{[^}]*)\\" .. tag .. "[%-%d%.%(%) ]*([^}]*}.*)$")
            if match_1 then line.text = match_1 .. match_2
            else return end
        until false
    end

    setTagSingle = function(line, tag, value)
        local match_1, match_2 = line.text:match("^({[^}]*)(}.*)$")
        if match_1 then line.text = match_1 .. "\\" .. tag .. string.format("%.3f", value) .. match_2
        else line.text = "{\\" .. tag .. string.format("%.3f", value) .. "}" .. line.text end
    end

    cleanTag = function(line, tag)
        repeat
            --                                        ^({[^}]*)\\fscx[%-%d%.%(%) ]*([^}]*\\fscx[%-%d%.%(%) ]*[^}]*}.*)$
            local match_1, match_2 = line.text:match("^({[^}]*)\\" .. tag .. "[%-%d%.%(%) ]*([^}]*\\" .. tag .. "[%-%d%.%(%) ]*[^}]*}.*)$")
            if match_1 then line.text = match_1 .. match_2
            else return end
        until false
    end

    getTagSingle = function(line, tag)
        --                               ^{[^}]*\\fscx *%(? *([%-%d.]+) *%)? *[^}]-}
        return tonumber(line.text:match("^{[^}]*\\" .. tag .. " *%(? *([%-%d.]+) *%)? *[^}]-}"))
    end

    getStyleTag = function(sub, line, tag_name)
        local enil

        if apply_AAE_style_cache[line.style] then
            return apply_AAE_style_cache[line.style][tag_name]
        end 
        for i=1,#sub do
            enil = sub[i]
            if enil.name == line.style then
                apply_AAE_style_cache[line.style] = enil
                return enil[tag_name]
            elseif enil.style then return end
    end end

    clearTag(line, "frx")
    clearTag(line, "fry")
    clearTag(line, "frz")
    clearTag(line, "fax")
    clearTag(line, "fay")
    cleanTag(line, "fscx")
    cleanTag(line, "fscy")

    to_write = math.deg(x_radian) if to_write >= 0.0005 and to_write < 359.9995 and getStyleTag(sub, line, "angle") == 0 then
    setTagSingle(line, "frz", to_write) end
    fscx = getTagSingle(line, "fscx") or getStyleTag(sub, line, "scale_x") or 100
    fscy = getTagSingle(line, "fscy") or getStyleTag(sub, line, "scale_y") or 100
    to_write = math.tan(y_radian - math.pi / 2 - x_radian) / (fscx / fscy) if to_write <= -0.0005 or to_write > 0.0005 then
    setTagSingle(line, "fax", to_write) end
end


if hasDepCtrl then
    DepCtrl:registerMacros({
        { "Aegisub-Orthographic-Motion", "Apply \\frz and \\fax to subtitle lines from AAE data", ortho_mo }
    })
else
    aegisub.register_macro("Aegisub-Orthographic-Motion", "Apply \\frz and \\fax to subtitle lines from AAE data", ortho_mo)
end
