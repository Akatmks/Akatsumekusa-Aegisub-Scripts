style = "Text - CN"
threshold = 24
flag = "loooooong"

it = (sub, act) ->
 i = act - 1
 first = true
 ->
  i = i + 1
  i = 1 if i > #sub
  if i == act
   if first
    first = nil
    return i
   else
    return nil
  i

aactor = require "aka.actor"

total = 0
for i in it sub, act
 l = sub[i]
 line = Table.copy l
 if line.class == "dialogue" and not line.comment and line.style == style
  Line.process ass, line
  text = string.gsub line.text_stripped, "  ", "　"
  text = string.gsub text, " ", ""
  if (unicode.len text) >= threshold
   aactor.setFlag l, flag
   sub[i] = l
   logger\dump line.text_stripped
   total = total + 1
  else
   if aactor.flag l, flag
    aactor.clearFlag l, flag
    sub[i] = l

logger\dump (tostring total) .. " lines marked."
