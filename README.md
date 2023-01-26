## aae-export

<img src="https://user-images.githubusercontent.com/112813970/209281100-3d7dfa0b-1ccb-4918-8bef-6e136a29a1ec.jpg" alt="AAE Export Function Preview" width="186" align="left" />

AAE Export is a Blender add-on that exports tracks and plane tracks into [Aegisub-Motion](https://github.com/TypesettingTools/Aegisub-Motion/) and [Aegisub-Perspective-Motion](https://github.com/Zahuczky/Zahuczkys-Aegisub-Scripts/tree/daily_stream) compatible AAE data.  

–　[Download (Windows)](scripts/aae-export/aae-export.py)  
–　[Download (Linux x86_64)](scripts/aae-export-linux-x86_64/aae-export.py)  
–　[Download (Linux aarch64)](scripts/aae-export/aae-export.py)  
–　[Download (Mac)](scripts/aae-export-mac/aae-export.py)  
–　[Tutorial 1: Install AAE Export](docs/aae-export-tutorial.md#tutorial-1-install-aae-export)  
–　[Tutorial 2: Track a simple pan using tracking marker](docs/aae-export-tutorial.md#tutorial-2-track-a-simple-pan-using-tracking-marker)  
–　[Tutorial 3: Track perspective using plane track](docs/aae-export-tutorial.md#tutorial-3-track-perspective-using-plane-track)  

Thanks to  

–　arch1t3cht for helping in improving algorithms and for developing the original AAE Export (Power Pin) script.  
–　bucket3432, petzku and others for helping with UI/UX design.  
–　Martin Herkt for developing the original AAE Export script in 2012.  

The tutorial for the new smoothing feature is underway. For anyone who is interested, there is also a [more complex script](https://github.com/Akatmks/Non-Carbonated-Motion) in development. It will be much better at correcting tracking error or bias than current smoothing feature. There is no guarantee when that script will be finished but hope it will come sooner rather than later.<br clear="left" />

*License information*  
– *aae-export was originally released by Martin Herkt under ISC License. Since then, aae-export has been completely rewritten, with every original line replaced. It is now released under a single MIT License.*  
– *[aae-export-install-dependencies](tools/aae-export-install-dependencies) is a helper tool with its binary included in Linux x86_64 and Mac version of aae-export. The tool is released under MIT License, using [Qt](https://www.qt.io/) libraries under LGPLv3.*  
– *[aae-export-base122](tools/aae-export-base122) is a helper tool with its binary included in Linux x86_64 and Mac version of aae-export. It is a wrapper of Kevin Albertson's [libbase122](https://github.com/kevinAlbs/libbase122) library, and is released under Apache License.*  

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

* `Kanji/Hanzi`: or Kanji and Hanzi. This includes all the unified or compatibility CJK Ideographs in Unicode.  
* `Hiragana`: This contains all the common Hiragana, as well as `ゝ` and a few archaic characters like `𛀁`.  
* `Katakana`: This includes all the common fullwidth Katakana, as well as fullwidth Katakana for Ainu like `ㇰ`.  
* `Katakana Halfwidth`: This includes all the halfwidth Katakana.  
* `Katakana Taiwanese`: This includes the tone marks in Taiwanese Katakana.  
* `Kana`: This includes the Hentaigana.  
* `Hangul`: This includes all the precomposed Hangul and Hangul Jamo.  
* `Bopomofo`: This includes all the bopomofos as well as the five tone marks.  
* `Numerical Halfwidth`: This includes numerical digits from `0` to `9`, as well as decimal separators like `.` and other symbols like `%` and `€`.  
* `Latin Halfwidth`: This includes latin letters like `a` and `z`, letters with diacritic like `â` and `ž`, ligatures like `ﬁ` and other forms.  

