## Overview  

**Prepare data**

* For regular track, `position` and `power_pin` is directly copied from the centre and the corners of the marker, after which the `scale` and `rotation` is calculated from `power_pin`.  
* For plane track, only `power_pin` is directly copied from the four corners of the plane track, while `position`, `scale` and `rotation` is calculated from `power_pin`.  
* `position` values are normally within the bounds of the video frame, but may occasionally be outside. For 16:9 video, `position` values inside the video frame has an x value in the range 0–1.778 (16⁄9) and a y value in the range 0–1. The origin of `position` data is set at the top left corner of the video.  
* `power_pin` data follows the same scale as the `position` data but they are relative to the `position` of the frame instead of the origin.  
* `scale` data ranges from 0 to 1, while every 2𝜋 in `rotation` data represents a full circle.  
* `rotation` data is „[unrolled](https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/blob/1c7aa5fd7f75ea164a2cc554ddd1983eb7fab2be/scripts/aae-export/aae-export.py#L717-L724)“ before starting the smoothing process.  

**Smoothing**

* The data is split into 13 individual streams: `position` x, `position` y, `scale` x, `scale` y, `rotation`, `power_pin` 0002 x, `power_pin` 0002 y, `power_pin` 0003 x, `power_pin` 0003 y, `power_pin` 0004 x, `power_pin` 0004 y, `power_pin` 0005 x, `power_pin` 0005 y.  
* Each stream is then fit to a polynomial regression with the specified max degree and linear regression model. [PolynomialFeatures](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html), [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html), [Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html), [HuberRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html).  

**Plotting**

* An x–y, frame–x, frame–residual of x, frame–y, and frame–residual of y graph will be plotted for `position`, `scale`, `power_pin` 0002, `power_pin` 0003, `power_pin` 0004, and `power_pin` 0005. A frame–rotation and frame–residual of rotation graph will be plotted for `rotation`. If smoothing is not enabled, only x–y, frame–x and frame-y graph will be plotted.  
* Modified Z-score will be calculated for the residual data. if a data has a Z-score higher than 3.0, its frame number will be annotated on the residual graph.  
