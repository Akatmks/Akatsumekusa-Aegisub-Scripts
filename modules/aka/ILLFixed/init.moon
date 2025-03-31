-- aka.ILLFixed
-- Copyright (c) 2023 Alen and Ruan Dias

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

versioning =
	name: "ILLFixed"
	description: "Module aka.ILLFixed"
	version: "1.1.1"
	author: "Alen, Ruan Dias, and Akatsumekusa"
	namespace: "aka.ILLFixed"
	requiredModules: "[{ \"moduleName\": \"ILL.ILL\" }]"


version = (require "l0.DependencyControl")
	name: versioning.name,
	description: versioning.description,
	version: versioning.version,
	author: versioning.author,
	moduleName: versioning.namespace,
	url: "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
	feed: "https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json",
	[1]: { { "ILL.ILL" } }

ILL = version\requireModules!
import Aegi, Config, Math, Table, Util, UTF8, Ass, Curve, Path, Point, Segment, Line, Tag, Tags, Text, Font from ILL

-- sets the final value of the text
Ass.__base.setText = (l) ->
	if Util.checkClass l.text, "Text"
		-- aka.ILLFixed Modified
		-- if l.isShape
		-- 	l.text = l.tags\__tostring! .. l.shape
		-- 	return
		copyInstance = Table.copy l.text
		l.text = l.text\__tostring!
		return copyInstance
	elseif l.tags
		local tags
		if Util.checkClass l.tags, "Tags"
			tags = Table.copy l.tags
			tags\clear l.styleref
			tags = tags\__tostring!
		else
			tags = l.tags
		if l.isShape
			l.text = tags .. l.shape
		else
			l.text = tags .. l.text_stripped
	elseif l.isShape and l.shape
		l.text = l.shape

with ILL
	.version = version
	.versioning = versioning

return version\register ILL
