## Table of contents

[Tutorial 1: Install AAE Export](#tutorial-1-install-aae-export)  
[Tutorial 2: Basic motion tracking](#tutorial-2-basic-motion-tracking)  
[Tutorial 3: Introducing smoothing feature](#tutorial-3-introducing-smoothing-feature)  
[Tutorial 4: Tracking perspective](#tutorial-4-tracking-perspective)  

## Tutorial 1: Install AAE Export

https://user-images.githubusercontent.com/112813970/204144711-09e56711-ce7c-4cc2-a193-29003769062d.mp4

### Summary: Install AAE Export

* At Blender splash screen, select VFX startup file and you will get a workspace that's pretty much ready for motion tracking. The most important editors for motion tracking are „Movie Clip Editor > Tracking > Clip“ editor and „Movie Clip Editor > Tracking > Graph“ editor.  
* Once you've set up your workspace, you can save a copy of your Blender file so you can keep the new workspace next time you open Blender. You can also set it as Blender's default startup file at „File > Defaults > Save Startup File“.  
* At the menu bar, click „Edit > Preference“, and then in the „Add-ons“ section, click the „Install“ button and select `aae-export.py` to install AAE Export.  

## Tutorial 2: Basic motion tracking

https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/8e7e5059-391c-4016-8508-2185b54370ba

### Summary: Basic motion tracking

* Motion tracking in Blender is based on tracking markers. You can place markers on the screen by clicking the „Add“ button in „Track > Marker“ on the left panel. You can configure the marker in „Track > Tracking Settings“ on the left panel before placing them on screen, or configure them in „Track > Tracking Settings“ on the right panel after placing.  
* You can move the marker around using the main preview, or use the small window in „Track > Track“ on the right panel to make tiny adjustments.  
* Although it looks like every marker is centred around a single point, some argues that the centre point doesn't really matter. What matters instead is the whole pattern area. witchymary discovered that using larger tracking area will significantly increase tracking accuracy.  
* The search area should be set depending on how fast the tracking target is moving. If the tracking target is moving slowly, you can set search area to around pattern area plus 100. However, if the tracking target is moving very fast through the scene, you might need to set the search area up to pattern area plus 400.  
* Note that the first frame of a video clip in Blender is frame 1. Frame 0 and negative frames show the same picture as frame 1. AAE Export will only export AAE data from frame 1 till the end of the video.  
* Select the marker you want to track, and use the tools in „Track > Track“ on the left panel to track the marker. After tracking, use the „Copy“ button in „Solve > AAE Export > Selected track“ on the left panel to copy AAE data to clipboard. Paste the AAE data in a-mo and apply it to subtitle.  
* AAE Export by default will automatically save a copy of the AAE data next to the video file. If you don't want this behaviour, you can turn it off by deselecting the „Auto export“ option in „Solve > AAE Export > All tracks“.  

## Tutorial 3: Introducing smoothing feature

https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/4bdbda67-d10c-43c3-957e-2d592da0f9dd

### Summary: Introducing smoothing feature

* Smoothing uses the track's position, scale, rotation and Power Pin data to fit polynomial regression models, and then uses the fit models to generate smoothed data. With the extrapolate function, you can use the smoothing feature to remove jittering, or to generate data over frames that are not trackable.  
* Among the four data types, position, scale and rotation data works on a-mo, while Power Pin data works on pers-mo.  
* You can use the „Plot“ button to view the smoothing result before applying it in Aegisub. The residual graph (thanks to Noroino Hanako) will be helpful to see if the track gets a good fit.  
* More information about smoothing feature could be found in [aae-export-smoothing-technical-details.md](aae-export-smoothing-technical-details.md).

## Tutorial 4: Tracking perspective

https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/assets/112813970/114ed7e0-7016-4112-8523-0bfe2de26d60

### Summary: Tracking perspective

* pers-mo is essentially perspective.moon running repeatly using the 4 corners of the marker, also known as Power Pin. For perspective.moon, you will need to draw a clip to generate perspective. For pers-mo, you need to draw the marker onto the surface for the text and then track it to generate perspective for each frames.  
* Perspective can be tracked in Blender using both „Perspective“ or „Affine“ motion model.  
* There is a „Power Pin Remap“ function below smoothing feature, with which you can rotate or flip the result sign.  
* Read PhosCity's [Blender Motion Tracking for Fansubbing](https://fansubbers.miraheze.org/wiki/User:PhosCity/Blender_Motion_Tracking_for_Fansubbing) for more details regarding motion tracking in Blender.  
