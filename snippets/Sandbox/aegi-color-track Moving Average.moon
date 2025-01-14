-- Please make sure you only have one valid colour tag for each frame
-- zah.aegi-color-track will not delete your original colour typesetting when inserting its own
-- It's possible you will have duplicate colour tags
-- Please make sure your colour tags is in the right order, from the first frame to the last frame
-- This Sandbox script doesn't check for either of these issues

-- Change here to match a different colour other than \c
colour = re.compile[[\\c(&H[0-9A-F]{6}&)]]

for line in *lines
 colours = {}
 for match in colour\gfind line.text
  table.insert colours, table.pack util.extract_color match
 count = #colours
 table.insert colours, 1, colours[1]
 table.insert colours, 1, colours[1]
 table.insert colours, colours[count + 2]
 table.insert colours, colours[count + 3]

 i = 3
 result = ""
 for match in colour\gsplit line.text
  result = result .. match
  if i <= count + 2
   r = (colours[i - 2][1] + colours[i - 1][1] + colours[i][1] + colours[i + 1][1] + colours[i + 2][1]) / 5
   g = (colours[i - 2][2] + colours[i - 1][2] + colours[i][2] + colours[i + 1][2] + colours[i + 2][2]) / 5
   b = (colours[i - 2][3] + colours[i - 1][3] + colours[i][3] + colours[i + 1][3] + colours[i + 2][3]) / 5
   result = result .. [[\c]] .. util.ass_color r, g, b
  i = i + 1
 line.text = result

lines\replaceLines!
