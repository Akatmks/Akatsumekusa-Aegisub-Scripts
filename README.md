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

There is currently no tutorial for the smoothing feature, but there is a small [page](docs/aae-export-smoothing-technical-details.md) logging some of the details about the smoothing process.
<br clear="left" />

*License information*  
– *aae-export was originally released by Martin Herkt under ISC License. Since then, aae-export has been completely rewritten, with every original line replaced. It is now released under a single MIT License.*  
– *[aae-export-install-dependencies](tools/aae-export-install-dependencies) is a helper tool with its binary included in Linux x86_64 and Mac version of aae-export. The tool is released under MIT License, using [Qt](https://www.qt.io/) libraries under LGPLv3.*  
– *[aae-export-base122](tools/aae-export-base122) is a helper tool with its binary included in Linux x86_64 and Mac version of aae-export. It is a wrapper of Kevin Albertson's [libbase122](https://github.com/kevinAlbs/libbase122) library, and is released under Apache License.*  
