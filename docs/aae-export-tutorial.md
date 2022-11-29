## Table of contents

[Tutorial 1: Install AAE Export](#tutorial-1-install-aae-export)  
[Tutorial 2: Track a simple pan using tracking marker](#tutorial-2-track-a-simple-pan-using-tracking-marker)  
[Tutorial 3: Track perspective using plane track](#tutorial-3-track-perspective-using-plane-track)

## Tutorial 1: Install AAE Export

https://user-images.githubusercontent.com/112813970/204144711-09e56711-ce7c-4cc2-a193-29003769062d.mp4

### Summary: Install AAE Export

* At Blender splash screen, select VFX startup file and you will get a workspace that's pretty much ready for motion tracking. The most important editors for motion tracking are „Movie Clip Editor > Tracking > Clip“ editor and „Movie Clip Editor > Tracking > Graph“ editor.  
* Once you've set up your workspace, you can save a copy of your Blender file so you can keep the new workspace next time you open Blender. You can also set it as Blender's default startup file at „File > Defaults > Save Startup File“.  
* At the menu bar, click „Edit > Preference“, and then in the „Add-ons“ section, click the „Install“ button and select `aae-export.py` to install AAE Export.  

## Tutorial 2: Track a simple pan using tracking marker

https://user-images.githubusercontent.com/112813970/204139371-d8649aa1-7c17-497f-b934-10048f8e00fa.mp4

### Summary: Using tracking marker to track clips in Blender

* Motion tracking in Blender is based on tracking markers. You can place markers on the screen by clicking the „Add“ button in „Track > Marker“ on the left panel. You can configure the marker in „Track > Tracking Settings“ on the left panel before placing them on screen, or configure them in „Track > Tracking Settings“ on the right panel after placing.  
* You can move the marker around using the main preview, or use the small window in „Track > Track“ on the right panel to make tiny adjustments.  
* Although it looks like every marker is centred around a single point, that centre point doesn't really matter. What matters instead is the whole pattern area. If you are tracking a pan without scaling or perspective, you can use a small tracking area at around 21 ~ 41. If you are tracking a pan with scale like in this tutorial, you should try to use a larger tracking area at about 81 ~ 121.  
* The search area should be set depending on how fast the tracking target is moving. If the tracking target is moving slowly like in this tutorial, you can set search area to around pattern area plus 50. However, if the tracking target is moving very fast through the scene, you might need to set the search area to as high as pattern area plus 400.  
* Note that the first frame of a video clip in Blender is frame 1. Frame 0 and negative frames show the same picture as frame 1. AAE Export will only export AAE data from frame 1 till the end of the video.  
* Select the marker you want to track, and use the tools in „Track > Track“ on the left panel to track the marker. After tracking, use the „Copy“ button in „Solve > AAE Export > Selected track“ on the left panel to copy AAE data to clipboard. Paste the AAE data in a-mo and apply it to subtitle.  
* AAE Export by default will automatically save a copy of the AAE data next to the video file. If you don't want this behaviour, you can turn it off by deselecting the „Auto export“ option in „Solve > AAE Export > All tracks“.  

## Tutorial 3: Track perspective using plane track

https://raw.githubusercontent.com/Akatmks/Akatmks/main/aae-export/tutorial02.mp4

### Summary: Using plane track to track perspective in Blender

* Plane track is created using 4 or more markers. It takes the position data from markers and use them to calculate perspective. It requires all the markers to be accurate to work.  
* The 4 corners of plane track is used by Aegisub-Perspective-Motion to generate perspective. Align the plane track to the surface you want to put text on, and use the „Copy“ button in „Solve > AAE Export > Selected track“ to copy AAE data to clipboard.  
