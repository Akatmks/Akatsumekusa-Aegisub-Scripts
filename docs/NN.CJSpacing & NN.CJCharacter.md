
## NN.CJSpacing && NN.CJCharacter

These two modules are designed to handle one thing and one thing only, auto spacing in Japanese and Chinese subtitles, yet it is extrememly complex.  

NN.CJCharacter only recognised common characters in subtitles. These are the basic types for the characters:   

<table>
  <tr>
    <td></td>
    <td align="center">Scriptio Continua</td>
    <td align="center">Space Separated</td>
  </tr>
  <tr>
    <td align="right"><code>C</code> (Kanji/Hanzi)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>H</code> (Hiragana)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>K</code> (Katakana)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>k</code> (Halfwidth Katakana)</td>
    <td align="center">○</td>
    <td align="center">×</td>
  </tr>
  <tr>
    <td align="right"><code>I</code> (Kana)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>b</code> (Bopomofo)</td>
    <td align="center">×</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>g</code> (Hangul)</td>
    <td align="center">×</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>a</code> (Alphabetical)</td>
    <td align="center">×</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>n</code> (Numeral)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>A</code> (Fullwidth Alphabetical)</td>
    <td align="center">○</td>
    <td align="center">×</td>
  </tr>
  <tr>
    <td align="right"><code>N</code> (Fullwidth Numeral)</td>
    <td align="center">○</td>
    <td align="center">×</td>
  </tr>
  <tr>
    <td align="right"><code>0</code> (Halfwidth Alphanumeric Symbol)</td>
    <td align="center">×</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>s</code> (Full/Half/Variablewidth Front/Rear Continuous Symbol),<br /><code>/</code> (Full/Half/Variablewidth Front/Rear Continuous Symbol Alternatives Available)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>-</code> (Full/Half/Variablewidth Strictly Front/Rear Continuous Symbol)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code><</code> (Full/Half/Variablewidth Strictly Front Continuous Rear Separated Symbol)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>></code> (Full/Half/Variablewidth Strictly Front Separated Rear Continuous Symbol)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code>S</code> (Full/Half/Variablewidth Strictly Front/Rear Separated Symbol)</td>
    <td align="center">○</td>
    <td align="center">○</td>
  </tr>
  <tr>
    <td align="right"><code> </code> (Space)</td>
    <td align="center">-</td>
    <td align="center">-</td>
  </tr>
</table>
