-- aka.uikit
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

versioning =
	name: "ILLFixed"
	description: "Module aka.ILLFixed"
	version: "1.0.2"
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
import Aegi, Line, Math, Table, Util, UTF8, Tags, Text, Path, Font from ILL

-- processes the line values by extending its information pool
Line.__base.process = (ass, l) ->
	{:styles, :meta} = ass
	{:res_x, :res_y, :video_x_correct_factor} = meta

	if type(l.text) == "string" and not l.isShape 
		l.text = Text l.text

	if not l.data and not l.isShape
		l.text\moveToFirstLayer!

	with l
		.text_stripped = .isShape and .text\gsub("%b{}", "") or .text\stripped!
		.duration = .end_time - .start_time
		textIsBlank = Util.isBlank .text_stripped

		if not .styleref or .reset
			if styleValue = .reset and styles[.reset.name] or styles[.style]
				.styleref = Table.copy styleValue
			else
				Aegi.debug 2, "WARNING: Style not found: #{.style}\n"
				.styleref = Table.copy styles[next styles]

			-- gets the alpha and color values separately
			.styleref.alpha  = "&H00&"
			.styleref.alpha1 = Util.convertColor "alpha_fs", .styleref.color1
			.styleref.alpha2 = Util.convertColor "alpha_fs", .styleref.color2
			.styleref.alpha3 = Util.convertColor "alpha_fs", .styleref.color3
			.styleref.alpha4 = Util.convertColor "alpha_fs", .styleref.color4
			.styleref.color1 = Util.convertColor "color_fs", .styleref.color1
			.styleref.color2 = Util.convertColor "color_fs", .styleref.color2
			.styleref.color3 = Util.convertColor "color_fs", .styleref.color3
			.styleref.color4 = Util.convertColor "color_fs", .styleref.color4

			-- adds tag values that are not part of the default style composition
			.data = Table.copy .styleref
			for tag, data in pairs ASS_TAGS
				{:style_name, :typer, :value} = data
				unless style_name or typer == "coords"
					.data[tag] = value

		-- sets the values found in the tags to the style
		.tags or= Tags .isShape and .text\match("%b{}") or .text.tagsBlocks[1]\get!
		for {:tag, :name} in *.tags\split!
			{:style_name, :value} = tag
			if style_name
				.data[style_name] = value
			elseif .isShape or .data[name]
				.data[name] = value

		-- as some tags can only appear once this avoids unnecessary
		-- capture repetitions which minimizes processing
		unless .reset
			values = Line.firstCategoryTags l, res_x, res_y
			for k, v in pairs values
				.data[k] = v
		else
			for name in *{"an", "pos", "move", "org", "fad", "fade"}
				if value = .reset.data[name]
					.data[name] = value

		font = Font .data

		-- if it's a shape, this information are irrelevant
		unless .isShape
			-- gets the value of the width of a space
			.space_width = font\getTextExtents(" ").width
			.space_width *= video_x_correct_factor

			-- spaces that are on the left and right of the text
			.prevspace = .text_stripped\match("^(%s*).-%s*$")\len! * .space_width
			.postspace = .text_stripped\match("^%s*.-(%s*)$")\len! * .space_width

			-- removes the spaces between the text
			.text_stripped = .text_stripped\match "^%s*(.-)%s*$"
		else
			-- to make everything more dynamic
			.shape = .text_stripped
			.text_stripped = ""

		-- gets the metric values of the text
		-- aka.ILLFixed Modified
		textValue = (textIsBlank or .isShape) and "" or .text_stripped
		textExtents = font\getTextExtents textValue
		textMetrics = font\getMetrics textValue
		.width = textExtents.width * video_x_correct_factor
		.height = textExtents.height
		.ascent = textMetrics.ascent
		.descent = textMetrics.descent
		.internal_leading = textMetrics.internal_leading
		.external_leading = textMetrics.external_leading

		-- text alignment
		{:an} = .data

		-- effective margins
		.eff_margin_l = .margin_l > 0 and .margin_l or .data.margin_l
		.eff_margin_r = .margin_r > 0 and .margin_r or .data.margin_r
		.eff_margin_t = .margin_t > 0 and .margin_t or .data.margin_t
		.eff_margin_b = .margin_b > 0 and .margin_b or .data.margin_b
		.eff_margin_v = .margin_t > 0 and .margin_t or .data.margin_v

		-- X-axis alignment
		switch an
			when 1, 4, 7
				-- Left aligned
				.left = .eff_margin_l
				.center = .left + .width / 2
				.right = .left + .width
				.x = .left
			when 2, 5, 8
				-- Centered aligned
				.left = (res_x - .eff_margin_l - .eff_margin_r - .width) / 2 + .eff_margin_l
				.center = .left + .width / 2
				.right = .left + .width
				.x = .center
			when 3, 6, 9
				-- Right aligned
				.left = res_x - .eff_margin_r - .width
				.center = .left + .width / 2
				.right = .left + .width
				.x = .right

		-- Y-axis alignment
		switch an
			when 7, 8, 9
				-- Top aligned
				.top = .eff_margin_t
				.middle = .top + .height / 2
				.bottom = .top + .height
				.y = .top
			when 4, 5, 6
				-- Mid aligned
				.top = (res_y - .eff_margin_t - .eff_margin_b - .height) / 2 + .eff_margin_t
				.middle = .top + .height / 2
				.bottom = .top + .height
				.y = .middle
			when 1, 2, 3
				-- Bottom aligned
				.bottom = res_y - .eff_margin_b
				.middle = .bottom - .height / 2
				.top = .bottom - .height
				.y = .bottom

with ILL
	.version = version
	.versioning = versioning

return version\register ILL
