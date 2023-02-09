## Overview  

**Prepare data**

* For regular track, `position` and `power_pin` is directly copied from the centre and the corners of the marker, after which the `scale` and `rotation` is calculated from `power_pin`.  
* For plane track, only `power_pin` is directly copied from the four corners of the plane track, while `position`, `scale` and `rotation` is calculated from `power_pin`.  
* For 16:9 video, a `position` with x value within 0 to 1.778 (16⁄9) and y value within 0 to 1 is inside the video frame. For other aspect ratios, `position` value is scaled as explained in the [code](https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/blob/1c7aa5fd7f75ea164a2cc554ddd1983eb7fab2be/scripts/aae-export/aae-export.py#L346-L355). The origin of `position` data is set at the top left corner of the video.  
* `power_pin` data follows the same scale as the `position` data but they are relative to the `position` of the frame instead of the origin.  
* `scale` data ranges from 0 to 1, while every 2𝜋 in `rotation` data represents a full circle.  
* `rotation` data is „[unrolled](https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/blob/1c7aa5fd7f75ea164a2cc554ddd1983eb7fab2be/scripts/aae-export/aae-export.py#L717-L724)“ before starting the smoothing process.  

**Smoothing**

* The data is split into 13 individual streams: `position` x, `position` y, `scale` x, `scale` y, `rotation`, `power_pin` 0002 x, `power_pin` 0002 y, `power_pin` 0003 x, `power_pin` 0003 y, `power_pin` 0004 x, `power_pin` 0004 y, `power_pin` 0005 x, `power_pin` 0005 y.  
* Each stream is then fit to a polynomial regression with the specified max degree and linear regression model. [PolynomialFeatures](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html), [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html), [Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html), [HuberRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html).  
