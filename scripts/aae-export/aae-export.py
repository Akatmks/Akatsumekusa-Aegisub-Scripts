# aae-export.py
# Copyright (c) Akatsumekusa, arch1t3cht, Martin Herkt and contributors

#  
#            :::         :::     ::::::::::                                
#         :+: :+:     :+: :+:   :+:                                        
#       +:+   +:+   +:+   +:+  +:+                                         
#     +#++:++#++: +#++:++#++: +#++:++#                                     
#    +#+     +#+ +#+     +#+ +#+                                           
#   #+#     #+# #+#     #+# #+#                                            
#  ###     ### ###     ### ##########                                      
#        :::::::::: :::    ::: :::::::::   ::::::::  ::::::::: ::::::::::: 
#       :+:        :+:    :+: :+:    :+: :+:    :+: :+:    :+:    :+:      
#      +:+         +:+  +:+  +:+    +:+ +:+    +:+ +:+    +:+    +:+       
#     +#++:++#     +#++:+   +#++:++#+  +#+    +:+ +#++:++#:     +#+        
#    +#+         +#+  +#+  +#+        +#+    +#+ +#+    +#+    +#+         
#   #+#        #+#    #+# #+#        #+#    #+# #+#    #+#    #+#          
#  ########## ###    ### ###         ########  ###    ###    ###           
#  

# ---------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ---------------------------------------------------------------------
# Title font: Alligator by Simon Bradley
# ---------------------------------------------------------------------

bl_info = {
    "name": "AAE Export",
    "description": "Export tracks and plane tracks to Aegisub-Motion and Aegisub-Perspective-Motion compatible AAE data",
    "author": "Martin Herkt, arch1t3cht, Akatsumekusa",
    "version": (0, 3, 0),
    "support": "COMMUNITY",
    "category": "Video Tools",
    "blender": (3, 1, 0),
    "location": "Clip Editor > Tools > Solve > AAE Export",
    "warning": "",
    "doc_url": "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts",
    "tracker_url": "https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/issues"
}

import bpy
import bpy_extras.io_utils
from datetime import datetime
from pathlib import Path

# ("import name", "PyPI name", "minimum version")
smoothing_modules = (("numpy", "numpy", ""), ("sklearn", "scikit-learn", "0.18"))

is_smoothing_modules_available = False

class AAEExportSettings(bpy.types.PropertyGroup):
    bl_label = "AAEExportSettings"
    bl_idname = "AAEExportSettings"
    
    do_includes_power_pin: bpy.props.BoolProperty(name="Includes Power Pin",
                                           description="Includes Power Pin data in the export for tracks and plane tracks.\nIf Aegisub-Perspective-Motion is having trouble with the Power Pin data, please update Aegisub-Perspective-Motion to the newest version.\nThis option will be removed by late January and Power Pin data will be included by default",
                                           default=True)
    do_smoothing_fake: bpy.props.BoolProperty(name="Enable",
                                              description="Perform smoothing on tracking data.\nThis feature requires additional packages to be installed. Please head to „Edit > Preference > Add-ons > Video Tools: AAE Export“ to install the dependencies",
                                              default=False)
    do_smoothing: bpy.props.BoolProperty(name="Enable",
                                         description="Perform smoothing on tracking data.\nThis uses position data, scale data, rotation data and Power Pin data of individual tracks and plane tracks to fit polynomial regression models, and uses the fit models to generate smoothed data.\n\nPlease note that this smoothing feature is very rudimentary and may cause more problems than it solves. Akatsumekusa recommends trying it only if the tracking is unbearably poor.\n\nAlso, Akatsumekusa is working on a new script that will provide this feature much better than it is right now. Please expect Non Carbonated AAE Export to come out sometime in 2023",
                                         default=False)
    smoothing_do_position: bpy.props.BoolProperty(name="Smooth",
                                                  description="Perform smoothing on position data",
                                                  default=True)
    smoothing_position_degree: bpy.props.IntProperty(name="Max Degree",
                                                     description="The maximal polynomial degree of position data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa sets the default value of this option to 3. Note that high degree settings may cause overfitting",
                                                     default=3,
                                                     min=1,
                                                     soft_max=5)
    smoothing_do_scale: bpy.props.BoolProperty(name="Smooth",
                                               description="Perform smoothing on scale data",
                                               default=True)
    smoothing_scale_degree: bpy.props.IntProperty(name="Max Degree",
                                                  description="The maximal polynomial degree of scale data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa sets the default value of this option to 2. Note that high degree settings may cause overfitting",
                                                  default=2,
                                                  min=1,
                                                  soft_max=4)
    smoothing_do_rotation: bpy.props.BoolProperty(name="Smooth",
                                               description="Perform smoothing on rotation data.\nPlease note that rotation calculation in AAE Export is very basic. Performing smoothing on rotations with high velocity may yield unexpected results",
                                               default=True)
    smoothing_rotation_degree: bpy.props.IntProperty(name="Max Degree",
                                                     description="The maximal polynomial degree of rotation data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa sets the default value of this option to 2. Note that high degree settings may cause overfitting",
                                                     default=2,
                                                     min=1,
                                                     soft_max=4)
    smoothing_do_power_pin: bpy.props.BoolProperty(name="Smooth",
                                                   description="Perform smoothing on Power Pin data",
                                                   default=True)
    smoothing_power_pin_degree: bpy.props.IntProperty(name="Max Degree",
                                                      description="The maximal polynomial degree of Power Pin data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nPlease note that regression model is fit to Power Pin data relative to the position data instead of absolute.\n\nAkatsumekusa sets the default value of this option to 3. Note that high degree settings may cause overfitting",
                                                      default=2,
                                                      min=1,
                                                      soft_max=5)
    smoothing_position_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "The Huber Regressor is an L2-regularised regression model that is robust to outliers"),
                                                                ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model"),
                                                                ("LINEAR", "Least Squares Regressor", "Ordinary least squares regression model")),
                                                         name="Linear Model",
                                                         default="HUBER")
    smoothing_position_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                              description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers",
                                                              default=1.45,
                                                              min=1.00,
                                                              soft_max=2.50,
                                                              step=1,
                                                              precision=2)
    smoothing_position_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                              description="The alpha of a Lasso Regressor controls the regularisation strength",
                                                              default=1.00,
                                                              min=0.00,
                                                              soft_max=100.0,
                                                              step=1,
                                                              precision=2)
    smoothing_do_predictive_smoothing: bpy.props.BoolProperty(name="Predictive Filling",
                                                              description="Generates position data, scale data, rotation data and Power Pin data over the whole length of the clip, even if the track or plane track is only enabled on a section of the clip.\n\nThe four options above, „Smooth Position“, „Smooth Scale“, „Smooth Rotation“ and „Smooth Power Pin“, decides whether to use predicted data to replace the existing data on frames where the track is enabled, while this option decides whether to use predicted data to fill the gaps in the frames where the marker is not enabled.\n\nAkatsumekusa recommends enabling this option only if the subtitle line covers the whole length of the trimmed clip",
                                                              default=False)
    do_also_export: bpy.props.BoolProperty(name="Auto export",
                                           description="Automatically export the selected track to file while copying",
                                           default=True)
    do_do_not_overwrite: bpy.props.BoolProperty(name="Do not overwrite",
                                                description="Generate unique files every time",
                                                default=False)

class AAEExportExportAll(bpy.types.Operator):
    bl_label = "Export"
    bl_description = "Export all tracking markers and plane tracks to AAE files next to the original movie clip"
    bl_idname = "movieclip.aae_export_export_all"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings

        for track in clip.tracking.tracks:
            AAEExportExportAll._export_to_file(clip, track, AAEExportExportAll._generate(clip, track, settings), None, settings.do_do_not_overwrite)

        for plane_track in clip.tracking.plane_tracks:
            AAEExportExportAll._export_to_file(clip, plane_track, AAEExportExportAll._generate(clip, plane_track, settings), None, settings.do_do_not_overwrite)
        
        return {"FINISHED"}

    @staticmethod
    def _generate(clip, track, settings):
        """
        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or bpy.types.MovieTrackingPlaneTrack
        settings : AAEExportSettings or None
            AAEExportSettings.

        Returns
        -------
        aae : str

        """
        if is_smoothing_modules_available:
            ratio, multiplier \
                = AAEExportExportAll._calculate_aspect_ratio( \
                      clip)

            position, scale, semilimited_rotation, power_pin \
                = AAEExportExportAll._prepare_data( \
                      clip, track, ratio)

            if settings.do_smoothing:
                position \
                    = AAEExportExportAll._smoothing( \
                          position, \
                          settings.smoothing_do_position, settings.smoothing_do_predictive_smoothing, \
                          settings.smoothing_position_degree, \
                          settings.smoothing_position_regressor, settings.smoothing_position_epsilon, settings.smoothing_position_lasso_alpha)

                scale \
                    = AAEExportExportAll._smoothing( \
                          scale, \
                          settings.smoothing_do_scale, settings.smoothing_do_predictive_smoothing, \
                          settings.smoothing_scale_degree, \
                          settings.smoothing_position_regressor, settings.smoothing_position_epsilon, settings.smoothing_position_lasso_alpha)

                rotation \
                    = AAEExportExportAll._unlimit_rotation( \
                          semilimited_rotation)
                
                rotation \
                    = AAEExportExportAll._smoothing( \
                          rotation, \
                          settings.smoothing_do_rotation, settings.smoothing_do_predictive_smoothing, \
                          settings.smoothing_rotation_degree, \
                          settings.smoothing_position_regressor, settings.smoothing_position_epsilon, settings.smoothing_position_lasso_alpha)

                limited_rotation \
                    = AAEExportExportAll._limit_rotation( \
                          rotation)

                for i in range(4):
                    power_pin[i] \
                        = AAEExportExportAll._smoothing( \
                              power_pin[i], \
                              settings.smoothing_do_power_pin, settings.smoothing_do_predictive_smoothing, \
                              settings.smoothing_power_pin_degree, \
                              settings.smoothing_position_regressor, settings.smoothing_position_epsilon, settings.smoothing_position_lasso_alpha)

            else:
                limited_rotation \
                    = AAEExportExportAll._limit_rotation( \
                          semilimited_rotation)

            aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005 \
                = AAEExportExportAll._generate_aae( \
                      position, scale, limited_rotation, power_pin, \
                      multiplier)

        else: # not is_smoothing_modules_available
            aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005 \
                = AAEExportExportAll._generate_aae_non_numpy( \
                      clip, track)

        aae \
            = AAEExportExportAll._combine_aae( \
                  clip, \
                  aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, \
                  settings.do_includes_power_pin)

        return aae

    @staticmethod
    def _calculate_aspect_ratio(clip):
        """
        Calculate aspect ratio.

        Parameters
        ----------
        clip : bpy.types.MovieClip

        Returns
        -------
        ratio : npt.NDArray[float64]
        multiplier: float

        """
        import numpy as np

        ar = clip.size[0] / clip.size[1]
        # As of 2021/2022
        if ar < 1 / 1.35: # 9:16, 9:19 and higher videos
            return np.array([1 / 1.35, 1 / 1.35 / ar], dtype=np.float64), clip.size[0] / 1 * 1.35
        elif ar < 1: # vertical videos from 1:1, 3:4, up to 1:1.35
            return np.array([ar, 1], dtype=np.float64), clip.size[1]
        elif ar <= 1.81: # 1:1, 4:3, 16:9, up to 1920 x 1061
            return np.array([ar, 1], dtype=np.float64), clip.size[1]
        else: # Ultrawide
            return np.array([1.81, 1.81 / ar], dtype=np.float64), clip.size[0] / 1.81

    @staticmethod
    def _prepare_data(clip, track, ratio):
        """
        Create position, scale, rotation and Power Pin array from tracking markers. [Step 04]

        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or bpy.types.MovieTrackingPlaneTrack
        ratio : npt.NDArray[float]
            ratio likely from Step 03

        Returns
        -------
        position : npt.NDArray[float64]
        scale : npt.NDArray[float64]
        semilimited_rotation : npt.NDArray[float64]
        power_pin : npt.NDArray[float64]

        """
        if track.__class__.__name__ == "MovieTrackingTrack":
            position, misshapen_power_pin \
                = AAEExportExportAll._prepare_position_and_misshapen_power_pin_marker_track( \
                      clip, track, ratio)
        elif track.__class__.__name__ == "MovieTrackingPlaneTrack":
            position, misshapen_power_pin \
                = AAEExportExportAll._prepare_position_and_misshapen_power_pin_plane_track( \
                      clip, track, ratio)
        else:
            raise ValueError("track.__class__.__name__ \"" + track.__class__.__name__ + "\" not recognised")

        scale, semilimited_rotation \
            = AAEExportExportAll._prepare_scale_and_semilimited_rotation( \
                  misshapen_power_pin)

        power_pin \
            = AAEExportExportAll._prepare_power_pin( \
                  misshapen_power_pin)

        return position, scale, semilimited_rotation, power_pin

    @staticmethod
    def _prepare_position_and_misshapen_power_pin_marker_track(clip, track, ratio):
        """
        Create position and misshapen_power_pin array from marker track.

        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack
        ratio : npt.NDArray[float]

        Returns
        -------
        position : npt.NDArray[float64]
        misshapen_power_pin : npt.NDArray[float64]
            As explained below.

        """
        import numpy as np

        if not clip.frame_duration >= 1:
            raise ValueError("clip.frame_duration must be greater than or equal to 1")

        # position array structure
        # +----------+----------------------------------------------------------+
        # |          |          Frame 0  Frame 1  Frame 2  Frame 3  Frame 4     |
        # +----------+----------------------------------------------------------+
        # | Position | array([  [x, y],  [x, y],  [x, y],  [x, y],  [x, y]   ]) |
        # +----------+----------------------------------------------------------+
        # The origin will be located at the upper left corner of the video,
        # contrary to Blender's usual lower left corner.
        #
        # The x and y value will have a pixel aspect ratio of 1:1. See
        # _calculate_aspect_ratio for the range where x and y value is on
        # screen.
        #
        # The start frame of a video will be frame 0, instead of Blender's
        # usual frame 1.
        # 
        # Also, on the topic of precision, NC AAE Export uses float64 across
        # the whole script instead of Blender's float32.
        position = np.full((clip.frame_duration, 2), np.nan, dtype=np.float64)
        # power_pin array structure
        # +--------------------+------------------------------------------------------------+
        # |                    |           Frame 0  Frame 1  Frame 2  Frame 3  Frame 4      |
        # +--------------------+------------------------------------------------------------+
        # | Upper-Left Corner  | array([[  [x, y],  [x, y],  [x, y],  [x, y],  [x, y]   ],  |
        # |   (Power Pin-0002) |                                                            |
        # | Upper-Right Corner |        [  [x, y],  [x, y],  [x, y],  [x, y],  [x, y]   ],  |
        # |   (Power Pin-0003) |                                                            |
        # | Lower-Left Corner  |        [  [x, y],  [x, y],  [x, y],  [x, y],  [x, y]   ],  |
        # |   (Power Pin-0004) |                                                            |
        # | Lower-Right Corner |        [  [x, y],  [x, y],  [x, y],  [x, y],  [x, y]   ]]) |
        # |   (Power Pin-0005) |                                                            |
        # +--------------------+------------------------------------------------------------+
        # power pin position is not absolute and is relative to the position
        # array
        # 
        # misshapen_power_pin array structure
        # +---------+-----------------------------------------------------------------+
        # |         |           Upper-Left  Upper-Right  Lower-Left  Lower-Right      |
        # +---------+-----------------------------------------------------------------+
        # | Frame 0 | array([[  x, y,       x, y,        x, y        x, y         ],  |
        # | Frame 1 |        [  x, y,       x, y,        x, y        x, y         ],  |
        # | Frame 2 |        [  x, y,       x, y,        x, y        x, y         ],  |
        # | Frame 3 |        [  x, y,       x, y,        x, y        x, y         ],  |
        # | Frame 4 |        [  x, y,       x, y,        x, y        x, y         ]]) |
        # +---------+-----------------------------------------------------------------+
        misshapen_power_pin = np.full((clip.frame_duration, 8), np.nan, dtype=np.float64)

        for marker in track.markers:
            if not 0 < marker.frame <= clip.frame_duration:
                continue
            if marker.mute:
                continue
            position[marker.frame - 1] = [marker.co[0], 1 - marker.co[1]]
            misshapen_power_pin[marker.frame - 1] = [marker.pattern_corners[3][0], -marker.pattern_corners[3][1], \
                                                     marker.pattern_corners[2][0], -marker.pattern_corners[2][1], \
                                                     marker.pattern_corners[0][0], -marker.pattern_corners[0][1], \
                                                     marker.pattern_corners[1][0], -marker.pattern_corners[1][1]]

        position *= ratio
        misshapen_power_pin *= np.tile(ratio, 4)

        return position, misshapen_power_pin

    @staticmethod
    def _prepare_position_and_misshapen_power_pin_plane_track(clip, track, ratio):
        """
        Create position and misshapen_power_pin array from plane track.

        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack
        ratio : npt.NDArray[float]

        Returns
        -------
        position : npt.NDArray[float64]
        misshapen_power_pin : npt.NDArray[float64]
            As explained in _prepare_position_and_power_pin_marker_track().

        """
        import numpy as np

        if not clip.frame_duration >= 1:
            raise ValueError("clip.frame_duration must be greater than or equal to 1")
            
        # As explained in _prepare_position_and_power_pin_marker_track()
        misshapen_power_pin = np.full((clip.frame_duration, 8), np.nan, dtype=np.float64)

        for marker in track.markers[1:-1]:
            if not 0 < marker.frame <= clip.frame_duration:
                continue
            if marker.mute:
                continue
            misshapen_power_pin[marker.frame - 1] = [marker.corners[3][0], 1 - marker.corners[3][1],
                                                     marker.corners[2][0], 1 - marker.corners[2][1],
                                                     marker.corners[0][0], 1 - marker.corners[0][1],
                                                     marker.corners[1][0], 1 - marker.corners[1][1]]
          
        misshapen_power_pin *= np.tile(ratio, 4)

        # https://stackoverflow.com/questions/563198/
        def eat(slice):
            if slice[0] == np.nan:
                return np.full((2), np.nan, dtype=np.float64)
            else:
                p = slice[0:2]
                r = slice[6:8] - slice[0:2]
                q = slice[4:6]
                s = slice[2:4] - slice[4:6]
                t = np.cross((q - p), s) / np.cross(r, s)
                return p + t * r
        position = np.apply_along_axis(eat, 1, misshapen_power_pin)
        misshapen_power_pin -= np.tile(position, 4)

        return position, misshapen_power_pin
        
    @staticmethod
    def _prepare_scale_and_semilimited_rotation(misshapen_power_pin):
        """
        Create scale and rotation array.

        Parameters
        ----------
        misshapen_power_pin : npt.NDArray[float64]

        Returns
        -------
        scale : npt.NDArray[float64]
            scale is a 2D array unmultiplied.
        semilimited_rotation : npt.NDArray[float64]
            rotation is an 1D array unmultiplied as well.

        """
        import numpy as np
        import numpy.linalg as LA
        
        # https://stackoverflow.com/questions/1401712/
        scale_x = LA.norm(misshapen_power_pin[:, 0:2] - misshapen_power_pin[:, 2:4] + misshapen_power_pin[:, 4:6] - misshapen_power_pin[:, 6:8], axis=1)
        scale_y = LA.norm(misshapen_power_pin[:, 0:2] - misshapen_power_pin[:, 4:6] + misshapen_power_pin[:, 2:4] - misshapen_power_pin[:, 6:8], axis=1)
        scale = np.hstack((scale_x.reshape((-1, 1)), scale_y.reshape((-1, 1))))
        try:
            scale /= scale[np.nonzero(~np.isnan(scale_x))[0][0]]
        except IndexError:
            raise ValueError("At least one marker in track.markers needs to be not marker.mute")

        rotation_x = (misshapen_power_pin[:, 0] + misshapen_power_pin[:, 2]) / 2
        rotation_y = (misshapen_power_pin[:, 1] + misshapen_power_pin[:, 3]) / 2
        semilimited_rotation = np.arctan2(rotation_x, -rotation_y)

        return scale, semilimited_rotation

    @staticmethod
    def _prepare_power_pin(misshapen_power_pin):
        """
        Create scale and rotation array.

        Parameters
        ----------
        misshapen_power_pin : npt.NDArray[float64]

        Returns
        -------
        power_pin : npt.NDArray[float64]

        """
        import numpy as np

        return np.swapaxes(misshapen_power_pin.reshape((-1, 4, 2)), 0, 1)

    @staticmethod
    def _smoothing(data, do_smoothing, do_predictive_smoothing, degree, regressor, huber_epsilon, lasso_alpha):
        """
        Perform smoothing depending on the smoothing settings.

        Parameters
        ----------
        data : npt.NDArray[float64]
            position, scale, rotation and each power_pin
        do_smoothing : bool
        do_predictive_smoothing : bool
        degree : int
        regressor : str
        huber_epsilon : int
        lasso_alpha : int

        Returns
        -------
        data : npt.NDArray[float64]

        """
        import numpy as np

        if data.ndim == 2:
            for i in range(data.shape[1]):
                data[:, i] \
                    = AAEExportExportAll._smoothing( \
                          data[:, i], do_smoothing, do_predictive_smoothing, degree, regressor, huber_epsilon, lasso_alpha)
        
        elif data.ndim == 1:
            match (do_smoothing << 1) + do_predictive_smoothing: # match case requires Python 3.10 (Blender 3.1)
                case 0b11:
                    predicted_data = AAEExportExportAll._smoothing_univariate(data, degree, regressor, huber_epsilon, lasso_alpha)
                    return predicted_data
                case 0b10:
                    predicted_data = AAEExportExportAll._smoothing_univariate(data, degree, regressor, huber_epsilon, lasso_alpha)
                    predicted_data[np.isnan(data)] = np.nan
                    return predicted_data
                case 0b01:
                    predicted_data = AAEExportExportAll._smoothing_univariate(data, degree, regressor, huber_epsilon, lasso_alpha)
                    data[np.isnan(data)] = predicted_data[np.isnan(data)]
                    return data
                case 0b00:
                    return data
        else:
            raise ValueError("data.ndim must be either 1 or 2")

    @staticmethod
    def _smoothing_univariate(data, degree, regressor, huber_epsilon, lasso_alpha):
        """
        Perform smoothing depending on the smoothing settings.

        Parameters
        ----------
        data : npt.NDArray[float64]
            univariate data
        degree : int
        regressor : str
        huber_epsilon : int
        lasso_alpha : int

        Returns
        -------
        predicted_data : npt.NDArray[float64]
            data with all frames filled with predicted value

        """
        import numpy as np
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import HuberRegressor, Lasso, LinearRegression
        from sklearn.pipeline import Pipeline

        X = np.arange(data.shape[0])[(index := ~np.isnan(data))].reshape(-1, 1) # := requires Python 3.8 (Blender 2.93)
        y = data[index]

        if regressor == "HUBER":
            return Pipeline([("poly", PolynomialFeatures(degree=degree)), \
                             ("huber", HuberRegressor(epsilon=huber_epsilon))]) \
                       .fit(X, y) \
                       .predict(np.arange(data.shape[0]).reshape(-1, 1))
        elif regressor == "LASSO":
            return Pipeline([("poly", PolynomialFeatures(degree=degree)), \
                             ("lasso", Lasso(alpha=lasso_alpha))]) \
                       .fit(X, y) \
                       .predict(np.arange(data.shape[0]).reshape(-1, 1))
        elif regressor == "LINEAR":
            return Pipeline([("poly", PolynomialFeatures(degree=degree)), \
                             ("regressor", LinearRegression())]) \
                       .fit(X, y) \
                       .predict(np.arange(data.shape[0]).reshape(-1, 1))
        else:
            raise ValueError("regressor " + regressor + " not recognised")

    @staticmethod
    def _unlimit_rotation(semilimited_rotation):
        """
        Unlimit the rotation.

        Parameters
        ----------
        semilimited_rotation : npt.NDArray[float64]

        Returns
        -------
        rotation : npt.NDArray[float64]

        """
        import numpy as np

        diff = np.diff(semilimited_rotation)

        for i in np.nonzero(diff > np.pi)[0]:
            semilimited_rotation[i+1:] -= 2 * np.pi
        for i in np.nonzero(diff <= -np.pi)[0]:
            semilimited_rotation[i+1:] += 2 * np.pi

        return semilimited_rotation

    @staticmethod
    def _limit_rotation(rotation):
        """
        Limit the rotation.

        Parameters
        ----------
        rotation : npt.NDArray[float64]

        Returns
        -------
        limited_rotation : npt.NDArray[float64]

        """
        import numpy as np

        return np.remainder(rotation, 2 * np.pi)

    @staticmethod
    def _generate_aae(position, scale, limited_rotation, power_pin, multiplier):
        """
        Finalised and stringify the data.

        Parameters
        ----------
        position : npt.NDArray[float64]
        scale : npt.NDArray[float64]
        limited_rotation : npt.NDArray[float64]
        power_pin : npt.NDArray[float64]
        multiplier: float

        Returns
        -------
        aae_position : list[str]
        aae_scale : list[str]
        aae_rotation : list[str]
        aae_power_pin_0002 : list[str]
        aae_power_pin_0003 : list[str]
        aae_power_pin_0004 : list[str]
        aae_power_pin_0005 : list[str]

        """
        import numpy as np

        position *= multiplier
        scale *= 100.0
        limited_rotation *= 180.0 / np.pi
        power_pin *= multiplier
        power_pin += position

        aae_position = []
        aae_scale = []
        aae_rotation = []
        aae_power_pin_0002 = []
        aae_power_pin_0003 = []
        aae_power_pin_0004 = []
        aae_power_pin_0005 = []

        for frame in range(position.shape[0]):
            if position[frame][0] != np.nan:
                aae_position.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(frame + 1, *position[frame], 0.0))
            if scale[frame][0] != np.nan:
                aae_scale.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(frame + 1, *scale[frame], 100.0))
            if limited_rotation[frame] != np.nan:
                aae_rotation.append("\t{:d}\t{:.3f}".format(frame + 1, limited_rotation[frame]))
            if power_pin[0][frame][0] != np.nan:
                aae_power_pin_0002.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[0][frame]))
                aae_power_pin_0003.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[1][frame]))
                aae_power_pin_0004.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[2][frame]))
                aae_power_pin_0005.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[3][frame]))

        return aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005
        
    @staticmethod
    def _generate_aae_non_numpy(clip, track):
        """
        Generate aae without numpy.

        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or bpy.types.MovieTrackingPlaneTrack

        Returns
        -------
        aae_position : list[str]
        aae_scale : list[str]
        aae_rotation : list[str]
        aae_power_pin_0002 : list[str]
        aae_power_pin_0003 : list[str]
        aae_power_pin_0004 : list[str]
        aae_power_pin_0005 : list[str]

        """
        aae_position = []
        aae_scale = []
        aae_rotation = []
        aae_power_pin_0002 = []
        aae_power_pin_0003 = []
        aae_power_pin_0004 = []
        aae_power_pin_0005 = []

        scale_base = None

        if track.__class__.__name__ == "MovieTrackingTrack":
            for marker in track.markers:
                if not 0 < marker.frame <= clip.frame_duration:
                    continue
                if marker.mute:
                    continue

                position, scale, rotation, power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005, \
                scale_base \
                    = AAEExportExportAll._calculate_marker_track_per_frame_non_numpy( \
                          clip, marker, scale_base)

                AAEExportExportAll._generate_aae_per_frame_non_numpy( \
                    marker, \
                    aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, \
                    position, scale, rotation, power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005)

        elif track.__class__.__name__ == "MovieTrackingPlaneTrack":
            for marker in track.markers[1:-1]:
                if not 0 < marker.frame <= clip.frame_duration:
                    continue
                if marker.mute:
                    continue

                position, scale, rotation, power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005, \
                scale_base \
                    = AAEExportExportAll._calculate_plane_track_per_frame_non_numpy( \
                          clip, marker, scale_base)

                AAEExportExportAll._generate_aae_per_frame_non_numpy( \
                    marker, \
                    aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, \
                    position, scale, rotation, power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005)

        else:
            raise ValueError("track.__class__.__name__ \"" + track.__class__.__name__ + "\" not recognised")

        return aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005

    @staticmethod
    def _calculate_marker_track_per_frame_non_numpy(clip, marker, scale_base):
        """
        Generate data without numpy.

        Parameters
        ----------
        clip : bpy.types.MovieClip
        marker : bpy.types.MovieTrackingMarker
        scale_base : tuple[float] or None

        Returns
        -------
        position : tuple[float]
        scale : tuple[float]
        rotate : float
        power_pin_0002 : tuple[float]
        power_pin_0003 : tuple[float]
        power_pin_0004 : tuple[float]
        power_pin_0005 : tuple[float]
        scale_base : tuple[float]
        """
        import math

        position = (float(marker.co[0]) * clip.size[0],
                    1 - float(marker.co[1]) * clip.size[1])

        relative_power_pin_0002 = (float(marker.pattern_corners[3][0]) * clip.size[0],
                                   -float(marker.pattern_corners[3][1]) * clip.size[1])
        relative_power_pin_0003 = (float(marker.pattern_corners[2][0]) * clip.size[0],
                                   -float(marker.pattern_corners[2][1]) * clip.size[1])
        relative_power_pin_0004 = (float(marker.pattern_corners[0][0]) * clip.size[0],
                                   -float(marker.pattern_corners[0][1]) * clip.size[1])
        relative_power_pin_0005 = (float(marker.pattern_corners[1][0]) * clip.size[0],
                                   -float(marker.pattern_corners[1][1]) * clip.size[1])

        scale = (math.sqrt(math.pow(relative_power_pin_0002[0] - relative_power_pin_0003[0] + relative_power_pin_0004[0] - relative_power_pin_0005[0], 2) + \
                           math.pow(relative_power_pin_0002[1] - relative_power_pin_0003[1] + relative_power_pin_0004[1] - relative_power_pin_0005[1], 2)),
                 math.sqrt(math.pow(relative_power_pin_0002[0] - relative_power_pin_0004[0] + relative_power_pin_0003[0] - relative_power_pin_0005[0], 2) + \
                           math.pow(relative_power_pin_0002[1] - relative_power_pin_0004[1] + relative_power_pin_0003[1] - relative_power_pin_0005[1], 2)))
        if scale_base == None:
            scale_base = scale
            scale = (100.0, 100.0)
        else:
            scale = (scale[0] / scale_base[0] * 100, scale[1] / scale_base[1] * 100)

        rotation = math.atan2((relative_power_pin_0002[0] + relative_power_pin_0003[0]) / 2,
                              -(relative_power_pin_0002[1] + relative_power_pin_0003[1]) / 2) % (2 * math.pi) * 180 / math.pi

        power_pin_0002 = (relative_power_pin_0002[0] + position[0], relative_power_pin_0002[1] + position[1])
        power_pin_0003 = (relative_power_pin_0003[0] + position[0], relative_power_pin_0003[1] + position[1])
        power_pin_0004 = (relative_power_pin_0004[0] + position[0], relative_power_pin_0004[1] + position[1])
        power_pin_0005 = (relative_power_pin_0005[0] + position[0], relative_power_pin_0005[1] + position[1])

        return position, scale, rotation, power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005, scale_base

    @staticmethod
    def _calculate_plane_track_per_frame_non_numpy(clip, marker, scale_base):
        """
        Generate data without numpy.

        Parameters
        ----------
        clip : bpy.types.MovieClip
        marker : bpy.types.MovieTrackingPlaneMarker
        scale_base : tuple[float] or None

        Returns
        -------
        position : tuple[float]
        scale : tuple[float]
        rotate : float
        power_pin_0002 : tuple[float]
        power_pin_0003 : tuple[float]
        power_pin_0004 : tuple[float]
        power_pin_0005 : tuple[float]
        scale_base : tuple[float]
        """
        import math

        power_pin_0002 = (float(marker.corners[3][0]) * clip.size[0],
                          (1 - float(marker.corners[3][1])) * clip.size[1])
        power_pin_0003 = (float(marker.corners[2][0]) * clip.size[0],
                          (1 - float(marker.corners[2][1])) * clip.size[1])
        power_pin_0004 = (float(marker.corners[0][0]) * clip.size[0],
                          (1 - float(marker.corners[0][1])) * clip.size[1])
        power_pin_0005 = (float(marker.corners[1][0]) * clip.size[0],
                          (1 - float(marker.corners[1][1])) * clip.size[1])
                          
        position \
            = AAEExportExportAll._calculate_centre_plane_track_per_frame_non_numpy( \
                  power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005)
    
        scale = (math.sqrt(math.pow(power_pin_0002[0] - power_pin_0003[0] + power_pin_0004[0] - power_pin_0005[0], 2) + \
                           math.pow(power_pin_0002[1] - power_pin_0003[1] + power_pin_0004[1] - power_pin_0005[1], 2)),
                 math.sqrt(math.pow(power_pin_0002[0] - power_pin_0004[0] + power_pin_0003[0] - power_pin_0005[0], 2) + \
                           math.pow(power_pin_0002[1] - power_pin_0004[1] + power_pin_0003[1] - power_pin_0005[1], 2)))
        if scale_base == None:
            scale_base = scale
            scale = (100.0, 100.0)
        else:
            scale = (scale[0] / scale_base[0] * 100, scale[1] / scale_base[1] * 100) % (2 * math.pi) * 180 / math.pi

        rotation = math.atan2((power_pin_0002[0] + power_pin_0003[0]) / 2 - position[0],
                              -((power_pin_0002[1] + power_pin_0003[1]) / 2 - position[1]))

        return position, scale, rotation, power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005, scale_base

    @staticmethod
    def _calculate_centre_plane_track_per_frame_non_numpy(power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005):
        """
        Parameters
        ----------
        power_pin_0002 : tuple[float]
        power_pin_0003 : tuple[float]
        power_pin_0004 : tuple[float]
        power_pin_0005 : tuple[float]

        Returns
        -------
        i : tuple[float]
            The centre of plane track. Never None.

        """
        # https://stackoverflow.com/questions/563198
        px = power_pin_0002[0]
        py = power_pin_0002[1]
        rx = power_pin_0002[0] - power_pin_0005[0]
        ry = power_pin_0002[1] - power_pin_0005[1]
        qx = power_pin_0004[0]
        qy = power_pin_0004[1]
        sx = power_pin_0004[0] - power_pin_0003[0]
        sy = power_pin_0004[1] - power_pin_0003[1]

        j = rx * sy - ry * sx
        k = (qx - px) * ry - (qy - py) * rx

        if j == 0 and k == 0:
            # The points are collinear
            return [(px * 2 + rx + qx * 2 + sx) / 4, (py * 2 + ry + qy * 2 + sy) / 4]
        elif j == 0 and k != 0:
            # The two lines are parallel
            # It could return AAEExportExportAll._plane_track_center(l, n, m, o)
            # but that will give a false sense of security as if this
            # function can deal with hourglass-shaped input.
            return [(px * 2 + rx + qx * 2 + sx) / 4, (py * 2 + ry + qy * 2 + sy) / 4]
        else: # j != 0
            # The two lines intersects
            t = k / j
            return [px + t * rx, py + t * ry]

    @staticmethod
    def _generate_aae_per_frame_non_numpy(marker, aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, position, scale, rotation, power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005):
        """
        Generate aae per frame without numpy.

        Parameters
        ----------
        marker : bpy.types.MovieTrackingMarker or bpy.types.MovieTrackingPlaneMarker
        aae_position : list[str]
        aae_scale : list[str]
        aae_rotation : list[str]
        aae_power_pin_0002 : list[str]
        aae_power_pin_0003 : list[str]
        aae_power_pin_0004 : list[str]
        aae_power_pin_0005 : list[str]
        position : tuple[float]
        scale : tuple[float]
        rotate : float
        power_pin_0002 : tuple[float]
        power_pin_0003 : tuple[float]
        power_pin_0004 : tuple[float]
        power_pin_0005 : tuple[float]

        """
        aae_position.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(marker.frame, *position, 0.0))
        aae_scale.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(marker.frame, *scale, 100.0))
        aae_rotation.append("\t{:d}\t{:.3f}".format(marker.frame, rotation))
        aae_power_pin_0002.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0002))
        aae_power_pin_0003.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0003))
        aae_power_pin_0004.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0004))
        aae_power_pin_0005.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0005))

    @staticmethod
    def _combine_aae(clip, aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, do_includes_power_pin):
        """
        Combine and finish aae.

        Parameters
        ----------
        clip : clip : bpy.types.MovieClip
        aae_position : list[str]
        aae_scale : list[str]
        aae_rotation : list[str]
        aae_power_pin_0002 : list[str]
        aae_power_pin_0003 : list[str]
        aae_power_pin_0004 : list[str]
        aae_power_pin_0005 : list[str]

        Returns
        -------
        aae : str

        """
        aae = ""

        aae += "Adobe After Effects 6.0 Keyframe Data\n\n"
        aae += "\tUnits Per Second\t{:.3f}\n".format(clip.fps)
        aae += "\tSource Width\t{:d}\n".format(clip.size[0])
        aae += "\tSource Height\t{:d}\n".format(clip.size[1])
        aae += "\tSource Pixel Aspect Ratio\t{:d}\n".format(1)
        aae += "\tComp Pixel Aspect Ratio\t{:d}\n\n".format(1)

        aae += "Anchor Point\n"
        aae += "\tFrame\tX pixels\tY pixels\tZ pixels\n"
        aae += "\n".join(aae_position) + "\n\n"

        aae += "Position\n"
        aae += "\tFrame\tX pixels\tY pixels\tZ pixels\n"
        aae += "\n".join(aae_position) + "\n\n"

        aae += "Scale\n"
        aae += "\tFrame\tX percent\tY percent\tZ percent\n"
        aae += "\n".join(aae_scale) + "\n\n"

        aae += "Rotation\n"
        aae += "\tFrame\tDegrees\n"
        aae += "\n".join(aae_rotation) + "\n\n"

        if do_includes_power_pin:
            aae += "Effects	CC Power Pin #1	CC Power Pin-0002\n"
            aae += "\tFrame\tX pixels\tY pixels\n"
            aae += "\n".join(aae_power_pin_0002) + "\n\n"
            aae += "Effects	CC Power Pin #1	CC Power Pin-0003\n"
            aae += "\tFrame\tX pixels\tY pixels\n"
            aae += "\n".join(aae_power_pin_0003) + "\n\n"
            aae += "Effects	CC Power Pin #1	CC Power Pin-0004\n"
            aae += "\tFrame\tX pixels\tY pixels\n"
            aae += "\n".join(aae_power_pin_0004) + "\n\n"
            aae += "Effects	CC Power Pin #1	CC Power Pin-0005\n"
            aae += "\tFrame\tX pixels\tY pixels\n"
            aae += "\n".join(aae_power_pin_0005) + "\n\n"

        aae += "End of Keyframe Data\n"

        return aae

    @staticmethod
    def _export_to_file(clip, track, aae, prefix, do_do_not_overwrite):
        """
        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or MovieTrackingPlaneTrack
        aae : str
            Likely coming from _generated().
        prefix : None or str
        do_do_not_overwrite : bool
            AAEExportSettings.do_do_not_overwrite.

        """
        coords = None
        if track.markers[0].__class__.__name__ == "MovieTrackingMarker":
            for marker in track.markers:
                if not marker.mute:
                    coords = (marker.co[0] * clip.size[0], (1 - marker.co[1]) * clip.size[1])
                    break
        else: # "MovieTrackingPlaneMarker"
            for marker in track.markers:
                if not marker.mute:
                    coords = AAEExportExportAll._plane_track_center(marker.corners[0], marker.corners[1], marker.corners[2], marker.corners[3])
                    coords = (coords[0] * clip.size[0], (1 - coords[1]) * clip.size[1])
                    break

        if coords != None:
            p = Path(bpy.path.abspath(clip.filepath if not prefix else prefix))
            # with_stem() requires Python 3.9 (Blender 2.93)
            p = p.with_stem(p.stem + \
                            "[" + ("Track" if track.markers[0].__class__.__name__ == "MovieTrackingMarker" else "Plane Track") + "]" + \
                            f"[({coords[0]:.0f}, {coords[1]:.0f})]" + \
                            (datetime.now().strftime("[%H%M%S %b %d]") if do_do_not_overwrite else "")) \
                 .with_suffix(".txt")
            with p.open(mode="w", encoding="utf-8", newline="\r\n") as f:
                f.write(aae)

    @staticmethod
    def _copy_to_clipboard(context, aae):
        """
        Parameters
        ----------
        context : bpy.context
        aae : str
            Likely coming from _generated().
            
        """
        context.window_manager.clipboard = aae

class AAEExportCopySingleTrack(bpy.types.Operator):
    bl_label = "Copy"
    bl_description = "Copy selected marker as AAE data to clipboard"
    bl_idname = "movieclip.aae_export_copy_single_track"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings

        aae = AAEExportExportAll._generate(clip, context.selected_movieclip_tracks[0], settings)
        
        AAEExportExportAll._copy_to_clipboard(context, aae)
        if settings.do_also_export:
            AAEExportExportAll._export_to_file(clip, context.selected_movieclip_tracks[0], aae, None, settings.do_do_not_overwrite)
        
        return {"FINISHED"}

class AAEExportCopyPlaneTrack(bpy.types.Operator):
    bl_label = "Copy"
    bl_description = "Copy selected plane track as AAE data to clipboard"
    bl_idname = "movieclip.aae_export_copy_plane_track"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings

        aae = None
        for plane_track in context.edit_movieclip.tracking.plane_tracks:
            if plane_track.select == True:
                aae = AAEExportExportAll._generate(clip, plane_track, settings)
                break

        AAEExportExportAll._copy_to_clipboard(context, aae)
        if settings.do_also_export:
            AAEExportExportAll._export_to_file(clip, clip.tracking.plane_tracks[0], aae, None, settings.do_do_not_overwrite)
        
        return {"FINISHED"}
    
class AAEExport(bpy.types.Panel):
    bl_label = "AAE Export"
    bl_idname = "SOLVE_PT_aae_export"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"
    bl_order = 1000000

    def draw(self, context):
        pass

    @classmethod
    def poll(cls, context):
        return context.edit_movieclip is not None

class AAEExportSelectedTrack(bpy.types.Panel):
    bl_label = "Selected track"
    bl_idname = "SOLVE_PT_aae_export_selected"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"
    bl_parent_id = "SOLVE_PT_aae_export"
    bl_order = 10

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        settings = context.screen.AAEExportSettings
        
        column = layout.column()
        column.label(text="Selected track")

        row = layout.row()
        row.scale_y = 2
        row.enabled = len(context.selected_movieclip_tracks) == 1
        row.operator("movieclip.aae_export_copy_single_track")
        
        column = layout.column()
        column.label(text="Selected plane track")
        
        selected_plane_tracks = 0
        for plane_track in context.edit_movieclip.tracking.plane_tracks:
            if plane_track.select == True:
                selected_plane_tracks += 1

        row = layout.row()
        row.scale_y = 2
        row.enabled = selected_plane_tracks == 1
        row.operator("movieclip.aae_export_copy_plane_track")

    @classmethod
    def poll(cls, context):
        return context.edit_movieclip is not None

class AAEExportAllTracks(bpy.types.Panel):
    bl_label = "All tracks"
    bl_idname = "SOLVE_PT_aae_export_all"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"
    bl_parent_id = "SOLVE_PT_aae_export"
    bl_order = 100

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        settings = context.screen.AAEExportSettings
        
        column = layout.column()
        column.label(text="All tracks")
        
        row = layout.row()
        row.scale_y = 2
        row.enabled = len(context.edit_movieclip.tracking.tracks) >= 1 or \
                      len(context.edit_movieclip.tracking.plane_tracks) >= 1
        row.operator("movieclip.aae_export_export_all")

class AAEExportOptions(bpy.types.Panel):
    bl_label = "Export Options"
    bl_idname = "SOLVE_PT_aae_export_options"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"
    bl_parent_id = "SOLVE_PT_aae_export"
    bl_order = 1000

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        settings = context.screen.AAEExportSettings
        
        # layout.separator(factor=0.0)
        box = layout.box()
        column = box.column(heading="Export")
        column.prop(settings, "do_includes_power_pin")
        # layout.separator(factor=0.6)
        box = layout.box()
        column = box.column(heading="Preference")
        column.prop(settings, "do_also_export")
        column.prop(settings, "do_do_not_overwrite")
        # layout.separator(factor=0.6)
        box = layout.box()
        if is_smoothing_modules_available:
            column = box.column(heading="Smoothing")
            column.prop(settings, "do_smoothing")
            column.separator(factor=0.0)
            sub_column = column.column(heading="Position")
            sub_column.enabled = settings.do_smoothing
            sub_column.prop(settings, "smoothing_do_position")
            sub_column.prop(settings, "smoothing_position_degree")
            sub_column = column.column(heading="Scale")
            sub_column.enabled = settings.do_smoothing
            sub_column.prop(settings, "smoothing_do_scale")
            sub_column.prop(settings, "smoothing_scale_degree")
            sub_column = column.column(heading="Rotation")
            sub_column.enabled = settings.do_smoothing
            sub_column.prop(settings, "smoothing_do_rotation")
            sub_column.prop(settings, "smoothing_rotation_degree")
            sub_column = column.column(heading="Power Pin")
            sub_column.enabled = settings.do_smoothing
            sub_column.prop(settings, "smoothing_do_power_pin")
            sub_column.prop(settings, "smoothing_power_pin_degree")
            sub_column = column.column()
            sub_column.enabled = settings.do_smoothing
            sub_column.prop(settings, "smoothing_position_regressor")
            if settings.smoothing_position_regressor == "HUBER":
                sub_column.prop(settings, "smoothing_position_huber_epsilon")
            elif settings.smoothing_position_regressor == "LASSO":
                sub_column.prop(settings, "smoothing_position_lasso_alpha")
            sub_column = column.column()
            sub_column.enabled = settings.do_smoothing
            sub_column.prop(settings, "smoothing_do_predictive_smoothing")
        else:
            column = box.column(heading="Smoothing")
            column.enabled = False
            column.prop(settings, "do_smoothing_fake")
        # layout.separator(factor=0.0)

    @classmethod
    def poll(cls, context):
        return context.edit_movieclip is not None

class AAEExportLegacy(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export motion tracking markers to Adobe After Effects 6.0 compatible files"""
    bl_label = "Export to Adobe After Effects 6.0 Keyframe Data"
    bl_idname = "export.aae_export_legacy"
    filename_ext = ""
    filter_glob = bpy.props.StringProperty(default="*", options={"HIDDEN"})

    def execute(self, context):
        if len(bpy.data.movieclips) == 0:
            raise ValueError("Have you opened any movie clips?")
        # This is broken but I don't want to fix...
        if len(bpy.data.movieclips) >= 2:
            raise ValueError("The legacy export method only allows one clip to be loaded into Blender at a time. You can either try the new export interface at „Clip Editor > Tools > Solve > AAE Export“ or use „File > New“ to create a new Blender file.")
        clip = bpy.data.movieclips[0]
        settings = context.screen.AAEExportSettings

        for track in clip.tracking.tracks:
            AAEExportExportAll._export_to_file(clip, track, AAEExportExportAll._generate(clip, track, None), self.filepath, True)

        for plane_track in clip.tracking.plane_tracks:
            AAEExportExportAll._export_to_file(clip, track, AAEExportExportAll._generate(clip, plane_track, None), self.filepath, True)

        return {"FINISHED"}

classes = (AAEExportSettings,
           AAEExportExportAll,
           AAEExportCopySingleTrack,
           AAEExportCopyPlaneTrack,
           AAEExport,
           AAEExportSelectedTrack,
           AAEExportAllTracks,
           AAEExportOptions,
           AAEExportLegacy)

class AAEExportRegisterSettings(bpy.types.PropertyGroup):
    bl_label = "AAEExportRegisterSettings"
    bl_idname = "AAEExportRegisterSettings"

class AAEExportRegisterInstallSmoothingDependencies(bpy.types.Operator):
    bl_label = "Install Optional Packages"
    bl_description = "AAE Export's smoothing feature requires additional packages to be installed.\nBy clicking this button, AAE Export will download and install " + \
                     (" and ".join([", ".join(["pip"] + [module[1] for module in smoothing_modules[:-1]]), smoothing_modules[-1][1]]) if len(smoothing_modules) != 0 else "pip") + \
                     " into your Blender distribution.\nThis process might take up to 3 minutes. Your Blender will freeze during the process"
    bl_idname = "preference.aae_export_register_install_smoothing_dependencies"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        import importlib.util
        import os
        import subprocess
        import sys

        if os.name == "nt":
            self._execute_nt(context)
        else:
            subprocess.run([sys.executable, "-m", "ensurepip"], check=True) # sys.executable requires Blender 2.93
            subprocess.run([sys.executable, "-m", "pip", "install"] + [module[1] + ">=" + module[2] if module[2] != "" else module[1] for module in smoothing_modules], check=True)
            
        for module in smoothing_modules:
            if importlib.util.find_spec(module[0]) == None:
                return {'FINISHED'}

        global is_smoothing_modules_available
        is_smoothing_modules_available = True

        unregister_register_class()
        
        self.report({"INFO"}, "Dependencies installed successfully.")

        return {'FINISHED'}

    def _execute_nt(self, context):
        # Python, in a Python, in a PowerShell, in a Python
        import importlib.util
        import os
        from pathlib import PurePath
        import subprocess
        import sys
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".py", delete=False) as f:
            f.write("import os, subprocess, sys, traceback\n")
            f.write("if __name__ == \"__main__\":\n")
            f.write("\ttry:\n")

            f.write("\t\tsubprocess.run([\"" + PurePath(sys.executable).as_posix() + "\", \"-m\", \"ensurepip\"], check=True)\n")
            f.write("\t\tsubprocess.run([\"" + PurePath(sys.executable).as_posix() + "\", \"-m\", \"pip\", \"install\", \"" + \
                                        "\", \"".join([module[1] + ">=" + module[2] if module[2] != "" else module[1] for module in smoothing_modules]) + \
                                        "\"], check=True)\n")

            f.write("\texcept:\n")
            f.write("\t\ttraceback.print_exc()\n")
            f.write("\t\tos.system(\"pause\")\n")

        print("aae-export: " + "PowerShell -Command \"& {Start-Process \\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\" -Verb runAs -Wait}\"")
        os.system("PowerShell -Command \"& {Start-Process \\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\" -Verb runAs -Wait}\"")

class AAEExportRegisterPreferencePanel(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    def draw(self, context):
        layout = self.layout
        settings = context.window_manager.AAEExportRegisterSettings

        layout.operator("preference.aae_export_register_install_smoothing_dependencies", icon="CONSOLE")

register_classes = (AAEExportRegisterSettings,
                    AAEExportRegisterInstallSmoothingDependencies,
                    AAEExportRegisterPreferencePanel)
def register():
    import importlib.util
    if importlib.util.find_spec("packaging") != None:
        import packaging.version
    elif importlib.util.find_spec("distutils") != None: # distutils deprecated in Python 3.12
        import distutils.version
    
    global is_smoothing_modules_available
    for module in smoothing_modules:
        if importlib.util.find_spec(module[0]) == None:
            register_register_classes()

            is_smoothing_modules_available = False
            break

        if module[2]:
            exec("import " + module[0])
            module_version = eval(module[0] + ".__version__")
            if "packaging" in locals():
                if packaging.version.parse(module_version) < packaging.version.parse(module[2]):
                    register_register_classes()

                    is_smoothing_modules_available = False
                    break
            elif "distutils" in locals(): # distutils deprecated in Python 3.12
                if distutils.version.LooseVersion(module_version) < distutils.version.LooseVersion(module[2]):
                    register_register_classes()

                    is_smoothing_modules_available = False
                    break
    else:
        is_smoothing_modules_available = True

    register_main_classes()

def register_export_legacy(self, context):
    self.layout.operator(AAEExportLegacy.bl_idname, text="Adobe After Effects 6.0 Keyframe Data")

def register_main_classes():
    for class_ in classes:
        bpy.utils.register_class(class_)
        
    bpy.types.Screen.AAEExportSettings = bpy.props.PointerProperty(type=AAEExportSettings)
        
    bpy.types.TOPBAR_MT_file_export.append(register_export_legacy)

def register_register_classes():
    for class_ in register_classes:
        bpy.utils.register_class(class_)

    bpy.types.WindowManager.AAEExportRegisterSettings = bpy.props.PointerProperty(type=AAEExportRegisterSettings)
    
def unregister():
    if not is_smoothing_modules_available:
        unregister_register_class()
    
    unregister_main_class()

def unregister_main_class():
    bpy.types.TOPBAR_MT_file_export.remove(register_export_legacy)
    
    del bpy.types.Screen.AAEExportSettings
    
    for class_ in classes:
        bpy.utils.unregister_class(class_)

def unregister_register_class():
    del bpy.types.WindowManager.AAEExportRegisterSettings

    for class_ in register_classes:
        bpy.utils.unregister_class(class_)

if __name__ == "__main__":
    register()
#    unregister() 
