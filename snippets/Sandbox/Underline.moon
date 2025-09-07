top_offset = 0
bottom_offset = 5
horizontal_offset = 0

for line, s, i, n in ass\iterSel!
 Line.extend ass, line
 Line.callBackExpand ass, line, nil, (line) ->
  path = switch line.data.an
   when 1
    Path { line.data.pos[1] - horizontal_offset,                                      line.data.pos[2] + top_offset,
           line.data.pos[1] + line.width - line.data.spacing + horizontal_offset,     line.data.pos[2] + bottom_offset }
   when 2
    Path { line.data.pos[1] - line.width / 2 - horizontal_offset,                     line.data.pos[2] + top_offset,
           line.data.pos[1] + line.width / 2 - line.data.spacing + horizontal_offset, line.data.pos[2] + bottom_offset }
   when 3
    Path { line.data.pos[1] - line.width - horizontal_offset,                         line.data.pos[2] + top_offset,
           line.data.pos[1] - line.data.spacing + horizontal_offset,                  line.data.pos[2] + bottom_offset }
   when 4
    Path { line.data.pos[1] - horizontal_offset,                                      line.data.pos[2] + line.height / 2 + top_offset, 
           line.data.pos[1] + line.width - line.data.spacing + horizontal_offset,     line.data.pos[2] + line.height / 2 + bottom_offset }
   when 5
    Path { line.data.pos[1] - line.width / 2 - horizontal_offset,                     line.data.pos[2] + line.height / 2 + top_offset,
           line.data.pos[1] + line.width / 2 - line.data.spacing + horizontal_offset, line.data.pos[2] + line.height / 2 + bottom_offset }
   when 6
    Path { line.data.pos[1] - line.width - horizontal_offset,                         line.data.pos[2] + line.height / 2 + top_offset,
           line.data.pos[1] - line.data.spacing + horizontal_offset,                  line.data.pos[2] + line.height / 2 + bottom_offset }
   when 7
    Path { line.data.pos[1] - horizontal_offset,                                      line.data.pos[2] + line.height + top_offset,
           line.data.pos[1] + line.width - line.data.spacing + horizontal_offset,     line.data.pos[2] + line.height + bottom_offset }
   when 8
    Path { line.data.pos[1] - line.width / 2 - horizontal_offset,                     line.data.pos[2] + line.height + top_offset,
           line.data.pos[1] + line.width / 2 - line.data.spacing + horizontal_offset, line.data.pos[2] + line.height + bottom_offset }
   when 9
    Path { line.data.pos[1] - line.width - horizontal_offset,                         line.data.pos[2] + line.height + top_offset,
           line.data.pos[1] - line.data.spacing + horizontal_offset,                  line.data.pos[2] + line.height + bottom_offset }
  with path
   \move -line.data.pos[1], -line.data.pos[2]
   line.shape = \export!
  ass\insertLine line, s
