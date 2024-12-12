<table><tr>
<th align="center" colspan="2"><hr /><h3>Table of Contents</h3><hr /></th>
</tr><tr>
<td>

***DependencyControl***  
`https://raw.githubusercontent.com/Akatmks/Akatsumekusa-Aegisub-Scripts/master/DependencyControl.json`  
***Motion Tracking***  
– [aae-export](#aae-export)  
***Typesetting Scripts***  
– [aka.99PercentTags](#aka99percenttags)  
– [aka.SandBox](#akasandbox)  
– [aka.BackupSection](#akabackupsection--akadupe-and-not-comment)  
– [aka.Cycles](#akacycles)  
– [aka.dupe-and-not-comment](#akabackupsection--akadupe-and-not-comment)  
***Typesetting Snippets***  
– [Typesetting Snippets](#typesetting-snippets)  
***farn huah***  
– [NN.farnhuah](#nnfarnhuah)  
***Aegisub VapourSynth Scripts***  
– [tkinter_alternatives](#tkinter_alternatives)  

</td>
<td>

***Modules***  
– [aka.uikit](#akauikit)  
– [aka.actor](#akaactor)  
– [aka.CIELab](#akacielab)  
– [aka.config](#akaconfig--akaconfig2)  
– [aka.config2](#akaconfig--akaconfig2)  
– [aka.optimising](#akaoptimising)  
– [aka.outcome](#akaoutcome)  
– [aka.singlesimple](#akasinglesimple)  
– [aka.threads](#akathreads)  
– [aka.unicode](#akaunicode)  
– [aka.unsemantic](#akaunsemantic)  
***Thirdparty Modules***  
– [effil](#effil)  
– [request](#request)  
– [StackTracePlus](#stacktraceplus)
  
</td>
</tr><tr>
<th align="center" colspan="2"><hr /></th>
</tr><tr>
<td><img width="2000" height="1px" /></td>
<td><img width="2000" height="1px" /></td>
</tr></table>

## aae-export

<img src="https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/af583631-7554-45a4-ab17-ae1ef2a14932" alt="AAE Export Function Preview" width="186" align="left" />

AAE Export is a Blender add-on that exports tracks and plane tracks into [Aegisub-Motion](https://github.com/TypesettingTools/Aegisub-Motion) and [Aegisub-Perspective-Motion](https://github.com/Zahuczky/Zahuczkys-Aegisub-Scripts) compatible AAE data.  

–　[Download (Windows)](scripts/aae-export-windows/aae-export.py)  
–　[Download (Linux x86_64)](scripts/aae-export-linux-x86_64/aae-export.py)  
–　[Download (Linux aarch64)](scripts/aae-export-windows/aae-export.py)  
–　[Download (Mac)](scripts/aae-export-mac/aae-export.py)  
–　[Tutorial 1: Install AAE Export](docs/aae-export-tutorial.md#tutorial-1-install-aae-export)  
–　[Tutorial 2: Basic motion tracking](docs/aae-export-tutorial.md#tutorial-2-basic-motion-tracking)  
–　[Tutorial 3: Introducing smoothing feature](docs/aae-export-tutorial.md#tutorial-3-introducing-smoothing-feature)  
–　[Tutorial 4: Tracking perspective](docs/aae-export-tutorial.md#tutorial-4-tracking-perspective)  
–　[Tutorial: Blender Motion Tracking for Fansubbing by PhosCity](https://fansubbers.miraheze.org/wiki/User:PhosCity/Blender_Motion_Tracking_for_Fansubbing)  

Thanks to  

–　arch1t3cht for helping in improving algorithms and for developing the original AAE Export (Power Pin) script.  
–　bucket3432, Noroino Hanako for helping with AAE Export's function.  
–　bucket3432, petzku and others for helping with UI/UX design.  
–　Martin Herkt for developing the original AAE Export script in 2012.
<br clear="left" />

*License information*  
– *aae-export was originally released by Martin Herkt under ISC License. Since then, aae-export has been completely rewritten, with every original line replaced. It is now released under a single MIT License.*  
– *[aae-export-install-dependencies](tools/aae-export-install-dependencies) is a helper tool with its binary included in Linux x86_64 and Mac version of aae-export. The tool is released under MIT License, using [Qt](https://www.qt.io/) libraries under LGPLv3.*  
– *[aae-export-base122](tools/aae-export-base122) is a helper tool with its binary included in Linux x86_64 and Mac version of aae-export. It is a wrapper of Kevin Albertson's [libbase122](https://github.com/kevinAlbs/libbase122) library, and is released under Apache License.*  

## aka.99PercentTags

99%Tags is a script for adding and modifying tags on subtitle lines. It combines the base functions of [HYDRA](https://unanimated.github.io/ts/scripts-manuals.htm#hydra), [PhosCity's Edit Tags](https://phoscity.github.io/Aegisub-Scripts/Edit%20Tags/), [Recalculator](https://unanimated.github.io/ts/scripts-manuals.htm#recalculator), [NecrosCopy](https://unanimated.github.io/ts/scripts-manuals.htm#necroscopy), and [LuaIntepret](https://github.com/TypesettingTools/lyger-Aegisub-Scripts#luainterpret) into a simple, easytouse, HYDRA-like interface. It can facilitate simple operations such as setting tag values across multiple lines or performing arithmetic calculations on tag values, but it also provides full Lua interface for complex operations.  

*To get started:*  
– Install the script.  
– Use it the same way as ua.HYDRA. If you want to set `\fscx` to 150, enter `150` in the text field for `fscx`.  
– Try out simple arithmetic calculations. If you want to multiply `\fscx` by 125%, enter `*1.25` in the text field for `fscx`.  
– Explore the builtin „Help“ panel for a detailed guide to all the features of 99%Tags.  

*Features:*  
– Carefully designed Lua system that minimises typing for simple operations.  
– Easytouse Lua interface that makes complex operations easier to code than [aka.Sandbox](#akasandbox).  
– Builtin „Help“ panel showcasing example usages and explaining all the details.  
– Bultiin import and export feature as well as an internal preset system for ease of reusing and sharing operations. See [Typesetting Snippets](#typesetting-snippets) for some snippets by Akatsumekusa.    

*Relations between 99%Tags and HYDRA, PhosCity's Edit Tags, or other similar scripts:*  
The idea of 99%Tags is not to replace [HYDRA](https://unanimated.github.io/ts/scripts-manuals.htm#hydra), [PhosCity's Edit Tags](https://phoscity.github.io/Aegisub-Scripts/Edit%20Tags/), [NecrosCopy](https://unanimated.github.io/ts/scripts-manuals.htm#necroscopy), or any other similar scripts (maybe except [Recalculator](https://unanimated.github.io/ts/scripts-manuals.htm#recalculator)). There are many situations where these scripts would be more convenient than 99%Tags. It would be a good idea to learn these scripts and use them when they are the most convenient.  

*Comparing against [aka.Sandbox](#akasandbox) for complex operations:*  
– For any operations that can be performed in 1 pass, especially modifying ASS tags, 99%Tags would be faster to code.  
– For any operations that need to compare between all selected lines and can't be performed in 1 pass, or operations that would need to create tags blocks or modify multiple tags blocks at once, [aka.Sandbox](#akasandbox) would be the better choice.  

<img src="https://github.com/user-attachments/assets/f595f986-3d47-406a-a8db-c51f3a79d2b3" alt="99%Tags Function Preview" width="542"/>

## aka.Sandbox

aka.Sandbox is a script similar to [lyger.LuaInterpret](https://github.com/TypesettingTools/lyger-Aegisub-Scripts/tree/master#user-content-LuaInterpret) but relies on libraries such as [ILL.ILL](https://github.com/TypesettingTools/ILL-Aegisub-Scripts) and [l0.ASSFoundation](https://github.com/TypesettingTools/ASSFoundation) for easy modification of subtitles.  

*Unique features:*  
– MoonScript support in addition to Lua.  
– Commonly used libraries already required and initialised. No need to manually write `require`s.  
– Builtin import and export of code snippets, as well as an internal preset system.  
– Better error handling. If an error occurs during execution, the editor window will open back up to make it easier to tweak the code.  

*Thanks to*  
– bucket3432 for developing the original `bucket.Sandbox` script.  
– Zahuczky and PhosCity for suggesting libraries to be required and made available in scope.  

<img src="https://github.com/user-attachments/assets/0281aea4-ae68-402d-9884-120db61059ad" alt="99%Tags Function Preview" width="770"/>

## aka.BackupSection & aka.dupe-and-not-comment

aka.BackupSection and aka.dupe-and-not-comment are similar in function to [garret.dupe-and-comment](https://github.com/garret1317/aegisub-scripts#dupe-and-comment) but arrange the new lines in different ways.  

To backup using aka.BackupSection, select the lines to backup and click „Backup“. To start from a previous backup, select the previously commented lines and click „Backup“.  

Comparing the three scripts,  
when applied to the following selection:  
<img src="https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/cfac5853-7e0d-463b-a977-82b17aa63770" alt="99%Tags Function Preview" width="600"/>

aka.BackupSection:  
<img src="https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/d8da70be-d684-437e-8faa-c3d1f0cf4419" alt="99%Tags Function Preview" width="600"/>

garret.dupe-and-comment:  
<img src="https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/79de7767-e432-4416-9904-6bcfb15f6067" alt="99%Tags Function Preview" width="600"/>

aka.dupe-and-not-comment:  
<img src="https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/460b0ba8-dd71-4610-83e3-4354db1b232e" alt="99%Tags Function Preview" width="600"/>

## aka.Cycles

aka.Cycles is largely the same as [ua.Cycles](https://github.com/unanimated/luaegisub) but with a configuration editor inside Aegisub.  

## NN.farnhuah

NN.farnhuah is an Aegisub frontend for [zhconvert](https://zhconvert.org/).  

To use NN.farnhuah, select the line for farnhuah and click „farn huah“. To switch between chs and cht subtitles, click „chie huann chs her cht“.  
On first launch, NN.farnhuah will show a configuration window. Create your own configuration from zhconvert's [documentation](https://docs.zhconvert.org/api/convert/), or click „Apply Preset“ to use the default config from SweetSub.  

## Typesetting Snippets

**[Fix Multiline fax (99%Tags)](snippets/Fix%20Multiline%20fax.json)**  
Fix alignment at `\N` for `\frz\fax` typeset signs.  
*How to Use:* Typeset, use [ua.NecrosCopy](https://github.com/Akatmks/unanimated-Aegisub-Scripts/blob/master/uam.NecrosCopy.lua) to split at \N, then apply this snippets using [99%Tags](#aka99percenttags).  

**[Fix Vertical Source Han (99%Tags)](snippets/Fix%20Vertical%20Source%20Han.json)**  
Fix render issues for vertical Source Han fonts.  
*How to Use:* Typeset under libass, use [zf.split](https://github.com/TypesettingTools/zeref-Aegisub-Scripts?tab=readme-ov-file#--macro-splits-text-by-)'s „Splits Text By Chars“ feature, then apply this snippets using [99%Tags](#aka99percenttags).  
*Limitations:* Only supports signs without perspective. `\pos` correction only supports `\an1`, `\an4` and `\an7`.  
*Notes:* Supporting signs with `\frz\fax` would probably be fairly easy. Send me a message if you need it.  

## tkinter_alternatives

tkinter_alternatives.py is a fix for Aegisub VapourSynth Default Video Script if your Python installation does not come with Tkinter.

[Download](vapoursynth/tkinter_alternatives.py) the file and put it in `automation/vapoursynth` in your Aegisub install location.  

Open Aegisub, open „View > Options“ and select „VapourSynth“. In „Default Video Script“, find the import aegisub_vs line:  
```python
import aegisub_vs as a
```
Add the following line below import aegisub_vs line:  
```python
import tkinter_alternatives as ask
```
Find the line to generate keyframe:  
```python
__aegi_keyframes = a.get_keyframes(filename, clip, __aegi_keyframes, generate=a.GenKeyframesMode.ASK)
```
Replace the line with:  
```python
__aegi_keyframes = a.get_keyframes(filename, clip, __aegi_keyframes, generate=a.GenKeyframesMode.ASK, ask_callback=ask.callback)
```

## aka.uikit

aka.uikit is a powerful UI framework for aegisub dialogs. Creating a dialog is as simple as:  
```moon
with dialog = adialog { width: 6 }
    \label { label: "Hello World!" }
with buttons = abuttons!
    \ok "OK"
    \close "Cancel"
button, result = (adisplay dialog, buttons)\resolve!
if buttons\is_ok button
    aegisub.debug.out "Hooray!"
```

View the document at [docs/Using aka.uikit.md](docs/Using%20aka.uikit.md).  

## aka.actor

aka.actor is a flag system visible to the user.  
For example, when you backup a line with [aka.BackupSection](#akabackupsection--akadupe-and-not-comment), a `backup` flag will be added to the commented line.  

Check whether a flag exists and the number of times it exists on line:  
```lua
aactor.flag(line, "backup")
```
Set flag on line:  
```lua
aactor.setFlag(line, "backup")
```

Other functions include:  
```lua
aactor.flag(line, flag)
aactor.setFlag(line, flag)
aactor.clearFlag(line, flag)
aactor.toggleFlag(line, flag)
aactor.onemoreFlag(line, flag)
aactor.onelessFlag(line, flag)
```

`aactor.field` is a [aka.singlesimple](#akasinglesimple) config specifying the field to place the flags. It has three possible values, `actor`, `effect` and `style`. It is synced across all scripts using aka.actor.  

## aka.CIELab

aka.CIELab is a module that converts between sRGB RGB with pure power curve 2.4 and CIELab.  
```moon
import Colour from require "aka.CIELab"
L, a, b = (Colour.fromBT1886RGB R, G, B)\toCIELab!
L, C, h = (Colour.fromPixel (Line.tagsBlocks ass, line)[1].data.color1)\toCIELCh!
X, Y, Z = (Colour.fromCIELCh L, C, h)\toXYZ!
```

Thanks to Chortos-2 and arch1t3cht for teaching me about BT.709 and gamma 2.4. I might still manage to screw something up in this module and it'll all be my fault, not theirs.  

## aka.config & aka.config2

aka.config is a config module that features a builtin JSON editor with pretty JSON. aka.config2 provides the base JSON and file system functions while aka.config implements three readytouse config functions with GUI.  

Readytouse config functions include:
```lua
aconfig.read_and_validate_config_if_empty_then_default_or_else_edit_and_save(self, config, config_supp, validation_func)
aconfig.read_and_validate_config_or_else_edit_and_save(self, config, config_supp, validation_func)
aconfig.read_edit_validate_and_save_config(self, config, config_supp, validation_func)
```

Detailed tutorial is available at [docs/Using aka.config and aka.config2.md](docs/Using%20aka.config%20and%20aka.config2.md).  

## aka.optimising

aka.optimising introduces a timing function for debugging.  

Set `aka.optimising.json` under DependencyControl's `configDir` to `{ true }`. Use `optimising.start()` to start the timer. Use `optimising.lap(lap_name)` to print time to `aegisub.debug.out`.  

## aka.outcome

aka.outcome introduces `Result` and `Option` similar to Rust's `std::result::Result` and `std::option::Option`. It is based on mtdowling's [Outcome](https://github.com/mtdowling/outcome) and is used by `aka.config`, `aka.config` and many other Akatsumkusa's scripts.  

Detailed introduction is available at [docs/Using aka.outcome.md](docs/Using%20aka.outcome.md).  

*License Information*  
– *Outcome is originally released by Michael Dowling under MIT License.*  
– *It is modified with exisiting functions changed and new functions added by Akatsumekusa.*  

## aka.singlesimple

aka.singlesimple is a config module. It stores one enum per config and the enum is synced\* across all scrips requesting the same config.  

```lua
-- Create a config
config = ss.make_config("aka.Testing", possible_values, default_value)
-- Get the current value
config:value()
-- Set the value
config:setValue(value)
```

\*: Loosely.  

Detailed tutorial is available at [docs/Using aka.singlesimple.md](docs/Using%20aka.singlesimple.md).  

## aka.threads

aka.threads is a synced [aka.singlesimple](#akasinglesimple) config storing the number of threads used when multithreading.  

aka.threads defaults to the number of logical processors on the system. Any multithreading script could get the number of threads to use from this config and also change this config at user's request.  
```lua
threads = require("aka.threads")
-- Get the number of threads to use
threads.threads()
-- Change this config for all scripts
threads.setThreads(8)
```

## aka.unicode

aka.unicode extends aegisub.unicode with a `unicode.char(codepoint)` function to turn codepoints back to characters.  

## aka.unsemantic

aka.unsemantic is a version compare module that supports basic version format with two or three positive numbers separated by periods.  

```lua
V = require("aka.unsemantic").V
assert(V"1.1.2" > V"1.0.24")
```

Two-number version is treated as three-number version with a patch number of `-1``.  

```lua
assert(V"2.1.0" > V"2.1")
```

## effil

[effil](https://github.com/effil/effil) is a multithreading library for Lua.  

Add `aka.effil` to DependencyControl's required modules. View the documents at the [original repository](https://github.com/effil/effil).  

It is recommended to use the synced module [aka.threads](#akathreads) for the number of threads to use when multithreading.  

*License Information*  
– *effil is copyrighted to Mikhail Kupriyanov and Ilia Udalov and is licensed under MIT License.*  

## request

[LuaJIT-Request](https://github.com/LPGhatguy/luajit-request) is a request module for LuaJIT based on libcurl.  

Add `aka.request` to DependencyControl's required modules. View the documents at the [original repository](https://github.com/LPGhatguy/luajit-request).  

*License Information*  
– *LuaJIT-Request is copyrighted to Lucien Greathouse and is licensed under zlib License. It is adapted to Aegisub environment with minimum modifications.*  

## StackTracePlus

[StackTracePlus](https://github.com/ignacio/StackTracePlus) provides enhanced stack traces for LuaJIT.  
```lua
require("aka.StackTracePlus")()
```
```moon
(require "aka.StackTracePlus")!
```

*License Information*  
– *StackTracePlus is copyrighted to Ignacio Burgueño and is licensed under MIT License. It is adapted to Aegisub environment with some modifications.*  
