## Overview  

**Prepare data**

* For regular track, `position` and `power_pin` is directly copied from the centre and the corners of the marker, after which the `scale` and `rotation` is calculated from `power_pin`.  
* For plane track, only `power_pin` is directly copied from the four corners of the plane track, while `position`, `scale` and `rotation` is calculated from `power_pin`.  
* `position` values are normally within the bounds of the video frame, but may occasionally be outside. For 16:9 video, `position` values inside the video frame has an x value in the range 0–1.778 (16⁄9) and a y value in the range 0–1. Ranges for videos with other aspect ratio can be found [here](https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/blob/1c7aa5fd7f75ea164a2cc554ddd1983eb7fab2be/scripts/aae-export/aae-export.py#L346-L355). The origin of `position` data is set at the top left corner of the video.  
* `power_pin` data follows the same scale as the `position` data but they are relative to the `position` of the frame instead of the origin.  
* `scale` data ranges from 0 to 1, while every 2𝜋 in `rotation` data represents a full circle.  
* `rotation` data is „[unrolled](https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/blob/1c7aa5fd7f75ea164a2cc554ddd1983eb7fab2be/scripts/aae-export/aae-export.py#L717-L724)“ before starting the smoothing process.  

**Section Smoothing**

* The data is split into 13 individual streams: `position` x, `position` y, `scale` x, `scale` y, `rotation`, `power_pin` 0002 x, `power_pin` 0002 y, `power_pin` 0003 x, `power_pin` 0003 y, `power_pin` 0004 x, `power_pin` 0004 y, `power_pin` 0005 x, `power_pin` 0005 y.  
* Within each sections, every stream is fit to a polynomial regression with the specified max degree and linear regression model. Documents for specific models are available at [PolynomialFeatures](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html), [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html), [Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html), [HuberRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html).  

**Plotting Section**

* An x–y, frame–x, frame–residual of x, frame–y, and frame–residual of y graph will be plotted for `position`, `scale`, `power_pin` 0002, `power_pin` 0003, `power_pin` 0004, and `power_pin` 0005 for the section, and a frame–rotation and frame–residual of rotation graph will be plotted for `rotation` for the section. If smoothing is not enabled, only x–y, frame–x and frame-y graph will be plotted.  
* [Modified Z-score](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm#Z-Scores) will be calculated for the residual data. if a data has a modified Z-score higher than 3.0, its frame number will be annotated on the residual graph.  

**Section Blending**

* Nearby sections share the frame at the boundary. If a section enables smoothing, it changes the output data at the boundary frame and it won't match up with the other section sharing the boundary frame. Section blending smoothes this transition from one section to the next. Only the difference between the data at the boundary frame, not derivative, affects the section blending.   

**Plotting Result**

* An x–y, frame–x, and frame–y graph will be plotted for the resulting `position`, `scale`, `power_pin` 0002, `power_pin` 0003, `power_pin` 0004, and `power_pin` 0005 data. A frame–rotation graph will be plotted for the resulting `rotation` data. If section blending is active, the data before section blending will also be plotted.  
