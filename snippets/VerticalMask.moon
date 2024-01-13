-- VerticalMask
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

ref = sub[act]
line = Table.copy ref

Line.process ass, ref
ref_clip = ref.data["clip"]
ref_clip[1] = math.floor ref_clip[1]
ref_clip[2] = math.floor ref_clip[2]
ref_clip[3] = math.ceil ref_clip[3]
ref_clip[4] = math.ceil ref_clip[4]

frame_number = aegisub.project_properties!.video_position
frame = aegisub.get_frame frame_number

for x = ref_clip[1], ref_clip[3] - 1
  with line
    .layer = .layer == 0 and 0 or .layer - 1
    .text = (string.format [[{\pos(0,0)\an7\bord0\shad0\blur0\c%s]], frame\getPixelFormatted x, ref_clip[2]) ..
            (string.format [[\p1}m %d %d l %d %d %d %d %d %d %d %d]], x, ref_clip[2], x + 1, ref_clip[2],
                                                                      x + 1, ref_clip[4], x, ref_clip[4],
                                                                      x, ref_clip[2])
  ass\insertLine line, act - ass.i - 1 + x - ref_clip[1]

ass\getNewSelection!
