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

local ConfigHandler
local settings

local init_config
local check_config

init_config = function(ConfigHandler_)
    ConfigHandler = ConfigHandler or ConfigHandler_
    assert(ConfigHandler)
end

check_config = function()
    if not settings then
        local is_success
        local msg

        ConfigHandler = ConfigHandler_

        is_success, msg = ConfigHandler:load()
        if not is_success then  end
        settings = ConfigHandler.c.settings
        -- validate
    end
end

return function(ConfigHandler_)
    init_config(ConfigHandler_)



end