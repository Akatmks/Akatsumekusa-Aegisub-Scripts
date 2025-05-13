style = "Text - CN"

it = (sub, act) ->
 i = act
 ->
  i = i + 1
  i = 1 if i > #sub
  i

for i in it sub, act
 line = sub[i]
 if line.class == "dialogue" and not line.comment and line.style == style
  Line.process ass, line
  text = string.gsub line.text_stripped, "  ", "　"
  text = string.gsub text, " ", ""
  if (unicode.len text) >= 24
   return { i }, i

aegisub.debug.out "No line of the specific style is longer than 24 characters."
