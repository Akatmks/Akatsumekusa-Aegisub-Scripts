# aae-export.py
# Copyright (c) Akatsumekusa, arch1t3cht, bucket3432, Martin Herkt and
# contributors

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
    "author": "Akatsumekusa, arch1t3cht, bucket3432, Martin Herkt and contributors",
    "version": (1, 2, 1),
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

# ("import name", "PyPI name", "minimum version")
smoothing_modules = (("numpy", "numpy", ""),
                     ("sklearn", "scikit-learn", "0.18"),
                     ("matplotlib", "matplotlib", ""),
                     ("PIL", "Pillow", ""))

is_smoothing_modules_available = False

def get_smoothing_modules_install_description():
    from pathlib import PurePath
    import sys

    pre_modules = "This will download and install "
    modules = " and ".join([", ".join(["pip"] + [module[1] for module in smoothing_modules[:-1]]), smoothing_modules[-1][1]]) if 17 != 0 else "pip"
    post_modules_pre_path = " to Blender's python environment at „"
    path = PurePath(sys.prefix).as_posix()
    post_path = "“. This process normally takes about 2 minutes"

    if 11 + 7 + 21 + 4 + 9 < 240:
        return pre_modules + modules + post_modules_pre_path + path + post_path
    else:
        available_len = 240 - 11 - 7 - 21 - 9
        path_last_two_parts = "/" + (parts := PurePath(path).parts)[-2] + "/" + parts[-1]
        return pre_modules + modules + post_modules_pre_path + path[:available_len - 19 - 3] + "..." + path_last_two_parts + post_path

class AAEExportSettings(bpy.types.PropertyGroup):
    bl_label = "AAEExportSettings"
    bl_idname = "AAEExportSettings"
    
    do_includes_power_pin: bpy.props.BoolProperty(name="Includes Power Pin",
                                                  description="Includes Power Pin data in the export for tracks and plane tracks.\nIf Aegisub-Perspective-Motion is unable to recognise the data, please update Aegisub-Perspective-Motion to the newest version.\nThis option will be removed by late January and Power Pin data will be included by default",
                                                  default=True)

    do_do_not_overwrite: bpy.props.BoolProperty(name="Do not overwrite",
                                                description="Generate unique filename every time",
                                                default=False)
    do_also_export: bpy.props.BoolProperty(name="Auto export",
                                           description="Automatically export AAE data to file when copying",
                                           default=True)

    do_advanced_smoothing: bpy.props.BoolProperty(name="Advanced",
                                                  description="Reveal more options for smoothing, including using different smoothing settings for different section of the clip and for different data and axis",
                                                  default=False)

    def _null_property_update(self, context):
        if self.null_property != "":
            self.null_property = ""
    null_property: bpy.props.StringProperty(name="",
                                            description="An empty field; Nothing to see here",
                                            default="",
                                            update=_null_property_update)

class AAEExportSettingsClip(bpy.types.PropertyGroup):
    bl_label = "AAEExportSettingsClip"
    bl_idname = "AAEExportSettingsClip"

    def _do_smoothing_update(self, context):
        # Create the first section if there aren't
        if context.edit_movieclip.AAEExportSettingsSectionLL == 0:
            self.smoothing_blending_cubic_p1 = 0.10
            self.smoothing_blending_cubic_p2 = 0.90
            self.smoothing_blending_cubic_range = 3.0

            item = context.edit_movieclip.AAEExportSettingsSectionL.add()
            context.edit_movieclip.AAEExportSettingsSectionLL = 1
            context.edit_movieclip.AAEExportSettingsSectionLI = 0

            item.frame_update_suppress = False
            item.start_frame = 1
            item.end_frame = 1

    do_smoothing_fake: bpy.props.BoolProperty(name="Enable",
                                              description="Perform smoothing on tracking data.\nThis feature requires additional packages to be installed. Please head to „Edit > Preference > Add-ons > Video Tools: AAE Export > Preferences“ to install the dependencies",
                                              default=False)
    do_smoothing: bpy.props.BoolProperty(name="Enable",
                                         description="Perform smoothing on tracking data.\nThis uses the track's position, scale, rotation and Power Pin data to fit polynomial regression models, and then uses the fit models to generate smoothed data",
                                         default=False,
                                         update=_do_smoothing_update)

    def _do_predictive_smoothing_update(self, context):
        context.edit_movieclip.AAEExportSettingsSectionL[0].smoothing_extrapolate = self.do_predictive_smoothing
    do_predictive_smoothing: bpy.props.BoolProperty(name="Extrapolate",
                                                    description="Generate position, scale, rotation and Power Pin data over the whole length of the clip, even if the track is disabled on some of the frames.\n\nThe four options above, „Smooth Position“, „Smooth Scale“, „Smooth Rotation“ and „Smooth Power Pin“, decides whether to use predicted data to replace the existing data on frames where the track is enabled, while this option decides whether to use predicted data to fill the gaps in frames where the track is not enabled",
                                                    default=False,
                                                    update=_do_predictive_smoothing_update)
                                         
    smoothing_blending: bpy.props.EnumProperty(items=(("NONE", "No Blending", "Average the frame on the section boundaries and do not perform any blending for the other frames"),
                                                      ("CUBIC", "Cubic", "Use a cubic curve to ease the transition between the sections"),
                                                      ("SHIFT", "Shift", "Shift sections until they match up at the boundaries.\nThe amount each section is shifted is proportional to the number of frames in each section")),
                                               name="Section Blending",
                                               default="CUBIC")
    smoothing_blending_cubic_p1: bpy.props.FloatProperty(name="p₁",
                                                          description="The cubic curve is given as (1-t)³ × 0 + (1-t)² × t × p₁ + (1-t) × t² × p₂ + t³ × 1. p₁ is the the second control point on the cubic curve",
                                                          default=0.00,
                                                          min=0.0,
                                                          max=1.0,
                                                          step=1,
                                                          precision=2)
    smoothing_blending_cubic_p2: bpy.props.FloatProperty(name="p₂",
                                                          description="The cubic curve is given as (1-t)³ × 0 + (1-t)² × t × p₁ + (1-t) × t² × p₂ + t³ × 1. p₂ is the the third control point on the cubic curve",
                                                          default=0.00,
                                                          min=0.0,
                                                          max=1.0,
                                                          step=1,
                                                          precision=2)
    smoothing_blending_cubic_range: bpy.props.FloatProperty(name="Range",
                                                             description="Number of frames prior to and following the section boundaries where the blending is applied",
                                                             default=0.0,
                                                             min=1.0,
                                                             soft_max=24.0,
                                                             step=50,
                                                             precision=1)

    power_pin_remap_0002: bpy.props.EnumProperty(items=(("0002", "0002 (Upper-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-left corner of the track"),
                                                        ("0003", "0003 (Upper-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-left corner of the track"),
                                                        ("0004", "0004 (Lower-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-left corner of the track"),
                                                        ("0005", "0005 (Lower-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-left corner of the track")),
                                               name="0002 (Upper-left)",
                                               default="0002")
    power_pin_remap_0003: bpy.props.EnumProperty(items=(("0002", "0002 (Upper-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-right corner of the track"),
                                                        ("0003", "0003 (Upper-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-right corner of the track"),
                                                        ("0004", "0004 (Lower-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-right corner of the track"),
                                                        ("0005", "0005 (Lower-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select target Power Pin for the upper-right corner of the track")),
                                               name="0003 (Upper-right)",
                                               default="0003")
    power_pin_remap_0004: bpy.props.EnumProperty(items=(("0002", "0002 (Upper-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-left corner of the track"),
                                                        ("0003", "0003 (Upper-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-left corner of the track"),
                                                        ("0004", "0004 (Lower-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-left corner of the track"),
                                                        ("0005", "0005 (Lower-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-left corner of the track")),
                                               name="0004 (Lower-left)",
                                               default="0004")
    power_pin_remap_0005: bpy.props.EnumProperty(items=(("0002", "0002 (Upper-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-right corner of the track"),
                                                        ("0003", "0003 (Upper-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-right corner of the track"),
                                                        ("0004", "0004 (Lower-left)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-right corner of the track"),
                                                        ("0005", "0005 (Lower-right)", "The four Power Pin data, Power Pin-0002 to 0005, follows the order of upper-left, upper-right, lower-left, lower-right.\nTo remap, select the target Power Pin for the lower-right corner of the track")),
                                               name="0005 (Lower-right)",
                                               default="0005")









    # fake settings before the first section is created
    start_frame: bpy.props.IntProperty(name="Start Frame",
                                       description="The first frame of the section",
                                       default=0
                                       )
    end_frame: bpy.props.IntProperty(name="End Frame",
                                     description="The last frame of the section",
                                     default=0
                                     )

    disable_section: bpy.props.BoolProperty(name="Disable section",
                                            description="Ignore the section and don't export anything from the section",
                                            default=False)

    smoothing_use_different_x_y: bpy.props.BoolProperty(name="Axes",
                                                        description="Use different regression settings for x and y axes of position, scale and Power Pin data",
                                                        default=False)
    smoothing_use_different_model: bpy.props.BoolProperty(name="Data",
                                                          description="Use different regression models for position, scale, rotation and Power Pin data",
                                                          default=False)
                                                          
    smoothing_extrapolate: bpy.props.BoolProperty(name="Extrapolate",
                                                  description="Generate position, scale, rotation and Power Pin data over the whole length of the section, even if the track is disabled on some of the frames.\n\nThe four options below, „Smooth Position“, „Smooth Scale“, „Smooth Rotation“ and „Smooth Power Pin“, decides whether to use predicted data to replace the existing data on frames where the track is enabled, while this option decides whether to use predicted data to fill the gaps in frames where the track is not enabled",
                                                  default=False)












    def _smoothing_regressor_update(self, context):
        self.smoothing_position_regressor = self.smoothing_regressor
        self.smoothing_scale_regressor = self.smoothing_regressor

        self.smoothing_rotation_regressor = self.smoothing_regressor

        self.smoothing_power_pin_regressor = self.smoothing_regressor


        pass

    smoothing_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_regressor_update)



    def _smoothing_huber_epsilon_update(self, context):
        self.smoothing_position_huber_epsilon = self.smoothing_huber_epsilon
        self.smoothing_scale_huber_epsilon = self.smoothing_huber_epsilon

        self.smoothing_rotation_huber_epsilon = self.smoothing_huber_epsilon

        self.smoothing_power_pin_huber_epsilon = self.smoothing_huber_epsilon


        pass

    smoothing_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_huber_epsilon_update)



    def _smoothing_lasso_alpha_update(self, context):
        self.smoothing_position_lasso_alpha = self.smoothing_lasso_alpha
        self.smoothing_scale_lasso_alpha = self.smoothing_lasso_alpha

        self.smoothing_rotation_lasso_alpha = self.smoothing_lasso_alpha

        self.smoothing_power_pin_lasso_alpha = self.smoothing_lasso_alpha


        pass

    smoothing_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_lasso_alpha_update)












    def _smoothing_do_position_update(self, context):

        pass

    smoothing_do_position: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on position data",
                default=True,
                update=_smoothing_do_position_update)



    def _smoothing_position_degree_update(self, context):


        pass

    smoothing_position_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for position data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=0,
                min=0,
                soft_max=16,
                update=_smoothing_position_degree_update)








    def _smoothing_do_scale_update(self, context):

        pass

    smoothing_do_scale: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on scale data",
                default=True,
                update=_smoothing_do_scale_update)



    def _smoothing_scale_degree_update(self, context):


        pass

    smoothing_scale_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for scale data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=0,
                min=0,
                soft_max=16,
                update=_smoothing_scale_degree_update)








    def _smoothing_do_rotation_update(self, context):

        pass

    smoothing_do_rotation: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on rotation data",
                default=True,
                update=_smoothing_do_rotation_update)



    def _smoothing_rotation_degree_update(self, context):


        pass

    smoothing_rotation_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for rotation data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=0,
                min=0,
                soft_max=16,
                update=_smoothing_rotation_degree_update)








    def _smoothing_do_power_pin_update(self, context):

        pass

    smoothing_do_power_pin: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on Power Pin data",
                default=True,
                update=_smoothing_do_power_pin_update)



    def _smoothing_power_pin_degree_update(self, context):


        pass

    smoothing_power_pin_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for power_pin data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=0,
                min=0,
                soft_max=16,
                update=_smoothing_power_pin_degree_update)





class AAEExportSettingsSectionL(bpy.types.PropertyGroup):
    bl_label = "AAEExportSettingsSectionL"
    bl_idname = "AAEExportSettingsSectionL"

    frame_update_suppress: bpy.props.BoolProperty(default=True)

    frame_update_tooltip: bpy.props.StringProperty(name="frame_update_tooltip", default="Sadly you can't rename sections")

    def _start_frame_update(self, context):
        if not self.frame_update_suppress:
            if context.edit_movieclip.AAEExportSettingsSectionLI == 0:
                context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                    = True
                context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame \
                    = context.edit_movieclip.frame_start
                context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                    = False
            else:
                if context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame < context.edit_movieclip.frame_start + context.edit_movieclip.AAEExportSettingsSectionLI:
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = True
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame \
                        = context.edit_movieclip.frame_start + context.edit_movieclip.AAEExportSettingsSectionLI
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = False
                if context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame > context.edit_movieclip.frame_start + context.edit_movieclip.frame_duration - context.edit_movieclip.AAEExportSettingsSectionLL + context.edit_movieclip.AAEExportSettingsSectionLI:
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = True
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame \
                        = context.edit_movieclip.frame_start + context.edit_movieclip.frame_duration - context.edit_movieclip.AAEExportSettingsSectionLL + context.edit_movieclip.AAEExportSettingsSectionLI
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = False
                for i in range(context.edit_movieclip.AAEExportSettingsSectionLI - 1, -1, -1):
                    context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                        = True
                    context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame \
                        = context.edit_movieclip.AAEExportSettingsSectionL[i + 1].start_frame
                    context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                        = False
                    if context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame >= context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame:
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = True
                        context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame - 1
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = False
                    else:
                        break
                for i in range(context.edit_movieclip.AAEExportSettingsSectionLI, context.edit_movieclip.AAEExportSettingsSectionLL - 1):
                    if context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame <= context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame:
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i + 1].frame_update_suppress \
                            = True
                        context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i + 1].start_frame \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame + 1
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i + 1].frame_update_suppress \
                            = False
                    else:
                        break

    def _end_frame_update(self, context):
        if not self.frame_update_suppress:
            if context.edit_movieclip.AAEExportSettingsSectionLI == context.edit_movieclip.AAEExportSettingsSectionLL - 1:
                context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                    = True
                context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame \
                    = context.edit_movieclip.frame_start + context.edit_movieclip.frame_duration - 1
                context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                    = False
            else:
                if context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame > context.edit_movieclip.frame_start + context.edit_movieclip.frame_duration - context.edit_movieclip.AAEExportSettingsSectionLL + context.edit_movieclip.AAEExportSettingsSectionLI:
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = True
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame \
                        = context.edit_movieclip.frame_start + context.edit_movieclip.frame_duration - context.edit_movieclip.AAEExportSettingsSectionLL + context.edit_movieclip.AAEExportSettingsSectionLI
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = False
                if context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame < context.edit_movieclip.frame_start + context.edit_movieclip.AAEExportSettingsSectionLI + 1:
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = True
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame \
                        = context.edit_movieclip.frame_start + context.edit_movieclip.AAEExportSettingsSectionLI + 1
                    context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                        = False
                for i in range(context.edit_movieclip.AAEExportSettingsSectionLI + 1, context.edit_movieclip.AAEExportSettingsSectionLL):
                    context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                        = True
                    context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame \
                        = context.edit_movieclip.AAEExportSettingsSectionL[i - 1].end_frame
                    context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                        = False
                    if context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame <= context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame:
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = True
                        context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame + 1
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = False
                    else:
                        break
                for i in range(context.edit_movieclip.AAEExportSettingsSectionLI, 0, -1):
                    if context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame >= context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame:
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i - 1].frame_update_suppress \
                            = True
                        context.edit_movieclip.AAEExportSettingsSectionL[i].start_frame \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i - 1].end_frame \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i].end_frame - 1
                        context.edit_movieclip.AAEExportSettingsSectionL[i].frame_update_suppress \
                            = context.edit_movieclip.AAEExportSettingsSectionL[i - 1].frame_update_suppress \
                            = False
                    else:
                        break
    
    start_frame: bpy.props.IntProperty(name="Start Frame",
                                       description="The first frame of the section",
                                       default=0,
                                       update=_start_frame_update)
    end_frame: bpy.props.IntProperty(name="End Frame",
                                     description="The last frame of the section",
                                     default=0,
                                     update=_end_frame_update)

    disable_section: bpy.props.BoolProperty(name="Disable section",
                                            description="Ignore the section and don't export anything from the section",
                                            default=False)

    smoothing_use_different_x_y: bpy.props.BoolProperty(name="Axes",
                                                        description="Use different regression settings for x and y axes of position, scale and Power Pin data",
                                                        default=False)
    smoothing_use_different_model: bpy.props.BoolProperty(name="Data",
                                                          description="Use different regression models for position, scale, rotation and Power Pin data",
                                                          default=False)
                                                          
    smoothing_extrapolate: bpy.props.BoolProperty(name="Extrapolate",
                                                  description="Generate position, scale, rotation and Power Pin data over the whole length of the section, even if the track is disabled on some of the frames.\n\nThe four options below, „Smooth Position“, „Smooth Scale“, „Smooth Rotation“ and „Smooth Power Pin“, decides whether to use predicted data to replace the existing data on frames where the track is enabled, while this option decides whether to use predicted data to fill the gaps in frames where the track is not enabled",
                                                  default=False)












    def _smoothing_regressor_update(self, context):
        self.smoothing_position_regressor = self.smoothing_regressor
        self.smoothing_scale_regressor = self.smoothing_regressor

        self.smoothing_rotation_regressor = self.smoothing_regressor

        self.smoothing_power_pin_regressor = self.smoothing_regressor


        self.smoothing_x_regressor = self.smoothing_regressor
        self.smoothing_y_regressor = self.smoothing_regressor

        pass

    smoothing_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_regressor_update)



    def _smoothing_huber_epsilon_update(self, context):
        self.smoothing_position_huber_epsilon = self.smoothing_huber_epsilon
        self.smoothing_scale_huber_epsilon = self.smoothing_huber_epsilon

        self.smoothing_rotation_huber_epsilon = self.smoothing_huber_epsilon

        self.smoothing_power_pin_huber_epsilon = self.smoothing_huber_epsilon


        self.smoothing_x_huber_epsilon = self.smoothing_huber_epsilon
        self.smoothing_y_huber_epsilon = self.smoothing_huber_epsilon

        pass

    smoothing_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_huber_epsilon_update)



    def _smoothing_lasso_alpha_update(self, context):
        self.smoothing_position_lasso_alpha = self.smoothing_lasso_alpha
        self.smoothing_scale_lasso_alpha = self.smoothing_lasso_alpha

        self.smoothing_rotation_lasso_alpha = self.smoothing_lasso_alpha

        self.smoothing_power_pin_lasso_alpha = self.smoothing_lasso_alpha


        self.smoothing_x_lasso_alpha = self.smoothing_lasso_alpha
        self.smoothing_y_lasso_alpha = self.smoothing_lasso_alpha

        pass

    smoothing_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_lasso_alpha_update)















    def _smoothing_x_regressor_update(self, context):
        self.smoothing_position_x_regressor = self.smoothing_x_regressor
        self.smoothing_scale_x_regressor = self.smoothing_x_regressor

        self.smoothing_rotation_regressor = self.smoothing_x_regressor

        self.smoothing_power_pin_x_regressor = self.smoothing_x_regressor

        pass

    smoothing_x_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_x_regressor_update)



    def _smoothing_x_huber_epsilon_update(self, context):
        self.smoothing_position_x_huber_epsilon = self.smoothing_x_huber_epsilon
        self.smoothing_scale_x_huber_epsilon = self.smoothing_x_huber_epsilon

        self.smoothing_rotation_huber_epsilon = self.smoothing_x_huber_epsilon

        self.smoothing_power_pin_x_huber_epsilon = self.smoothing_x_huber_epsilon

        pass

    smoothing_x_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_x_huber_epsilon_update)



    def _smoothing_x_lasso_alpha_update(self, context):
        self.smoothing_position_x_lasso_alpha = self.smoothing_x_lasso_alpha
        self.smoothing_scale_x_lasso_alpha = self.smoothing_x_lasso_alpha

        self.smoothing_rotation_lasso_alpha = self.smoothing_x_lasso_alpha

        self.smoothing_power_pin_x_lasso_alpha = self.smoothing_x_lasso_alpha

        pass

    smoothing_x_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_x_lasso_alpha_update)















    def _smoothing_y_regressor_update(self, context):
        self.smoothing_position_y_regressor = self.smoothing_y_regressor
        self.smoothing_scale_y_regressor = self.smoothing_y_regressor

        self.smoothing_power_pin_y_regressor = self.smoothing_y_regressor

        pass

    smoothing_y_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_y_regressor_update)



    def _smoothing_y_huber_epsilon_update(self, context):
        self.smoothing_position_y_huber_epsilon = self.smoothing_y_huber_epsilon
        self.smoothing_scale_y_huber_epsilon = self.smoothing_y_huber_epsilon

        self.smoothing_power_pin_y_huber_epsilon = self.smoothing_y_huber_epsilon

        pass

    smoothing_y_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_y_huber_epsilon_update)



    def _smoothing_y_lasso_alpha_update(self, context):
        self.smoothing_position_y_lasso_alpha = self.smoothing_y_lasso_alpha
        self.smoothing_scale_y_lasso_alpha = self.smoothing_y_lasso_alpha

        self.smoothing_power_pin_y_lasso_alpha = self.smoothing_y_lasso_alpha

        pass

    smoothing_y_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_y_lasso_alpha_update)












    def _smoothing_do_position_update(self, context):

        self.smoothing_do_position_x = self.smoothing_do_position
        self.smoothing_do_position_y = self.smoothing_do_position

        pass

    smoothing_do_position: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on position data",
                default=True,
                update=_smoothing_do_position_update)



    def _smoothing_position_degree_update(self, context):


        self.smoothing_position_x_degree = self.smoothing_position_degree
        self.smoothing_position_y_degree = self.smoothing_position_degree

        pass

    smoothing_position_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for position data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_position_degree_update)




    def _smoothing_position_regressor_update(self, context):


        self.smoothing_position_x_regressor = self.smoothing_position_regressor
        self.smoothing_position_y_regressor = self.smoothing_position_regressor

        pass

    smoothing_position_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_position_regressor_update)



    def _smoothing_position_huber_epsilon_update(self, context):


        self.smoothing_position_x_huber_epsilon = self.smoothing_position_huber_epsilon
        self.smoothing_position_y_huber_epsilon = self.smoothing_position_huber_epsilon

        pass

    smoothing_position_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_position_huber_epsilon_update)



    def _smoothing_position_lasso_alpha_update(self, context):


        self.smoothing_position_x_lasso_alpha = self.smoothing_position_lasso_alpha
        self.smoothing_position_y_lasso_alpha = self.smoothing_position_lasso_alpha

        pass

    smoothing_position_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_position_lasso_alpha_update)











    def _smoothing_do_position_x_update(self, context):
        pass

    smoothing_do_position_x: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on x axis of position data",
                default=True,
                update=_smoothing_do_position_x_update)



    def _smoothing_position_x_degree_update(self, context):

        pass

    smoothing_position_x_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for position x.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_position_x_degree_update)




    def _smoothing_position_x_regressor_update(self, context):

        pass

    smoothing_position_x_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_position_x_regressor_update)



    def _smoothing_position_x_huber_epsilon_update(self, context):

        pass

    smoothing_position_x_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_position_x_huber_epsilon_update)



    def _smoothing_position_x_lasso_alpha_update(self, context):

        pass

    smoothing_position_x_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_position_x_lasso_alpha_update)











    def _smoothing_do_position_y_update(self, context):
        pass

    smoothing_do_position_y: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on y axis of position data",
                default=True,
                update=_smoothing_do_position_y_update)



    def _smoothing_position_y_degree_update(self, context):

        pass

    smoothing_position_y_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for position y.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_position_y_degree_update)




    def _smoothing_position_y_regressor_update(self, context):

        pass

    smoothing_position_y_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_position_y_regressor_update)



    def _smoothing_position_y_huber_epsilon_update(self, context):

        pass

    smoothing_position_y_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_position_y_huber_epsilon_update)



    def _smoothing_position_y_lasso_alpha_update(self, context):

        pass

    smoothing_position_y_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_position_y_lasso_alpha_update)












    def _smoothing_do_scale_update(self, context):

        self.smoothing_do_scale_x = self.smoothing_do_scale
        self.smoothing_do_scale_y = self.smoothing_do_scale

        pass

    smoothing_do_scale: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on scale data",
                default=True,
                update=_smoothing_do_scale_update)



    def _smoothing_scale_degree_update(self, context):


        self.smoothing_scale_x_degree = self.smoothing_scale_degree
        self.smoothing_scale_y_degree = self.smoothing_scale_degree

        pass

    smoothing_scale_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for scale data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_scale_degree_update)




    def _smoothing_scale_regressor_update(self, context):


        self.smoothing_scale_x_regressor = self.smoothing_scale_regressor
        self.smoothing_scale_y_regressor = self.smoothing_scale_regressor

        pass

    smoothing_scale_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_scale_regressor_update)



    def _smoothing_scale_huber_epsilon_update(self, context):


        self.smoothing_scale_x_huber_epsilon = self.smoothing_scale_huber_epsilon
        self.smoothing_scale_y_huber_epsilon = self.smoothing_scale_huber_epsilon

        pass

    smoothing_scale_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_scale_huber_epsilon_update)



    def _smoothing_scale_lasso_alpha_update(self, context):


        self.smoothing_scale_x_lasso_alpha = self.smoothing_scale_lasso_alpha
        self.smoothing_scale_y_lasso_alpha = self.smoothing_scale_lasso_alpha

        pass

    smoothing_scale_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_scale_lasso_alpha_update)











    def _smoothing_do_scale_x_update(self, context):
        pass

    smoothing_do_scale_x: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on x axis of scale data",
                default=True,
                update=_smoothing_do_scale_x_update)



    def _smoothing_scale_x_degree_update(self, context):

        pass

    smoothing_scale_x_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for scale x.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_scale_x_degree_update)




    def _smoothing_scale_x_regressor_update(self, context):

        pass

    smoothing_scale_x_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_scale_x_regressor_update)



    def _smoothing_scale_x_huber_epsilon_update(self, context):

        pass

    smoothing_scale_x_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_scale_x_huber_epsilon_update)



    def _smoothing_scale_x_lasso_alpha_update(self, context):

        pass

    smoothing_scale_x_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_scale_x_lasso_alpha_update)











    def _smoothing_do_scale_y_update(self, context):
        pass

    smoothing_do_scale_y: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on y axis of scale data.\nAs of May 2023, a-mo does not support using different scale for different axes",
                default=True,
                update=_smoothing_do_scale_y_update)



    def _smoothing_scale_y_degree_update(self, context):

        pass

    smoothing_scale_y_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for scale y.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_scale_y_degree_update)




    def _smoothing_scale_y_regressor_update(self, context):

        pass

    smoothing_scale_y_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_scale_y_regressor_update)



    def _smoothing_scale_y_huber_epsilon_update(self, context):

        pass

    smoothing_scale_y_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_scale_y_huber_epsilon_update)



    def _smoothing_scale_y_lasso_alpha_update(self, context):

        pass

    smoothing_scale_y_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_scale_y_lasso_alpha_update)













    def _smoothing_do_rotation_update(self, context):

        pass

    smoothing_do_rotation: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on rotation data",
                default=True,
                update=_smoothing_do_rotation_update)



    def _smoothing_rotation_degree_update(self, context):


        pass

    smoothing_rotation_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for rotation data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=1,
                min=0,
                soft_max=16,
                update=_smoothing_rotation_degree_update)




    def _smoothing_rotation_regressor_update(self, context):


        pass

    smoothing_rotation_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_rotation_regressor_update)



    def _smoothing_rotation_huber_epsilon_update(self, context):


        pass

    smoothing_rotation_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_rotation_huber_epsilon_update)



    def _smoothing_rotation_lasso_alpha_update(self, context):


        pass

    smoothing_rotation_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_rotation_lasso_alpha_update)













    def _smoothing_do_power_pin_update(self, context):

        self.smoothing_do_power_pin_x = self.smoothing_do_power_pin
        self.smoothing_do_power_pin_y = self.smoothing_do_power_pin

        pass

    smoothing_do_power_pin: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on Power Pin data",
                default=True,
                update=_smoothing_do_power_pin_update)



    def _smoothing_power_pin_degree_update(self, context):


        self.smoothing_power_pin_x_degree = self.smoothing_power_pin_degree
        self.smoothing_power_pin_y_degree = self.smoothing_power_pin_degree

        pass

    smoothing_power_pin_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for Power Pin data.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_power_pin_degree_update)




    def _smoothing_power_pin_regressor_update(self, context):


        self.smoothing_power_pin_x_regressor = self.smoothing_power_pin_regressor
        self.smoothing_power_pin_y_regressor = self.smoothing_power_pin_regressor

        pass

    smoothing_power_pin_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_power_pin_regressor_update)



    def _smoothing_power_pin_huber_epsilon_update(self, context):


        self.smoothing_power_pin_x_huber_epsilon = self.smoothing_power_pin_huber_epsilon
        self.smoothing_power_pin_y_huber_epsilon = self.smoothing_power_pin_huber_epsilon

        pass

    smoothing_power_pin_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_power_pin_huber_epsilon_update)



    def _smoothing_power_pin_lasso_alpha_update(self, context):


        self.smoothing_power_pin_x_lasso_alpha = self.smoothing_power_pin_lasso_alpha
        self.smoothing_power_pin_y_lasso_alpha = self.smoothing_power_pin_lasso_alpha

        pass

    smoothing_power_pin_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_power_pin_lasso_alpha_update)











    def _smoothing_do_power_pin_x_update(self, context):
        pass

    smoothing_do_power_pin_x: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on x axis of Power Pin data",
                default=True,
                update=_smoothing_do_power_pin_x_update)



    def _smoothing_power_pin_x_degree_update(self, context):

        pass

    smoothing_power_pin_x_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for Power Pin x.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_power_pin_x_degree_update)




    def _smoothing_power_pin_x_regressor_update(self, context):

        pass

    smoothing_power_pin_x_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_power_pin_x_regressor_update)



    def _smoothing_power_pin_x_huber_epsilon_update(self, context):

        pass

    smoothing_power_pin_x_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_power_pin_x_huber_epsilon_update)



    def _smoothing_power_pin_x_lasso_alpha_update(self, context):

        pass

    smoothing_power_pin_x_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_power_pin_x_lasso_alpha_update)











    def _smoothing_do_power_pin_y_update(self, context):
        pass

    smoothing_do_power_pin_y: bpy.props.BoolProperty(
                name="Smooth",
                description="Perform smoothing on y axis of Power Pin data",
                default=True,
                update=_smoothing_do_power_pin_y_update)



    def _smoothing_power_pin_y_degree_update(self, context):

        pass

    smoothing_power_pin_y_degree: bpy.props.IntProperty(
                name="Max Degree",
                description="The maximal polynomial degree for Power Pin y.\nSet degree to 0 to average the data in the section, 1 to perform linear regression on the data, 2 to perform quadratic regression on the data, and 3 to perform cubic regression on the data.\n\nSetting this too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                default=2,
                min=0,
                soft_max=16,
                update=_smoothing_power_pin_y_degree_update)




    def _smoothing_power_pin_y_regressor_update(self, context):

        pass

    smoothing_power_pin_y_regressor: bpy.props.EnumProperty(
                items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                       ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                       ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                name="Linear Model",
                default="LINEAR",
                update=_smoothing_power_pin_y_regressor_update)



    def _smoothing_power_pin_y_huber_epsilon_update(self, context):

        pass

    smoothing_power_pin_y_huber_epsilon: bpy.props.FloatProperty(
                name="Epsilon",
                description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                default=1.50,
                min=1.00,
                soft_max=10.00,
                step=1,
                precision=2,
                update=_smoothing_power_pin_y_huber_epsilon_update)



    def _smoothing_power_pin_y_lasso_alpha_update(self, context):

        pass

    smoothing_power_pin_y_lasso_alpha: bpy.props.FloatProperty(
                name="Alpha",
                description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                default=0.10,
                min=0.00,
                soft_max=100.0,
                step=1,
                precision=2,
                update=_smoothing_power_pin_y_lasso_alpha_update)












class AAEExportExportAll(bpy.types.Operator):
    bl_label = "Export"
    bl_description = "Export all tracking markers and plane tracks to AAE files next to the original movie clip"
    bl_idname = "movieclip.aae_export_export_all"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings
        clip_settings = context.edit_movieclip.AAEExportSettingsClip
        section_settings_l = context.edit_movieclip.AAEExportSettingsSectionL
        section_settings_ll = context.edit_movieclip.AAEExportSettingsSectionLL

        for track in clip.tracking.tracks:
            AAEExportExportAll._export_to_file( \
                clip, track, \
                AAEExportExportAll._generate(clip, track, settings, clip_settings, section_settings_l, section_settings_ll), \
                None, settings.do_do_not_overwrite)

        for plane_track in clip.tracking.plane_tracks:
            AAEExportExportAll._export_to_file( \
                clip, plane_track, \
                AAEExportExportAll._generate(clip, plane_track, settings, clip_settings, section_settings_l, section_settings_ll), \
                None, settings.do_do_not_overwrite)
        
        return { "FINISHED" }

    @staticmethod
    def _generate(clip, track, settings, clip_settings, section_settings_l, section_settings_ll):
        """
        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or bpy.types.MovieTrackingPlaneTrack
        settings : AAEExportSettings
            AAEExportSettings.
        clip_settings : AAEExportSettingsClip
            AAEExportSettingsClip.
        section_settings_l : AAEExportSettingsSectionL
            AAEExportSettingsSectionL.
        section_settings_ll : bpy.props.IntProperty
            AAEExportSettingsSectionLL.

        Returns
        -------
        aae : str

        """
        if is_smoothing_modules_available:
            ratio, multiplier \
                = AAEExportExportAll._calculate_aspect_ratio( \
                      clip)

            data \
                = AAEExportExportAll._prepare_data( \
                      clip, track, ratio, \
                      clip_settings.power_pin_remap_0002, clip_settings.power_pin_remap_0003, clip_settings.power_pin_remap_0004, clip_settings.power_pin_remap_0005)

            if clip_settings.do_smoothing:
                AAEExportExportAll._unlimit_rotation_and_frz_fax( \
                    data)

                parsed_section_settings \
                    = AAEExportExportAll._parse_section_settings( \
                        section_settings_l, section_settings_ll)

                data \
                    = AAEExportExportAll._smoothing_main( \
                          data, \
                          clip, clip_settings, parsed_section_settings, section_settings_ll)

                AAEExportExportAll._limit_rotation_and_frz_fax( \
                    data)
            else:
                AAEExportExportAll._limit_rotation_and_frz_fax( \
                    data)

            aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, aae_frz_fax \
                = AAEExportExportAll._generate_aae( \
                      data, multiplier)

        else: # not is_smoothing_modules_available
            aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005 \
                = AAEExportExportAll._generate_aae_non_numpy( \
                      clip, track)

            aae_frz_fax \
                = None

        aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005 \
            = AAEExportExportAll._remap_power_pin( \
                  aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, \
                  clip_settings.power_pin_remap_0002, clip_settings.power_pin_remap_0003, clip_settings.power_pin_remap_0004, clip_settings.power_pin_remap_0005)

        aae \
            = AAEExportExportAll._combine_aae( \
                  clip, \
                  aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, aae_frz_fax, \
                  settings.do_includes_power_pin)

        return aae

    @staticmethod
    def _plot_result(clip, track, settings, clip_settings, section_settings_l, section_settings_ll):
        """
        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or bpy.types.MovieTrackingPlaneTrack
        settings : AAEExportSettings
            AAEExportSettings.
        clip_settings : AAEExportSettingsClip
            AAEExportSettingsClip.
        section_settings_l : AAEExportSettingsSectionL
            AAEExportSettingsSectionL.
        section_settings_ll : bpy.props.IntProperty
            AAEExportSettingsSectionLL.

        """
        import collections
        import numpy as np
        
        ratio, _ \
            = AAEExportExportAll._calculate_aspect_ratio( \
                  clip)

        data \
            = AAEExportExportAll._prepare_data( \
                  clip, track, ratio, \
                  clip_settings.power_pin_remap_0002, clip_settings.power_pin_remap_0003, clip_settings.power_pin_remap_0004, clip_settings.power_pin_remap_0005)

        AAEExportExportAll._unlimit_rotation_and_frz_fax( \
            data)

        parsed_section_settings \
            = AAEExportExportAll._parse_section_settings( \
                section_settings_l, section_settings_ll)

        if clip_settings.smoothing_blending != "NONE" and \
           section_settings_ll > 1 and \
           sum([not (np.all(np.isnan(data[0][parsed_section_settings[i]["start_frame"]:parsed_section_settings[i]["end_frame"]])) or \
                     parsed_section_settings[i]["disable_section"]) for i in range(section_settings_ll)]) > 1:
            smoothed_data, no_blending_data \
                = AAEExportExportAll._smoothing_main( \
                      data, \
                      clip, clip_settings, parsed_section_settings, section_settings_ll, \
                      plotting=True)

            AAEExportExportAll._plot_result_plot( \
                data, smoothed_data, no_blending_data, \
                clip_settings)
        else:
            smoothed_data \
                = AAEExportExportAll._smoothing_main( \
                      data, \
                      clip, clip_settings, parsed_section_settings, section_settings_ll)

            AAEExportExportAll._plot_result_plot( \
                data, smoothed_data, [None] * 13, \
                clip_settings)

    @staticmethod
    def _plot_section(clip, track, settings, clip_settings, section_settings_l, section_settings_li, section_settings_ll):
        """
        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or bpy.types.MovieTrackingPlaneTrack
        settings : AAEExportSettings
            AAEExportSettings.
        clip_settings : AAEExportSettingsClip
            AAEExportSettingsClip.
        section_settings_l : AAEExportSettingsSectionL
            AAEExportSettingsSectionL.
        section_settings_li : bpy.props.IntProperty
            AAEExportSettingsSectionLI.
        section_settings_ll : bpy.props.IntProperty
            AAEExportSettingsSectionLL.

        """
        import collections
        import numpy as np
        
        ratio, _ \
            = AAEExportExportAll._calculate_aspect_ratio( \
                  clip)

        data \
            = AAEExportExportAll._prepare_data( \
                  clip, track, ratio, \
                  clip_settings.power_pin_remap_0002, clip_settings.power_pin_remap_0003, clip_settings.power_pin_remap_0004, clip_settings.power_pin_remap_0005)

        AAEExportExportAll._unlimit_rotation_and_frz_fax( \
            data)

        parsed_section_settings \
            = AAEExportExportAll._parse_section_settings( \
                section_settings_l, section_settings_ll)

        smoothed_data = {}
        for i in range(15):
            data[i] = \
                data[i][parsed_section_settings[section_settings_li]["start_frame"]:parsed_section_settings[section_settings_li]["end_frame"]]
            if parsed_section_settings[section_settings_li][i]["smoothing"] or \
               parsed_section_settings[section_settings_li]["smoothing_extrapolate"]:
                smoothed_data[i] = \
                    AAEExportExportAll._smoothing( \
                        data[i],
                        parsed_section_settings[section_settings_li][i])
            else:
                smoothed_data[i] = \
                    None

        AAEExportExportAll._plot_section_plot( \
            data, smoothed_data, \
            parsed_section_settings[section_settings_li])

    @staticmethod
    def _calculate_aspect_ratio(clip):
        """
        Calculate aspect ratio.

        Parameters
        ----------
        clip : bpy.types.MovieClip

        Returns
        -------
        ratio : tuple[float64]
        multiplier: float

        """
        import numpy as np

        ar = clip.size[0] / clip.size[1]
        # As of 2021/2022
        if ar < 1 / 1.35: # 9:16, 9:19 and higher videos
            return (1 / 1.35, 1 / 1.35 / ar), clip.size[0] / 1 * 1.35
        elif ar < 1: # vertical videos from 1:1, 3:4, up to 1:1.35
            return (ar, 1), clip.size[1]
        elif ar <= 1.81: # 1:1, 4:3, 16:9, up to 1920 x 1061
            return (ar, 1), clip.size[1]
        else: # Ultrawide
            return (1.81, 1.81 / ar), clip.size[0] / 1.81

    @staticmethod
    def _prepare_data(clip, track, ratio, power_pin_remap_0002, power_pin_remap_0003, power_pin_remap_0004, power_pin_remap_0005):
        """
        Create position, scale, rotation and Power Pin array from tracking markers. [Step 04]

        Parameters
        ----------
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack or bpy.types.MovieTrackingPlaneTrack
        ratio : tuple[float64]

        Returns
        -------
        data : dict[npt.NDArray[float64]]

        """
        # data
        # {
        #      0: position_x,
        #      1: position_y,
        #      2: scale_x,
        #      3: scale_y,
        #      4: rotation,
        #      5: power_pin_0002_x (relative to position_x),
        #      6: power_pin_0002_y (relative to position_y),
        #      7: power_pin_0003_x,
        #      8: power_pin_0003_y,
        #      9: power_pin_0004_x,
        #     10: power_pin_0004_y,
        #     11: power_pin_0005_x,
        #     12: power_pin_0005_y,
        #     13: frz axis,
        #     14: fax axis
        # }
        data = {}

        if track.__class__.__name__ == "MovieTrackingTrack":
            AAEExportExportAll._prepare_position_and_power_pin_marker_track( \
                data, clip, track, ratio)
        elif track.__class__.__name__ == "MovieTrackingPlaneTrack":
            AAEExportExportAll._prepare_position_and_power_pin_plane_track( \
                data, clip, track, ratio)
        else:
            raise ValueError("track.__class__.__name__ \"" + track.__class__.__name__ + "\" not recognised")

        AAEExportExportAll._prepare_scale_and_semilimited_rotation( \
            data)

        AAEExportExportAll._prepare_frz_fax( \
            data, \
            power_pin_remap_0002, power_pin_remap_0003, power_pin_remap_0004, power_pin_remap_0005)

        return data

    @staticmethod
    def _prepare_position_and_power_pin_marker_track(data, clip, track, ratio):
        """
        Create position and Power Pin array from marker track.

        Parameters
        ----------
        data : dict[npt.NDArray[float64]]
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack
        ratio : tuple[float64]

        """
        import numpy as np

        if not clip.frame_duration >= 1:
            raise ValueError("clip.frame_duration must be greater than or equal to 1")

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
        data[0] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[1] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        
        # power pin position is not absolute and is relative to the position
        data[5] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[6] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[7] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[8] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[9] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[10] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[11] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[12] = np.full(clip.frame_duration, np.nan, dtype=np.float64)

        for marker in track.markers:
            if not clip.frame_start <= marker.frame <= clip.frame_duration:
                continue
            if marker.mute:
                continue

            i = marker.frame - clip.frame_start

            data[0][i] = marker.co[0] * ratio[0]
            data[1][i] = (1 - marker.co[1]) * ratio[1]

            data[5][i] = marker.pattern_corners[3][0] * ratio[0]
            data[6][i] = -marker.pattern_corners[3][1] * ratio[1]
            data[7][i] = marker.pattern_corners[2][0] * ratio[0]
            data[8][i] = -marker.pattern_corners[2][1] * ratio[1]
            data[9][i] = marker.pattern_corners[0][0] * ratio[0]
            data[10][i] = -marker.pattern_corners[0][1] * ratio[1]
            data[11][i] = marker.pattern_corners[1][0] * ratio[0]
            data[12][i] = -marker.pattern_corners[1][1] * ratio[1]

    @staticmethod
    def _prepare_position_and_power_pin_plane_track(data, clip, track, ratio):
        """
        Create position and Power Pin array from plane track.

        Parameters
        ----------
        data : dict[npt.NDArray[float64]]
        clip : bpy.types.MovieClip
        track : bpy.types.MovieTrackingTrack
        ratio : tuple[float64]

        """
        import numpy as np
        import numpy.linalg as LA

        if not clip.frame_duration >= 1:
            raise ValueError("clip.frame_duration must be greater than or equal to 1")

        # As explained in _prepare_position_and_misshapen_power_pin_marker_track() above
        data[0] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[1] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        
        data[5] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[6] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[7] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[8] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[9] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[10] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[11] = np.full(clip.frame_duration, np.nan, dtype=np.float64)
        data[12] = np.full(clip.frame_duration, np.nan, dtype=np.float64)

        for marker in track.markers:
            if not clip.frame_start <= marker.frame <= clip.frame_duration:
                continue
            if marker.mute:
                continue

            i = marker.frame - clip.frame_start

            data[5][i] = marker.corners[3][0] * ratio[0]
            data[6][i] = -marker.corners[3][1] * ratio[1]
            data[7][i] = marker.corners[2][0] * ratio[0]
            data[8][i] = -marker.corners[2][1] * ratio[1]
            data[9][i] = marker.corners[0][0] * ratio[0]
            data[10][i] = -marker.corners[0][1] * ratio[1]
            data[11][i] = marker.corners[1][0] * ratio[0]
            data[12][i] = -marker.corners[1][1] * ratio[1]

            if not np.isnan(data[5][i]):
                try:
                    t = LA.solve([[data[11][i] - data[5][i], data[7][i] - data[9][i]],
                                  [data[12][i] - data[6][i], data[8][i] - data[10][i]]],
                                 [data[7][i] - data[5][i], data[8][i] - data[6][i]])[0]
                except LA.LinAlgError:
                    data[0][i] = (data[5][i] + data[7][i] + data[9][i] + data[11][i]) / 4
                    data[1][i] = (data[6][i] + data[8][i] + data[10][i] + data[12][i]) / 4
                else:
                    data[0][i] = (1 - t) * data[5][i] + t * data[11][i]
                    data[1][i] = (1 - t) * data[6][i] + t * data[12][i]

            for j in range(5, 13, 2):
                data[j][i] -= data[0][i]
                data[j + 1][i] -= data[1][i]
            
            # This is discarded due to it being unstable, despite its slightly
            # faster speed.
            # https://stackoverflow.com/questions/563198/
            # def eat(slice):
            #     if slice[0] == np.nan:
            #         return np.full((2), np.nan, dtype=np.float64)
            #     else:
            #         p = slice[0:2]
            #         r = slice[6:8] - slice[0:2]
            #         q = slice[4:6]
            #         s = slice[2:4] - slice[4:6]
            #         t = np.cross((q - p), s) / np.cross(r, s)
            #         return p + t * r

            # https://stackoverflow.com/questions/563198/
            # def eat_(slice):
            #     if np.isnan(slice[0]):
            #         return np.full((2), np.nan, dtype=np.float64)
            #     try:
            #         t = LA.solve(np.transpose(np.vstack((slice[6:8] - slice[0:2], slice[2:4] - slice[4:6]))), slice[2:4] - slice[0:2])[0]
            #     except LA.LinAlgError:
            #         return np.mean(slice.reshape((4, 2)), axis=0)
            #     else:
            #         return (1 - t) * slice[0:2] + t * slice[6:8]

    @staticmethod
    def _prepare_scale_and_semilimited_rotation(data):
        """
        Create scale and rotation array.

        Parameters
        ----------
        data : dict[npt.NDArray[float64]]

        """
        import numpy as np
        import numpy.linalg as LA

        # https://stackoverflow.com/questions/1401712/
        data[2] = LA.norm(np.column_stack((data[5] - data[7] + data[9] - data[11],
                                           data[6] - data[8] + data[10] - data[12])), axis=1)
        data[3] = LA.norm(np.column_stack((data[5] - data[9] + data[7] - data[11],
                                           data[6] - data[10] + data[8] - data[12])), axis=1)
        try:
            data[2] /= data[2][np.nonzero(~np.isnan(data[2]))[0][0]]
            data[3] /= data[3][np.nonzero(~np.isnan(data[2]))[0][0]]
        except IndexError:
            raise ValueError("At least one marker in track.markers needs to be not marker.mute")

        data[4] = np.arctan2(data[5] + data[7], -data[6] - data[8])


    @staticmethod
    def _prepare_frz_fax(data, power_pin_remap_0002, power_pin_remap_0003, power_pin_remap_0004, power_pin_remap_0005):
        import numpy as np

        power_pin_data = {}
        power_pin_data[0] = None
        power_pin_data[1] = None
        power_pin_data[2] = None
        power_pin_data[3] = None
        power_pin_data[4] = None
        power_pin_data[5] = None





        match power_pin_remap_0002:
            case "0002":
                power_pin_data[0] =  power_pin_data[0] if power_pin_data[0] is not None else data[5]
                power_pin_data[1] =  power_pin_data[1] if power_pin_data[1] is not None else data[6]
            case "0003":
                pass
            case "0004":
                power_pin_data[2] =  power_pin_data[2] if power_pin_data[2] is not None else data[5]
                power_pin_data[3] =  power_pin_data[3] if power_pin_data[3] is not None else data[6]
            case "0005":
                power_pin_data[4] =  power_pin_data[4] if power_pin_data[4] is not None else data[5]
                power_pin_data[5] =  power_pin_data[5] if power_pin_data[5] is not None else data[6]





        match power_pin_remap_0003:
            case "0002":
                power_pin_data[0] =  power_pin_data[0] if power_pin_data[0] is not None else data[7]
                power_pin_data[1] =  power_pin_data[1] if power_pin_data[1] is not None else data[8]
            case "0003":
                pass
            case "0004":
                power_pin_data[2] =  power_pin_data[2] if power_pin_data[2] is not None else data[7]
                power_pin_data[3] =  power_pin_data[3] if power_pin_data[3] is not None else data[8]
            case "0005":
                power_pin_data[4] =  power_pin_data[4] if power_pin_data[4] is not None else data[7]
                power_pin_data[5] =  power_pin_data[5] if power_pin_data[5] is not None else data[8]





        match power_pin_remap_0004:
            case "0002":
                power_pin_data[0] =  power_pin_data[0] if power_pin_data[0] is not None else data[9]
                power_pin_data[1] =  power_pin_data[1] if power_pin_data[1] is not None else data[10]
            case "0003":
                pass
            case "0004":
                power_pin_data[2] =  power_pin_data[2] if power_pin_data[2] is not None else data[9]
                power_pin_data[3] =  power_pin_data[3] if power_pin_data[3] is not None else data[10]
            case "0005":
                power_pin_data[4] =  power_pin_data[4] if power_pin_data[4] is not None else data[9]
                power_pin_data[5] =  power_pin_data[5] if power_pin_data[5] is not None else data[10]





        match power_pin_remap_0005:
            case "0002":
                power_pin_data[0] =  power_pin_data[0] if power_pin_data[0] is not None else data[11]
                power_pin_data[1] =  power_pin_data[1] if power_pin_data[1] is not None else data[12]
            case "0003":
                pass
            case "0004":
                power_pin_data[2] =  power_pin_data[2] if power_pin_data[2] is not None else data[11]
                power_pin_data[3] =  power_pin_data[3] if power_pin_data[3] is not None else data[12]
            case "0005":
                power_pin_data[4] =  power_pin_data[4] if power_pin_data[4] is not None else data[11]
                power_pin_data[5] =  power_pin_data[5] if power_pin_data[5] is not None else data[12]






        if power_pin_data[0] is None:
            raise ValueError("ortho-mo requires at least one Power Pin to be specified as Power Pin 0002")
        if power_pin_data[2] is None:
            raise ValueError("ortho-mo requires at least one Power Pin to be specified as Power Pin 0004")
        if power_pin_data[4] is None:
            raise ValueError("ortho-mo requires at least one Power Pin to be specified as Power Pin 0005")

        data[13] = np.arctan2(-power_pin_data[5] + power_pin_data[3], power_pin_data[4] - power_pin_data[2])
        data[14] = np.arctan2(-power_pin_data[1] + power_pin_data[3], power_pin_data[0] - power_pin_data[2])

    @staticmethod
    def _unlimit_rotation_and_frz_fax(data):
        """
        Unlimit the rotation.

        Parameters
        ----------
        data : dict[npt.NDArray[float64]]

        """
        import numpy as np

        for i in (4, 13, 14):
            diff = np.diff(data[i])

            for j in np.nonzero(diff > np.pi)[0]:
                data[i][j+1:] -= 2 * np.pi
            for j in np.nonzero(diff <= -np.pi)[0]:
                data[i][j+1:] += 2 * np.pi

    @staticmethod
    def _limit_rotation_and_frz_fax(data):
        """
        Limit the rotation.

        Parameters
        ----------
        data : dict[npt.NDArray[float64]]

        """
        import numpy as np

        for i in (4, 13, 14):
            np.remainder(data[i], 2 * np.pi, out=data[i])

    @staticmethod
    def _parse_section_settings(section_settings_l, section_settings_ll):
        """
        Deal with the messy Blender and output an easy to use section settings.

        Parameters
        ----------
        section_settings_l : AAEExportSettingsSectionL
            AAEExportSettingsSectionL.
        section_settings_ll : bpy.props.IntProperty
            AAEExportSettingsSectionLL.

        Returns
        -------
        parsed_settings : dict[dict[dict[]]]

        """
        # parsed_settings structure
        #
        # {
        #     (Section) 0: {
        #         start_frame: 0
        #
        #         (Type) 0..12: {
        #             degree: 2
        #
        #         }
        #     }
        # }
        parsed_settings = {}

        for i in range(section_settings_ll):
            parsed_settings[i] = {}

            parsed_settings[i]["start_frame"] = section_settings_l[i].start_frame - 1
            parsed_settings[i]["end_frame"] = section_settings_l[i].end_frame

            parsed_settings[i]["disable_section"] = section_settings_l[i].disable_section
            parsed_settings[i]["smoothing_extrapolate"] = section_settings_l[i].smoothing_extrapolate



  

            parsed_settings[i][0] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][0]["smoothing"] = section_settings_l[i].smoothing_do_position
                    parsed_settings[i][0]["degree"] = section_settings_l[i].smoothing_position_degree
                    parsed_settings[i][0]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][0]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][0]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][0]["smoothing"] = section_settings_l[i].smoothing_do_position
                    parsed_settings[i][0]["degree"] = section_settings_l[i].smoothing_position_degree
                    parsed_settings[i][0]["regressor"] = section_settings_l[i].smoothing_position_regressor
                    parsed_settings[i][0]["huber_epsilon"] = section_settings_l[i].smoothing_position_huber_epsilon
                    parsed_settings[i][0]["lasso_alpha"] = section_settings_l[i].smoothing_position_lasso_alpha
                case 0b10:

                    parsed_settings[i][0]["smoothing"] = section_settings_l[i].smoothing_do_position_x
                    parsed_settings[i][0]["degree"] = section_settings_l[i].smoothing_position_x_degree
                    parsed_settings[i][0]["regressor"] = section_settings_l[i].smoothing_x_regressor
                    parsed_settings[i][0]["huber_epsilon"] = section_settings_l[i].smoothing_x_huber_epsilon
                    parsed_settings[i][0]["lasso_alpha"] = section_settings_l[i].smoothing_x_lasso_alpha

                case 0b11:

                    parsed_settings[i][0]["smoothing"] = section_settings_l[i].smoothing_do_position_x
                    parsed_settings[i][0]["degree"] = section_settings_l[i].smoothing_position_x_degree
                    parsed_settings[i][0]["regressor"] = section_settings_l[i].smoothing_position_x_regressor
                    parsed_settings[i][0]["huber_epsilon"] = section_settings_l[i].smoothing_position_x_huber_epsilon
                    parsed_settings[i][0]["lasso_alpha"] = section_settings_l[i].smoothing_position_x_lasso_alpha


  
  

            parsed_settings[i][1] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][1]["smoothing"] = section_settings_l[i].smoothing_do_position
                    parsed_settings[i][1]["degree"] = section_settings_l[i].smoothing_position_degree
                    parsed_settings[i][1]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][1]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][1]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][1]["smoothing"] = section_settings_l[i].smoothing_do_position
                    parsed_settings[i][1]["degree"] = section_settings_l[i].smoothing_position_degree
                    parsed_settings[i][1]["regressor"] = section_settings_l[i].smoothing_position_regressor
                    parsed_settings[i][1]["huber_epsilon"] = section_settings_l[i].smoothing_position_huber_epsilon
                    parsed_settings[i][1]["lasso_alpha"] = section_settings_l[i].smoothing_position_lasso_alpha
                case 0b10:

                    parsed_settings[i][1]["smoothing"] = section_settings_l[i].smoothing_do_position_y
                    parsed_settings[i][1]["degree"] = section_settings_l[i].smoothing_position_y_degree
                    parsed_settings[i][1]["regressor"] = section_settings_l[i].smoothing_y_regressor
                    parsed_settings[i][1]["huber_epsilon"] = section_settings_l[i].smoothing_y_huber_epsilon
                    parsed_settings[i][1]["lasso_alpha"] = section_settings_l[i].smoothing_y_lasso_alpha

                case 0b11:

                    parsed_settings[i][1]["smoothing"] = section_settings_l[i].smoothing_do_position_y
                    parsed_settings[i][1]["degree"] = section_settings_l[i].smoothing_position_y_degree
                    parsed_settings[i][1]["regressor"] = section_settings_l[i].smoothing_position_y_regressor
                    parsed_settings[i][1]["huber_epsilon"] = section_settings_l[i].smoothing_position_y_huber_epsilon
                    parsed_settings[i][1]["lasso_alpha"] = section_settings_l[i].smoothing_position_y_lasso_alpha


  

  

            parsed_settings[i][2] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][2]["smoothing"] = section_settings_l[i].smoothing_do_scale
                    parsed_settings[i][2]["degree"] = section_settings_l[i].smoothing_scale_degree
                    parsed_settings[i][2]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][2]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][2]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][2]["smoothing"] = section_settings_l[i].smoothing_do_scale
                    parsed_settings[i][2]["degree"] = section_settings_l[i].smoothing_scale_degree
                    parsed_settings[i][2]["regressor"] = section_settings_l[i].smoothing_scale_regressor
                    parsed_settings[i][2]["huber_epsilon"] = section_settings_l[i].smoothing_scale_huber_epsilon
                    parsed_settings[i][2]["lasso_alpha"] = section_settings_l[i].smoothing_scale_lasso_alpha
                case 0b10:

                    parsed_settings[i][2]["smoothing"] = section_settings_l[i].smoothing_do_scale_x
                    parsed_settings[i][2]["degree"] = section_settings_l[i].smoothing_scale_x_degree
                    parsed_settings[i][2]["regressor"] = section_settings_l[i].smoothing_x_regressor
                    parsed_settings[i][2]["huber_epsilon"] = section_settings_l[i].smoothing_x_huber_epsilon
                    parsed_settings[i][2]["lasso_alpha"] = section_settings_l[i].smoothing_x_lasso_alpha

                case 0b11:

                    parsed_settings[i][2]["smoothing"] = section_settings_l[i].smoothing_do_scale_x
                    parsed_settings[i][2]["degree"] = section_settings_l[i].smoothing_scale_x_degree
                    parsed_settings[i][2]["regressor"] = section_settings_l[i].smoothing_scale_x_regressor
                    parsed_settings[i][2]["huber_epsilon"] = section_settings_l[i].smoothing_scale_x_huber_epsilon
                    parsed_settings[i][2]["lasso_alpha"] = section_settings_l[i].smoothing_scale_x_lasso_alpha


  
  

            parsed_settings[i][3] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][3]["smoothing"] = section_settings_l[i].smoothing_do_scale
                    parsed_settings[i][3]["degree"] = section_settings_l[i].smoothing_scale_degree
                    parsed_settings[i][3]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][3]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][3]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][3]["smoothing"] = section_settings_l[i].smoothing_do_scale
                    parsed_settings[i][3]["degree"] = section_settings_l[i].smoothing_scale_degree
                    parsed_settings[i][3]["regressor"] = section_settings_l[i].smoothing_scale_regressor
                    parsed_settings[i][3]["huber_epsilon"] = section_settings_l[i].smoothing_scale_huber_epsilon
                    parsed_settings[i][3]["lasso_alpha"] = section_settings_l[i].smoothing_scale_lasso_alpha
                case 0b10:

                    parsed_settings[i][3]["smoothing"] = section_settings_l[i].smoothing_do_scale_y
                    parsed_settings[i][3]["degree"] = section_settings_l[i].smoothing_scale_y_degree
                    parsed_settings[i][3]["regressor"] = section_settings_l[i].smoothing_y_regressor
                    parsed_settings[i][3]["huber_epsilon"] = section_settings_l[i].smoothing_y_huber_epsilon
                    parsed_settings[i][3]["lasso_alpha"] = section_settings_l[i].smoothing_y_lasso_alpha

                case 0b11:

                    parsed_settings[i][3]["smoothing"] = section_settings_l[i].smoothing_do_scale_y
                    parsed_settings[i][3]["degree"] = section_settings_l[i].smoothing_scale_y_degree
                    parsed_settings[i][3]["regressor"] = section_settings_l[i].smoothing_scale_y_regressor
                    parsed_settings[i][3]["huber_epsilon"] = section_settings_l[i].smoothing_scale_y_huber_epsilon
                    parsed_settings[i][3]["lasso_alpha"] = section_settings_l[i].smoothing_scale_y_lasso_alpha


  

  

            parsed_settings[i][4] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][4]["smoothing"] = section_settings_l[i].smoothing_do_rotation
                    parsed_settings[i][4]["degree"] = section_settings_l[i].smoothing_rotation_degree
                    parsed_settings[i][4]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][4]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][4]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][4]["smoothing"] = section_settings_l[i].smoothing_do_rotation
                    parsed_settings[i][4]["degree"] = section_settings_l[i].smoothing_rotation_degree
                    parsed_settings[i][4]["regressor"] = section_settings_l[i].smoothing_rotation_regressor
                    parsed_settings[i][4]["huber_epsilon"] = section_settings_l[i].smoothing_rotation_huber_epsilon
                    parsed_settings[i][4]["lasso_alpha"] = section_settings_l[i].smoothing_rotation_lasso_alpha
                case 0b10:

                    parsed_settings[i][4]["smoothing"] = section_settings_l[i].smoothing_do_rotation
                    parsed_settings[i][4]["degree"] = section_settings_l[i].smoothing_rotation_degree
                    parsed_settings[i][4]["regressor"] = section_settings_l[i].smoothing_x_regressor
                    parsed_settings[i][4]["huber_epsilon"] = section_settings_l[i].smoothing_x_huber_epsilon
                    parsed_settings[i][4]["lasso_alpha"] = section_settings_l[i].smoothing_x_lasso_alpha

                case 0b11:

                    parsed_settings[i][4]["smoothing"] = section_settings_l[i].smoothing_do_rotation
                    parsed_settings[i][4]["degree"] = section_settings_l[i].smoothing_rotation_degree
                    parsed_settings[i][4]["regressor"] = section_settings_l[i].smoothing_rotation_regressor
                    parsed_settings[i][4]["huber_epsilon"] = section_settings_l[i].smoothing_rotation_huber_epsilon
                    parsed_settings[i][4]["lasso_alpha"] = section_settings_l[i].smoothing_rotation_lasso_alpha


  

  

            parsed_settings[i][5] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][5]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][5]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][5]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][5]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][5]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][5]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][5]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][5]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][5]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][5]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][5]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][5]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][5]["regressor"] = section_settings_l[i].smoothing_x_regressor
                    parsed_settings[i][5]["huber_epsilon"] = section_settings_l[i].smoothing_x_huber_epsilon
                    parsed_settings[i][5]["lasso_alpha"] = section_settings_l[i].smoothing_x_lasso_alpha

                case 0b11:

                    parsed_settings[i][5]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][5]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][5]["regressor"] = section_settings_l[i].smoothing_power_pin_x_regressor
                    parsed_settings[i][5]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_x_huber_epsilon
                    parsed_settings[i][5]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_x_lasso_alpha


  
  

            parsed_settings[i][6] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][6]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][6]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][6]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][6]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][6]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][6]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][6]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][6]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][6]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][6]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][6]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][6]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][6]["regressor"] = section_settings_l[i].smoothing_y_regressor
                    parsed_settings[i][6]["huber_epsilon"] = section_settings_l[i].smoothing_y_huber_epsilon
                    parsed_settings[i][6]["lasso_alpha"] = section_settings_l[i].smoothing_y_lasso_alpha

                case 0b11:

                    parsed_settings[i][6]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][6]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][6]["regressor"] = section_settings_l[i].smoothing_power_pin_y_regressor
                    parsed_settings[i][6]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_y_huber_epsilon
                    parsed_settings[i][6]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_y_lasso_alpha


  
  

            parsed_settings[i][7] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][7]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][7]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][7]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][7]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][7]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][7]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][7]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][7]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][7]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][7]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][7]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][7]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][7]["regressor"] = section_settings_l[i].smoothing_x_regressor
                    parsed_settings[i][7]["huber_epsilon"] = section_settings_l[i].smoothing_x_huber_epsilon
                    parsed_settings[i][7]["lasso_alpha"] = section_settings_l[i].smoothing_x_lasso_alpha

                case 0b11:

                    parsed_settings[i][7]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][7]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][7]["regressor"] = section_settings_l[i].smoothing_power_pin_x_regressor
                    parsed_settings[i][7]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_x_huber_epsilon
                    parsed_settings[i][7]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_x_lasso_alpha


  
  

            parsed_settings[i][8] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][8]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][8]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][8]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][8]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][8]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][8]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][8]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][8]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][8]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][8]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][8]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][8]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][8]["regressor"] = section_settings_l[i].smoothing_y_regressor
                    parsed_settings[i][8]["huber_epsilon"] = section_settings_l[i].smoothing_y_huber_epsilon
                    parsed_settings[i][8]["lasso_alpha"] = section_settings_l[i].smoothing_y_lasso_alpha

                case 0b11:

                    parsed_settings[i][8]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][8]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][8]["regressor"] = section_settings_l[i].smoothing_power_pin_y_regressor
                    parsed_settings[i][8]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_y_huber_epsilon
                    parsed_settings[i][8]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_y_lasso_alpha


  
  

            parsed_settings[i][9] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][9]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][9]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][9]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][9]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][9]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][9]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][9]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][9]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][9]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][9]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][9]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][9]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][9]["regressor"] = section_settings_l[i].smoothing_x_regressor
                    parsed_settings[i][9]["huber_epsilon"] = section_settings_l[i].smoothing_x_huber_epsilon
                    parsed_settings[i][9]["lasso_alpha"] = section_settings_l[i].smoothing_x_lasso_alpha

                case 0b11:

                    parsed_settings[i][9]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][9]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][9]["regressor"] = section_settings_l[i].smoothing_power_pin_x_regressor
                    parsed_settings[i][9]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_x_huber_epsilon
                    parsed_settings[i][9]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_x_lasso_alpha


  
  

            parsed_settings[i][10] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][10]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][10]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][10]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][10]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][10]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][10]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][10]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][10]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][10]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][10]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][10]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][10]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][10]["regressor"] = section_settings_l[i].smoothing_y_regressor
                    parsed_settings[i][10]["huber_epsilon"] = section_settings_l[i].smoothing_y_huber_epsilon
                    parsed_settings[i][10]["lasso_alpha"] = section_settings_l[i].smoothing_y_lasso_alpha

                case 0b11:

                    parsed_settings[i][10]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][10]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][10]["regressor"] = section_settings_l[i].smoothing_power_pin_y_regressor
                    parsed_settings[i][10]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_y_huber_epsilon
                    parsed_settings[i][10]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_y_lasso_alpha


  
  

            parsed_settings[i][11] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][11]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][11]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][11]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][11]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][11]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][11]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][11]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][11]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][11]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][11]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][11]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][11]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][11]["regressor"] = section_settings_l[i].smoothing_x_regressor
                    parsed_settings[i][11]["huber_epsilon"] = section_settings_l[i].smoothing_x_huber_epsilon
                    parsed_settings[i][11]["lasso_alpha"] = section_settings_l[i].smoothing_x_lasso_alpha

                case 0b11:

                    parsed_settings[i][11]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_x
                    parsed_settings[i][11]["degree"] = section_settings_l[i].smoothing_power_pin_x_degree
                    parsed_settings[i][11]["regressor"] = section_settings_l[i].smoothing_power_pin_x_regressor
                    parsed_settings[i][11]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_x_huber_epsilon
                    parsed_settings[i][11]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_x_lasso_alpha


  
  

            parsed_settings[i][12] = {}

            match (section_settings_l[i].smoothing_use_different_x_y * 2) + section_settings_l[i].smoothing_use_different_model:
                case 0b00:
                    parsed_settings[i][12]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][12]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][12]["regressor"] = section_settings_l[i].smoothing_regressor
                    parsed_settings[i][12]["huber_epsilon"] = section_settings_l[i].smoothing_huber_epsilon
                    parsed_settings[i][12]["lasso_alpha"] = section_settings_l[i].smoothing_lasso_alpha
                case 0b01:
                    parsed_settings[i][12]["smoothing"] = section_settings_l[i].smoothing_do_power_pin
                    parsed_settings[i][12]["degree"] = section_settings_l[i].smoothing_power_pin_degree
                    parsed_settings[i][12]["regressor"] = section_settings_l[i].smoothing_power_pin_regressor
                    parsed_settings[i][12]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_huber_epsilon
                    parsed_settings[i][12]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_lasso_alpha
                case 0b10:

                    parsed_settings[i][12]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][12]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][12]["regressor"] = section_settings_l[i].smoothing_y_regressor
                    parsed_settings[i][12]["huber_epsilon"] = section_settings_l[i].smoothing_y_huber_epsilon
                    parsed_settings[i][12]["lasso_alpha"] = section_settings_l[i].smoothing_y_lasso_alpha

                case 0b11:

                    parsed_settings[i][12]["smoothing"] = section_settings_l[i].smoothing_do_power_pin_y
                    parsed_settings[i][12]["degree"] = section_settings_l[i].smoothing_power_pin_y_degree
                    parsed_settings[i][12]["regressor"] = section_settings_l[i].smoothing_power_pin_y_regressor
                    parsed_settings[i][12]["huber_epsilon"] = section_settings_l[i].smoothing_power_pin_y_huber_epsilon
                    parsed_settings[i][12]["lasso_alpha"] = section_settings_l[i].smoothing_power_pin_y_lasso_alpha


  



        return parsed_settings

    @staticmethod
    def _smoothing_main(data, clip, clip_settings, section_settings, section_settings_ll, plotting=False):
        """
        The main logic for smoothing.

        Parameters
        ----------
        data : dict[npt.NDArray[float64]]
        clip : bpy.types.MovieClip
        clip_settings : AAEExportSettingsClip
            AAEExportSettingsClip.
        section_settings : dict[dict[dict[]]]
        section_settings_ll : bpy.props.IntProperty
            AAEExportSettingsSectionLL.

        Returns
        -------
        smoothed_data : dict[npt.NDArray[float64]]

        """
        import collections
        import numpy as np

        smoothed_data = {}
        if plotting:
            no_blending_data = {}

        for i in range(13):
            smoothed_data[i] \
                = np.zeros_like(data[i])
            if plotting:
                no_blending_data[i] \
                    = np.zeros_like(data[i])
            carryover \
                = np.full((2), np.nan, dtype=np.float64)
            if plotting:
                no_blending_carryover \
                    = np.full((1), np.nan, dtype=np.float64)

            for j in range(section_settings_ll):
                match (section_settings[j]["disable_section"] * 4) + (section_settings[j][i]["smoothing"] * 2) + section_settings[j]["smoothing_extrapolate"]:
                    case 0b011:
                        returned_data \
                            = AAEExportExportAll._smoothing( \
                                  data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]], \
                                  section_settings[j][i])
                    case 0b010:
                        returned_data \
                            = AAEExportExportAll._smoothing( \
                                  data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]], \
                                  section_settings[j][i])
                        returned_data[np.isnan(data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]])] \
                            = np.nan
                    case 0b001:
                        returned_data \
                            = AAEExportExportAll._smoothing( \
                                  data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]], \
                                  section_settings[j][i])
                        returned_data[indices] \
                            = data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]][(indices := ~np.isnan(data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]]))]
                    case 0b000:
                        returned_data \
                            = data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]]
                    case 0b100 | 0b101 | 0b110 | 0b111:
                        returned_data \
                            = np.full_like(data[i][section_settings[j]["start_frame"]:section_settings[j]["end_frame"]], np.nan)

                AAEExportExportAll._smoothing_append_section( \
                    smoothed_data[i], returned_data, \
                    clip, clip_settings, section_settings[j], \
                    carryover)
                if plotting:
                    AAEExportExportAll._smoothing_append_section( \
                        no_blending_data[i], returned_data, \
                        clip, collections.namedtuple("FakeAAEExportSettingsClip", ["smoothing_blending"])("NONE"), section_settings[j], \
                        no_blending_carryover)

        if not plotting:
            return smoothed_data
        else:
            return smoothed_data, no_blending_data

    @staticmethod
    def _smoothing(data, section_settings):
        """
        Perform smoothing depending on the smoothing settings.

        Parameters
        ----------
        data : npt.NDArray[float64]
            univariate data
        section_settings : dict[]
            Parsed settings for the section and data

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

        if X.shape[0] == 0:
            return np.copy(data)
        elif section_settings["degree"] == 0:
            return np.full_like(data, np.average(data[~np.isnan(data)]))
        elif section_settings["regressor"] == "HUBER":
            return Pipeline([("poly", PolynomialFeatures(degree=section_settings["degree"])), \
                             ("huber", HuberRegressor(epsilon=section_settings["huber_epsilon"]))]) \
                       .fit(X, y) \
                       .predict(np.arange(data.shape[0]).reshape(-1, 1))
        elif section_settings["regressor"] == "LASSO":
            return Pipeline([("poly", PolynomialFeatures(degree=section_settings["degree"])), \
                             ("lasso", Lasso(alpha=section_settings["lasso_alpha"]))]) \
                       .fit(X, y) \
                       .predict(np.arange(data.shape[0]).reshape(-1, 1))
        elif section_settings["regressor"] == "LINEAR":
            return Pipeline([("poly", PolynomialFeatures(degree=section_settings["degree"])), \
                             ("regressor", LinearRegression())]) \
                       .fit(X, y) \
                       .predict(np.arange(data.shape[0]).reshape(-1, 1))
        else:
            raise ValueError("regressor " + section_settings["regressor"] + " not recognised")

    @staticmethod
    def _smoothing_append_section(smoothed_data, data, clip, clip_settings, section_settings, carryover):
        """
        The main logic for smoothing.

        Parameters
        ----------
        smoothed_data : npt.NDArray[float64]
            smoothed_data created in _smoothing_main()
        data : npt.NDArray[float64]
            data after smoothed in _smoothing_main()
        clip : bpy.types.MovieClip
        clip_settings : AAEExportSettingsClip
        section_settings : dict[dict[]]
            Parsed settings for the section
        carryover : npt.NDArray[float64]
            Carryover. Initialised in _smoothing_main()

        """
        import numpy as np

        match clip_settings.smoothing_blending:
            case "NONE":
                match (np.isnan(carryover[0]) * 2) + np.isnan(data[0]):
                    case 0b00:
                        smoothed_data[section_settings["start_frame"]] = (smoothed_data[section_settings["start_frame"]] + data[0]) / 2
                        smoothed_data[section_settings["start_frame"]+1:section_settings["end_frame"]] = data[1:]
                    case 0b10:
                        smoothed_data[section_settings["start_frame"]:section_settings["end_frame"]] = data
                    case 0b01 | 0b11:
                        smoothed_data[section_settings["start_frame"]+1:section_settings["end_frame"]] = data[1:]
                carryover[0] = data[-1]

            case "CUBIC":
                smoothed_data[section_settings["start_frame"]+1:section_settings["end_frame"]] = smoothed_data[section_settings["start_frame"]+1:section_settings["end_frame"]] + data[1:]
                match (np.isnan(carryover[0]) * 2) + np.isnan(data[0]):
                    case 0b00:
                        t = np.arange(-(l := min(section_settings["start_frame"], int(clip_settings.smoothing_blending_cubic_range))),
                                      (h := min(clip.frame_duration - section_settings["start_frame"] - 1, int(clip_settings.smoothing_blending_cubic_range))) + 1, dtype=np.float64)
                        t = 0.5 / clip_settings.smoothing_blending_cubic_range * t + 0.5
                        t = 3 * np.power(1-t, 2) * t * clip_settings.smoothing_blending_cubic_p1 + \
                            3 * (1-t) * np.power(t, 2) * clip_settings.smoothing_blending_cubic_p2 + \
                            np.power(t, 3)
                        t[:l+1] = t[:l+1] * (data[0] - carryover[0])
                        t[l+1:] = -(1 - t[l+1:]) * (data[0] - carryover[0])

                        smoothed_data[section_settings["start_frame"]-l:section_settings["start_frame"]+h+1] = smoothed_data[section_settings["start_frame"]-l:section_settings["start_frame"]+h+1] + t
                    case 0b10 | 0b11:
                        smoothed_data[section_settings["start_frame"]] = data[0]
                    case 0b01:
                        pass

                carryover[0] = data[-1]

            case "SHIFT":
                match (np.isnan(carryover[0]) * 4) + (np.isnan(smoothed_data[section_settings["start_frame"]]) * 2) + np.isnan(data[0]):
                    case 0b100 | 0b101:
                        smoothed_data[section_settings["start_frame"]:section_settings["end_frame"]] = data
                        carryover[0] = 0
                        carryover[1] = 0
                    case 0b000:
                        carryover[1] = data[0] - smoothed_data[section_settings["start_frame"]]
                        smoothed_data[section_settings["start_frame"]+1:section_settings["end_frame"]] = data[1:] - carryover[1]
                        carryover[0] = carryover[0] + carryover[1] * np.count_nonzero(~np.isnan(data[1:]))
                    case 0b010:
                        smoothed_data[section_settings["start_frame"]:section_settings["end_frame"]] = data - carryover[1]
                        carryover[0] = carryover[0] + carryover[1] * np.count_nonzero(~np.isnan(data))
                    case 0b001 | 0b011:
                        smoothed_data[section_settings["start_frame"]+1:section_settings["end_frame"]] = data[1:] - carryover[1]
                        carryover[0] = carryover[0] + carryover[1] * np.count_nonzero(~np.isnan(data[1:]))
                    case 0b110 | 0b111:
                        raise ValueError("carryover[0] is NaN but smoothed_data[section_settings[\"start_frame\"]] is also NaN")

                if section_settings["end_frame"] == clip.frame_duration:
                    np.add(smoothed_data, carryover[0] / np.count_nonzero(~np.isnan(smoothed_data)), out=smoothed_data)

    @staticmethod
    def _generate_aae(data, multiplier):
        """
        Finalised and stringify the data.

        Parameters
        ----------
        data : data : dict[npt.NDArray[float64]]
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

        data[0] *= multiplier
        data[1] *= multiplier
        data[2] *= 100
        data[3] *= 100
        data[4] = np.degrees(data[4])
        data[4][data[4] >= 359.9995] = 0.0
        data[5] *= multiplier
        data[5] += data[0]
        data[6] *= multiplier
        data[6] += data[1]
        data[7] *= multiplier
        data[7] += data[0]
        data[8] *= multiplier
        data[8] += data[1]
        data[9] *= multiplier
        data[9] += data[0]
        data[10] *= multiplier
        data[10] += data[1]
        data[11] *= multiplier
        data[11] += data[0]
        data[12] *= multiplier
        data[12] += data[1]

        aae_position = []
        aae_scale = []
        aae_rotation = []
        aae_power_pin_0002 = []
        aae_power_pin_0003 = []
        aae_power_pin_0004 = []
        aae_power_pin_0005 = []
        aae_frz_fax = []

        for frame in range(data[0].shape[0]):
            if not np.isnan(data[0][frame]):
                aae_position.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(frame + 1, data[0][frame], data[1][frame], 0.0))
            if not np.isnan(data[2][frame]):
                aae_scale.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(frame + 1, data[2][frame], data[3][frame], 100.0))
            if not np.isnan(data[4][frame]):
                aae_rotation.append("\t{:d}\t{:.3f}".format(frame + 1, data[4][frame]))
            if not np.isnan(data[5][frame]):
                aae_power_pin_0002.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, data[5][frame], data[6][frame]))
                aae_power_pin_0003.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, data[7][frame], data[8][frame]))
                aae_power_pin_0004.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, data[9][frame], data[10][frame]))
                aae_power_pin_0005.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, data[11][frame], data[12][frame]))
            if not np.isnan(data[13][frame]):
                aae_frz_fax.append("\t{:d}\t{:f}\t{:f}".format(frame + 1, data[13][frame], data[14][frame]))

        return aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, aae_frz_fax
        
    @staticmethod
    def _plot_result_plot(data, smoothed_data, no_blending_data, clip_settings):
        """
        Plot the data.

        Parameters
        ----------
        data : list[npt.NDArray[float64]]
        smoothed_data : list[npt.NDArray[float64]]
        no_blending_data : list[npt.NDArray[float64] or None]
        clip_settings : AAEExportSettingsClip

        """
        import matplotlib.pyplot as plt
        import numpy as np
        import PIL
        import re







        def plot_x_y(axs, y, x, i, j, label, power_pin_remapped=False):
            axs[y, x].invert_yaxis()
            axs[y, x].scatter(data[i], data[j], color="lightgrey", marker=".", s=0.7, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if no_blending_data[i] is not None:
                axs[y, x].plot(no_blending_data[i], no_blending_data[j], color="wheat", lw=1.0, label="_".join(["no_blending"] + re.split(" |_", label.lower())), zorder=2.002)
            axs[y, x].plot(smoothed_data[i], smoothed_data[j], color="orange", lw=1.4, label="_".join(["result"] + re.split(" |_", label.lower())), zorder=2.003)
            axs[y, x].legend()
            axs[y, x].set_xlabel("X")
            axs[y, x].set_ylabel("Y")

            axs[y, x + 1].scatter(np.arange(1, data[i].shape[0] + 1), data[i], color="lightgrey", s=0.7, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if no_blending_data[i] is not None:
                axs[y, x + 1].plot(np.arange(1, data[i].shape[0] + 1), no_blending_data[i], color="wheat", lw=1.0, label="_".join(["no_blending"] + re.split(" |_", label.lower())), zorder=2.002)
            axs[y, x + 1].plot(np.arange(1, data[i].shape[0] + 1), smoothed_data[i], color="orange", lw=1.4, label="_".join(["result"] + re.split(" |_", label.lower())), zorder=2.003)
            axs[y, x + 1].legend()
            axs[y, x + 1].set_xlabel("Frame")
            axs[y, x + 1].set_ylabel(" ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " X" + (" (Remapped)" if power_pin_remapped else ""))

            axs[y, x + 2].scatter(np.arange(1, data[i].shape[0] + 1), data[j], color="lightgrey", s=0.7, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if no_blending_data[i] is not None:
                axs[y, x + 2].plot(np.arange(1, data[i].shape[0] + 1), no_blending_data[j], color="wheat", lw=1.0, label="_".join(["no_blending"] + re.split(" |_", label.lower())), zorder=2.002)
            axs[y, x + 2].plot(np.arange(1, data[i].shape[0] + 1), smoothed_data[j], color="orange", lw=1.4, label="_".join(["result"] + re.split(" |_", label.lower())), zorder=2.003)
            axs[y, x + 2].legend()
            axs[y, x + 2].set_xlabel("Frame")
            axs[y, x + 2].set_ylabel(" ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " Y" + (" (Remapped)" if power_pin_remapped else ""))
        
        def plot_univariate(axs, y, x, i, label):
            axs[y, x].axis("off")
            
            axs[y, x + 1].scatter(np.arange(1, data[i].shape[0] + 1), data[i], color="lightgrey", s=0.7, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if no_blending_data[i] is not None:
                axs[y, x + 1].plot(np.arange(1, data[i].shape[0] + 1), no_blending_data[i], color="wheat", lw=1.0, label="_".join(["no_blending"] + re.split(" |_", label.lower())), zorder=2.002)
            axs[y, x + 1].plot(np.arange(1, data[i].shape[0] + 1), smoothed_data[i], color="orange", lw=1.4, label="_".join(["result"] + re.split(" |_", label.lower())), zorder=2.003)
            axs[y, x + 1].legend()
            axs[y, x + 1].set_xlabel("Frame")
            axs[y, x + 1].set_ylabel(label.title())

            axs[y, x + 2].axis("off")

        def plot_emptyness(axs, y, x):
            axs[y, x].axis("off")
            axs[y, x + 1].axis("off")
            axs[y, x + 2].axis("off")






        
        fig, axs = plt.subplots(ncols=6, nrows=4, figsize=(6 * 5.4, 4 * 4.05), dpi=250, layout="constrained")
        plot_x_y(axs, 0, 0, 0, 1, "position")
        plot_x_y(axs, 0, 3, 2, 3, "scale")
        plot_univariate(axs, 1, 0, 4, "rotation")
        plot_emptyness(axs, 1, 3)
        plot_x_y(axs, 2, 0, 5, 6, "power_pin_" + clip_settings.power_pin_remap_0002, clip_settings.power_pin_remap_0002 != "0002")
        plot_x_y(axs, 2, 3, 7, 8, "power_pin_" + clip_settings.power_pin_remap_0003, clip_settings.power_pin_remap_0003 != "0003")
        plot_x_y(axs, 3, 0, 9, 10, "power_pin_" + clip_settings.power_pin_remap_0004, clip_settings.power_pin_remap_0004 != "0004")
        plot_x_y(axs, 3, 3, 11, 12, "power_pin_" + clip_settings.power_pin_remap_0005, clip_settings.power_pin_remap_0005 != "0005")

        fig.canvas.draw()
        with PIL.Image.frombytes("RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb()) as im:
            im.show()
        plt.close(fig)

    @staticmethod
    def _plot_section_plot(data, smoothed_data, section_settings):
        """
        Plot the data.

        Parameters
        ----------
        data : list[npt.NDArray[float64]]
        smoothed_data : list[npt.NDArray[float64] or None]
        section_settings :  AAEExportSettingsSectionL
            AAEExportSettingsSectionL[AAEExportSettingsSectionLI]
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import PIL
        import re








        def plot_x_y(row, i, j, label):
            def test_z_score(data):
                # Iglewicz and Hoaglin's modified Z-score
                return np.nonzero(0.6745 * (d := np.absolute(data - np.median(data))) / np.median(d) >= 3)[0]

            row[0].invert_yaxis()
            row[0].scatter(data[i], data[j], marker="+", color="lightslategrey", s=7.3, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if smoothed_data[i] is not None or smoothed_data[j] is not None:
                row[0].plot(smoothed_data[i] if smoothed_data[i] is not None else data[i], smoothed_data[j] if smoothed_data[j] is not None else data[j], color="dodgerblue", lw=1.0, label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[0].legend()
            row[0].set_xlabel("X")
            row[0].set_ylabel("Y")

            row[1].scatter((frames := np.arange(section_settings["start_frame"], section_settings["end_frame"])), data[i], marker="+", color="lightslategrey", s=7.3, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if smoothed_data[i] is not None:
                row[1].plot(frames, smoothed_data[i], color="dodgerblue", lw=1.0, label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[1].legend()
            row[1].set_xlabel("Frame")
            row[1].set_ylabel(" ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " X")

            if smoothed_data[i] is not None:
                row[2].plot(frames, np.zeros_like(data[i]), color="lightslategrey", lw=0.9, label="_".join(re.split(" |_", label.lower())), zorder=2.002)
                row[2].plot(frames, (p := data[i] - smoothed_data[i]), color="dodgerblue", lw=1.4, label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.001)
                for i in test_z_score(p):
                    row[2].annotate(i + section_settings["start_frame"], (i + section_settings["start_frame"], p[i]))
                row[2].legend()
                row[2].set_xlabel("Frame")
                row[2].set_ylabel("Residual of " + " ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " X")
            else:
                row[2].axis("off")

            row[3].scatter(frames, data[j], marker="+", color="lightslategrey", s=7.3, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if smoothed_data[j] is not None:
                row[3].plot(frames, smoothed_data[j], color="dodgerblue", lw=1.0, label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[3].legend()
            row[3].set_xlabel("Frame")
            row[3].set_ylabel(" ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " Y")

            if smoothed_data[j] is not None:
                row[4].plot(frames, np.zeros_like(data[j]), color="lightslategrey", lw=0.9, label="_".join(re.split(" |_", label.lower())), zorder=2.002)
                row[4].plot(frames, (p := data[j] - smoothed_data[j]), color="dodgerblue", lw=1.4, label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.001)
                for i in test_z_score(p):
                    row[4].annotate(i + section_settings["start_frame"], (i + section_settings["start_frame"], p[i]))
                row[4].legend()
                row[4].set_xlabel("Frame")
                row[4].set_ylabel("Residual of " + " ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " Y")
            else:
                row[4].axis("off")
        
        def plot_univariate(row, i, label):
            row[0].axis("off")
            
            row[1].scatter((frames := np.arange(section_settings["start_frame"], section_settings["end_frame"])), data[i], marker="+", color="lightslategrey", s=7.3, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if smoothed_data[i] is not None:
                row[1].plot(frames, smoothed_data[i], color="dodgerblue", lw=1.0, label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[1].legend()
            row[1].set_xlabel("Frame")
            row[1].set_ylabel(label.title())

            if smoothed_data[i] is not None:
                row[2].plot(frames, np.zeros_like(data[i]), color="lightslategrey", lw=0.9, label="_".join(re.split(" |_", label.lower())), zorder=2.002)
                row[2].plot(frames, data[i] - smoothed_data[i], color="dodgerblue", lw=1.4, label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.001)
                row[2].legend()
                row[2].set_xlabel("Frame")
                row[2].set_ylabel("Residual of " + " ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))))
            else:
                row[2].axis("off")
            
            row[3].axis("off")
            row[4].axis("off")







        
        fig, axs = plt.subplots(ncols=5, nrows=7, figsize=(5 * 5.4, 7 * 4.05), dpi=250, layout="constrained")
        plot_x_y(axs[0], 0, 1, "position")
        plot_x_y(axs[1], 2, 3, "scale")
        plot_univariate(axs[2], 4, "rotation")
        plot_x_y(axs[3], 5, 6, "power_pin_0002")
        plot_x_y(axs[4], 7, 8, "power_pin_0003")
        plot_x_y(axs[5], 9, 10, "power_pin_0004")
        plot_x_y(axs[6], 11, 12, "power_pin_0005")

        fig.canvas.draw()
        with PIL.Image.frombytes("RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb()) as im:
            im.show()
        plt.close(fig)

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
            for marker in track.markers:
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
                    (1 - float(marker.co[1])) * clip.size[1])

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
            scale = (scale[0] / scale_base[0] * 100, scale[1] / scale_base[1] * 100)

        rotation = math.atan2((power_pin_0002[0] + power_pin_0003[0]) / 2 - position[0],
                              -((power_pin_0002[1] + power_pin_0003[1]) / 2 - position[1])) % (2 * math.pi) * 180 / math.pi

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
        # LU decomposition thanks to arch1t3cht
        def calculate_coef_(a, b):
            return ((a[1] - b[1], b[0] - a[0]), b[0] * a[1] - a[0] * b[1])
        def caluclate_solution_(A, b):
            det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
            if det == 0:
                return None
            else:
                return ((A[1][1] * b[0][0] - A[0][1] * b[1][0]) / det, (A[0][0] * b[1][0] - A[1][0] * b[0][0]) / det)
        
        coef_a = calculate_coef_(power_pin_0002, power_pin_0005)
        coef_b = calculate_coef_(power_pin_0003, power_pin_0004)
        result = caluclate_solution_((coef_a[0], coef_b[0]), ((coef_a[1],), (coef_b[1],)))

        if result:
            return result
        else:
            return ((power_pin_0002[0] + power_pin_0003[0] + power_pin_0004[0] + power_pin_0005[0]) / 4, \
                    (power_pin_0002[1] + power_pin_0003[1] + power_pin_0004[1] + power_pin_0005[1]) / 4)

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
        if rotation >= 359.9995:
            rotation = 0.0
        aae_rotation.append("\t{:d}\t{:.3f}".format(marker.frame, rotation))
        aae_power_pin_0002.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0002))
        aae_power_pin_0003.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0003))
        aae_power_pin_0004.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0004))
        aae_power_pin_0005.append("\t{:d}\t{:.3f}\t{:.3f}".format(marker.frame, *power_pin_0005))

    @staticmethod
    def _remap_power_pin(power_pin_0002, power_pin_0003, power_pin_0004, power_pin_0005, power_pin_remap_0002, power_pin_remap_0003, power_pin_remap_0004, power_pin_remap_0005):
        """
        Remap Power Pin
        
        Parameters
        ----------
        power_pin_0002 : object
        power_pin_0003 : object
        power_pin_0004 : object
        power_pin_0005 : object
        power_pin_remap_0002 : str
        power_pin_remap_0003 : str
        power_pin_remap_0004 : str
        power_pin_remap_0005 : str

        Returns
        -------
        return_0002 : object
        return_0003 : object
        return_0004 : object
        return_0005 : object

        """



        match power_pin_remap_0002:
            case "0002":
                return_0002 = power_pin_0002
            case "0003":
                return_0002 = power_pin_0003
            case "0004":
                return_0002 = power_pin_0004
            case "0005":
                return_0002 = power_pin_0005




        match power_pin_remap_0003:
            case "0002":
                return_0003 = power_pin_0002
            case "0003":
                return_0003 = power_pin_0003
            case "0004":
                return_0003 = power_pin_0004
            case "0005":
                return_0003 = power_pin_0005




        match power_pin_remap_0004:
            case "0002":
                return_0004 = power_pin_0002
            case "0003":
                return_0004 = power_pin_0003
            case "0004":
                return_0004 = power_pin_0004
            case "0005":
                return_0004 = power_pin_0005




        match power_pin_remap_0005:
            case "0002":
                return_0005 = power_pin_0002
            case "0003":
                return_0005 = power_pin_0003
            case "0004":
                return_0005 = power_pin_0004
            case "0005":
                return_0005 = power_pin_0005



        return return_0002, return_0003, return_0004, return_0005

    @staticmethod
    def _combine_aae(clip, aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005, aae_frz_fax, do_includes_power_pin):
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

        if aae_frz_fax is not None:
            aae += "Orthographic-Motion Data\n"
            aae += "\tFrame\tX radians\tY radians\n"
            aae += "\n".join(aae_frz_fax) + "\n\n"

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
        from datetime import datetime
        from pathlib import Path

        coords = None
        if track.markers[0].__class__.__name__ == "MovieTrackingMarker":
            for marker in track.markers:
                if not marker.mute:
                    coords = (marker.co[0] * clip.size[0], (1 - marker.co[1]) * clip.size[1])
                    break
        else: # "MovieTrackingPlaneMarker"
            for marker in track.markers:
                if not marker.mute:
                    coords = AAEExportExportAll._calculate_centre_plane_track_per_frame_non_numpy(marker.corners[3], marker.corners[2], marker.corners[0], marker.corners[1])
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
        clip_settings = context.edit_movieclip.AAEExportSettingsClip
        section_settings_l = context.edit_movieclip.AAEExportSettingsSectionL
        section_settings_ll = context.edit_movieclip.AAEExportSettingsSectionLL

        aae = AAEExportExportAll._generate(clip, context.selected_movieclip_tracks[0], settings, clip_settings, section_settings_l, section_settings_ll)
        
        AAEExportExportAll._copy_to_clipboard(context, aae)
        if settings.do_also_export:
            AAEExportExportAll._export_to_file(clip, context.selected_movieclip_tracks[0], aae, None, settings.do_do_not_overwrite)
        
        return { "FINISHED" }

class AAEExportCopyPlaneTrack(bpy.types.Operator):
    bl_label = "Copy"
    bl_description = "Copy selected plane track as AAE data to clipboard"
    bl_idname = "movieclip.aae_export_copy_plane_track"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings
        clip_settings = context.edit_movieclip.AAEExportSettingsClip
        section_settings_l = context.edit_movieclip.AAEExportSettingsSectionL
        section_settings_ll = context.edit_movieclip.AAEExportSettingsSectionLL

        aae = None
        for plane_track in context.edit_movieclip.tracking.plane_tracks:
            if plane_track.select == True:
                aae = AAEExportExportAll._generate(clip, plane_track, settings, clip_settings, section_settings_l, section_settings_ll)
                break

        AAEExportExportAll._copy_to_clipboard(context, aae)
        if settings.do_also_export:
            AAEExportExportAll._export_to_file(clip, clip.tracking.plane_tracks[0], aae, None, settings.do_do_not_overwrite)
        
        return { "FINISHED" }

class AAEExportPlotResult(bpy.types.Operator):
    bl_label = "Plot Result"
    bl_description = "Plot the result data on graph"
    bl_idname = "movieclip.aae_export_plot_result"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings
        clip_settings = context.edit_movieclip.AAEExportSettingsClip
        section_settings_l = context.edit_movieclip.AAEExportSettingsSectionL
        section_settings_ll = context.edit_movieclip.AAEExportSettingsSectionLL

        if context.selected_movieclip_tracks.__len__() == 1:
            AAEExportExportAll._plot_result(clip, context.selected_movieclip_tracks[0], settings, clip_settings, section_settings_l, section_settings_ll)
        else:
            for plane_track in context.edit_movieclip.tracking.plane_tracks:
                if plane_track.select == True:
                    AAEExportExportAll._plot_result(clip, plane_track, settings, clip_settings, section_settings_l, section_settings_ll)
                    break

        return { "FINISHED" }

class AAEExportPlotSection(bpy.types.Operator):
    bl_label = "Plot Section"
    bl_description = "Plot data and smoothed data for the section on graph"
    bl_idname = "movieclip.aae_export_plot_section"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings
        clip_settings = context.edit_movieclip.AAEExportSettingsClip
        section_settings_l = context.edit_movieclip.AAEExportSettingsSectionL
        section_settings_li = context.edit_movieclip.AAEExportSettingsSectionLI
        section_settings_ll = context.edit_movieclip.AAEExportSettingsSectionLL

        if context.selected_movieclip_tracks.__len__() == 1:
            AAEExportExportAll._plot_section(clip, context.selected_movieclip_tracks[0], settings, clip_settings, section_settings_l, section_settings_li, section_settings_ll)
        else:
            for plane_track in context.edit_movieclip.tracking.plane_tracks:
                if plane_track.select == True:
                    AAEExportExportAll._plot_section(clip, plane_track, settings, clip_settings, section_settings_l, section_settings_li, section_settings_ll)
                    break

        return { "FINISHED" }

class AAEExportPlot(bpy.types.Operator):
    bl_label = "Plot"
    bl_description = "Plot data and smoothed data on graph"
    bl_idname = "movieclip.aae_export_plot"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings
        clip_settings = context.edit_movieclip.AAEExportSettingsClip
        section_settings_l = context.edit_movieclip.AAEExportSettingsSectionL

        if context.selected_movieclip_tracks.__len__() == 1:
            AAEExportExportAll._plot_section(clip, context.selected_movieclip_tracks[0], settings, clip_settings, section_settings_l, 0, 1)
        else:
            for plane_track in context.edit_movieclip.tracking.plane_tracks:
                if plane_track.select == True:
                    AAEExportExportAll._plot_section(clip, plane_track, settings, clip_settings, section_settings_l, 0, 1)
                    break

        return { "FINISHED" }

class AAEExport(bpy.types.Panel):
    bl_label = "AAE Export"
    bl_idname = "SOLVE_PT_aae_export"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"

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
        
        column = layout.column()
        column.label(text="Selected track")

        row = layout.row()
        row.scale_y = 2
        row.enabled = context.selected_movieclip_tracks.__len__() == 1
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
        
        column = layout.column()
        column.label(text="All tracks")
        
        row = layout.row()
        row.scale_y = 2
        row.enabled = context.edit_movieclip.tracking.tracks.__len__() >= 1 or \
                      context.edit_movieclip.tracking.plane_tracks.__len__() >= 1
        row.operator("movieclip.aae_export_export_all")

class AAEExportOptions(bpy.types.Panel):
    bl_label = "Export Options"
    bl_idname = "SOLVE_PT_aae_export_options"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"
    bl_parent_id = "SOLVE_PT_aae_export"
    bl_order = 1000
    bl_options = { "DEFAULT_CLOSED" }

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        settings = context.screen.AAEExportSettings
        
        # box = layout.box()
        # column = box.column(heading="Export")
        # column.prop(settings, "do_includes_power_pin")

        box = layout.box()
        column = box.column(heading="Preference")
        column.prop(settings, "do_also_export")
        column.prop(settings, "do_do_not_overwrite")

        box = layout.box()
        if is_smoothing_modules_available:





            clip_settings = context.edit_movieclip.AAEExportSettingsClip
            
            selected_plane_tracks = 0
            for plane_track in context.edit_movieclip.tracking.plane_tracks:
                if plane_track.select == True:
                    selected_plane_tracks += 1

            column = box.column(heading="Smoothing")
            column.prop(clip_settings, "do_smoothing")
            column.separator(factor=0.0)

            if settings.do_advanced_smoothing:
                sub_column = column.column()
                sub_column.enabled = clip_settings.do_smoothing and \
                                     (selected_plane_tracks == 1) is not (context.selected_movieclip_tracks.__len__() == 1)
                sub_column.operator("movieclip.aae_export_plot_result")
                column.separator(factor=0.0)
            else:
                sub_column = column.column()
                sub_column.enabled = clip_settings.do_smoothing and \
                                     (selected_plane_tracks == 1) is not (context.selected_movieclip_tracks.__len__() == 1)
                sub_column.operator("movieclip.aae_export_plot")
                column.separator(factor=0.0)

            if settings.do_advanced_smoothing:
                sub_column = column.column()
                sub_column.enabled = clip_settings.do_smoothing
                sub_column.prop(clip_settings, "smoothing_blending")
                if clip_settings.smoothing_blending == "CUBIC":
                    row = sub_column.row(align=True)
                    row.prop(clip_settings, "smoothing_blending_cubic_p1", text="Controls")
                    row.prop(clip_settings, "smoothing_blending_cubic_p2", text="")
                    sub_column.prop(clip_settings, "smoothing_blending_cubic_range")
                column.separator(factor=0.44)

                row = column.row(align=True)
                row.enabled = clip_settings.do_smoothing
                row.alignment = "CENTER"
                row.label(text="Sections")
                column.separator(factor=0.40)

                sub_column = column.column()
                sub_column.enabled = clip_settings.do_smoothing
                sub_column.template_list("SOLVE_PT_UL_aae_export_section_list", "SOLVE_PT_aae_export_section_vgourp",
                                         context.edit_movieclip, "AAEExportSettingsSectionL",
                                         context.edit_movieclip, "AAEExportSettingsSectionLI",
                                         item_dyntip_propname="frame_update_tooltip",
                                         rows=2, maxrows=6, type="DEFAULT")



            if context.edit_movieclip.AAEExportSettingsSectionLL != 0:
                section_settings = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI]
                if settings.do_advanced_smoothing:
                    row = column.row(align=True)
                    row.enabled = clip_settings.do_smoothing
                    sub_row = row.row(align=True)
                    sub_row.enabled = clip_settings.do_smoothing and \
                                      context.edit_movieclip.AAEExportSettingsSectionLL > 0 and \
                                      ((context.edit_movieclip.AAEExportSettingsSectionLI == context.edit_movieclip.AAEExportSettingsSectionLL - 1 and \
                                        context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame >= 2) or \
                                       (context.edit_movieclip.AAEExportSettingsSectionLI < context.edit_movieclip.AAEExportSettingsSectionLL - 1 and \
                                        (context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame >= 2 or \
                                         context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].start_frame >= 2)))
                    sub_row.operator("movieclip.aae_export_section_add_section")
                    sub_row = row.row(align=True)
                    sub_row.enabled = clip_settings.do_smoothing and \
                                      context.edit_movieclip.AAEExportSettingsSectionLL >= 2
                    sub_row.operator("movieclip.aae_export_section_remove_section")
                    column.separator(factor=0.44)

                    row = column.row()
                    row.enabled = clip_settings.do_smoothing
                    row.alignment = "CENTER"
                    row.label(text="Section Settings")
                    column.separator(factor=0.40)

                    sub_column = column.column()
                    sub_column.enabled = clip_settings.do_smoothing
                    sub_column.prop(section_settings, "start_frame")
                    sub_column.prop(section_settings, "end_frame")
                    column.separator(factor=0.0)

                    sub_column = column.column(align=True)
                    sub_column.enabled = clip_settings.do_smoothing
                    sub_column.prop(section_settings, "disable_section")
                    sub_column.prop(section_settings, "smoothing_extrapolate", text="Extrapolate section")
                    column.separator(factor=0.44)

                    row = column.row(align=True)
                    row.enabled = clip_settings.do_smoothing and not section_settings.disable_section
                    row.alignment = "CENTER"
                    row.label(text="Section Smoothing")
                    column.separator(factor=0.40)

                    row = column.row(heading="Split Settings for", align=True)
                    row.enabled = clip_settings.do_smoothing and not section_settings.disable_section
                    row.prop(section_settings, "smoothing_use_different_x_y")
                    row.prop(section_settings, "smoothing_use_different_model")
                    column.separator(factor=0.0)

                    sub_column = column.column()
                    sub_column.enabled = clip_settings.do_smoothing and not section_settings.disable_section and \
                                         (selected_plane_tracks == 1) is not (context.selected_movieclip_tracks.__len__() == 1)
                    sub_column.operator("movieclip.aae_export_plot_section")
                    column.separator(factor=0.0)










                sub_column = column.column(heading="Position")
                sub_column.enabled = clip_settings.do_smoothing and not section_settings.disable_section

                if section_settings.smoothing_use_different_x_y:
                    row = sub_column.row(align=True)
                    row.prop(section_settings, "smoothing_do_position_x")
                    row.prop(section_settings, "smoothing_do_position_y")
                    if section_settings.smoothing_do_position_x == section_settings.smoothing_do_position_y == True or section_settings.smoothing_extrapolate:
                        row = sub_column.row(align=True)
                        row.prop(section_settings, "smoothing_position_x_degree")
                        row.prop(section_settings, "smoothing_position_y_degree", text="")
                    elif section_settings.smoothing_do_position_x:
                        row = sub_column.row(align=True)
                        row.prop(section_settings, "smoothing_position_x_degree")
                        row.prop(settings, "null_property")
                    elif section_settings.smoothing_do_position_y:
                        row = sub_column.row(align=True)
                        row.prop(settings, "null_property", text="Max Degree")
                        row.prop(section_settings, "smoothing_position_y_degree", text="")
                else:
                    sub_column.prop(section_settings, "smoothing_do_position")
                    if section_settings.smoothing_do_position or section_settings.smoothing_extrapolate:
                        sub_column.prop(section_settings, "smoothing_position_degree")
                if section_settings.smoothing_use_different_model:



                    if section_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               ((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) \
                                or \
                               ((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) \
                               :
                            if \
                               ((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) \
                               :
                                row.prop(section_settings, "smoothing_position_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               ((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) \
                               :
                                row.prop(section_settings, "smoothing_position_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if section_settings.smoothing_position_x_regressor == section_settings.smoothing_position_y_regressor and \
                               ((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) \
                                and \
                               ((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) \
                               :
                                if section_settings.smoothing_position_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_position_x_huber_epsilon")
                                    row.prop(section_settings, "smoothing_position_y_huber_epsilon", text="")
                                elif section_settings.smoothing_position_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_position_x_lasso_alpha")
                                    row.prop(section_settings, "smoothing_position_y_lasso_alpha", text="")
                            else:
                                if section_settings.smoothing_position_x_regressor == "HUBER" and \
                               ((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_position_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif section_settings.smoothing_position_x_regressor == "LASSO" and \
                               ((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_position_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if section_settings.smoothing_position_y_regressor == "HUBER" and \
                               ((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(section_settings, "smoothing_position_y_huber_epsilon", text="")
                                elif section_settings.smoothing_position_y_regressor == "LASSO" and \
                               ((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(section_settings, "smoothing_position_y_lasso_alpha", text="")


                    else:

                        if (section_settings.smoothing_do_position or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_degree != 0:

                            sub_column.prop(section_settings, "smoothing_position_regressor")
                            if section_settings.smoothing_position_regressor == "HUBER":
                                sub_column.prop(section_settings, "smoothing_position_huber_epsilon")
                            elif section_settings.smoothing_position_regressor == "LASSO":
                                sub_column.prop(section_settings, "smoothing_position_lasso_alpha")







                sub_column = column.column(heading="Scale")
                sub_column.enabled = clip_settings.do_smoothing and not section_settings.disable_section

                if section_settings.smoothing_use_different_x_y:
                    row = sub_column.row(align=True)
                    row.prop(section_settings, "smoothing_do_scale_x")
                    row.prop(section_settings, "smoothing_do_scale_y")
                    if section_settings.smoothing_do_scale_x == section_settings.smoothing_do_scale_y == True or section_settings.smoothing_extrapolate:
                        row = sub_column.row(align=True)
                        row.prop(section_settings, "smoothing_scale_x_degree")
                        row.prop(section_settings, "smoothing_scale_y_degree", text="")
                    elif section_settings.smoothing_do_scale_x:
                        row = sub_column.row(align=True)
                        row.prop(section_settings, "smoothing_scale_x_degree")
                        row.prop(settings, "null_property")
                    elif section_settings.smoothing_do_scale_y:
                        row = sub_column.row(align=True)
                        row.prop(settings, "null_property", text="Max Degree")
                        row.prop(section_settings, "smoothing_scale_y_degree", text="")
                else:
                    sub_column.prop(section_settings, "smoothing_do_scale")
                    if section_settings.smoothing_do_scale or section_settings.smoothing_extrapolate:
                        sub_column.prop(section_settings, "smoothing_scale_degree")
                if section_settings.smoothing_use_different_model:



                    if section_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) \
                                or \
                               ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) \
                               :
                            if \
                               ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) \
                               :
                                row.prop(section_settings, "smoothing_scale_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) \
                               :
                                row.prop(section_settings, "smoothing_scale_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if section_settings.smoothing_scale_x_regressor == section_settings.smoothing_scale_y_regressor and \
                               ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) \
                                and \
                               ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) \
                               :
                                if section_settings.smoothing_scale_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_scale_x_huber_epsilon")
                                    row.prop(section_settings, "smoothing_scale_y_huber_epsilon", text="")
                                elif section_settings.smoothing_scale_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_scale_x_lasso_alpha")
                                    row.prop(section_settings, "smoothing_scale_y_lasso_alpha", text="")
                            else:
                                if section_settings.smoothing_scale_x_regressor == "HUBER" and \
                               ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_scale_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif section_settings.smoothing_scale_x_regressor == "LASSO" and \
                               ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_scale_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if section_settings.smoothing_scale_y_regressor == "HUBER" and \
                               ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(section_settings, "smoothing_scale_y_huber_epsilon", text="")
                                elif section_settings.smoothing_scale_y_regressor == "LASSO" and \
                               ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(section_settings, "smoothing_scale_y_lasso_alpha", text="")


                    else:

                        if (section_settings.smoothing_do_scale or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_degree != 0:

                            sub_column.prop(section_settings, "smoothing_scale_regressor")
                            if section_settings.smoothing_scale_regressor == "HUBER":
                                sub_column.prop(section_settings, "smoothing_scale_huber_epsilon")
                            elif section_settings.smoothing_scale_regressor == "LASSO":
                                sub_column.prop(section_settings, "smoothing_scale_lasso_alpha")








                sub_column = column.column(heading="Rotation")
                sub_column.enabled = clip_settings.do_smoothing and not section_settings.disable_section

                sub_column.prop(section_settings, "smoothing_do_rotation")
                if section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate:
                    if section_settings.smoothing_use_different_x_y and not section_settings.smoothing_use_different_model:
                        row = sub_column.row(align=True)
                        row.prop(section_settings, "smoothing_rotation_degree")
                        row.prop(settings, "null_property")
                    else:
                        sub_column.prop(section_settings, "smoothing_rotation_degree")
                if section_settings.smoothing_use_different_model:



                    if (section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate) and \
                       section_settings.smoothing_rotation_degree != 0:
                        sub_column.prop(section_settings, "smoothing_rotation_regressor")
                        if section_settings.smoothing_rotation_regressor == "HUBER":
                            sub_column.prop(section_settings, "smoothing_rotation_huber_epsilon")
                        elif section_settings.smoothing_rotation_regressor == "LASSO":
                            sub_column.prop(section_settings, "smoothing_rotation_lasso_alpha")








                sub_column = column.column(heading="Power Pin")
                sub_column.enabled = clip_settings.do_smoothing and not section_settings.disable_section

                if section_settings.smoothing_use_different_x_y:
                    row = sub_column.row(align=True)
                    row.prop(section_settings, "smoothing_do_power_pin_x")
                    row.prop(section_settings, "smoothing_do_power_pin_y")
                    if section_settings.smoothing_do_power_pin_x == section_settings.smoothing_do_power_pin_y == True or section_settings.smoothing_extrapolate:
                        row = sub_column.row(align=True)
                        row.prop(section_settings, "smoothing_power_pin_x_degree")
                        row.prop(section_settings, "smoothing_power_pin_y_degree", text="")
                    elif section_settings.smoothing_do_power_pin_x:
                        row = sub_column.row(align=True)
                        row.prop(section_settings, "smoothing_power_pin_x_degree")
                        row.prop(settings, "null_property")
                    elif section_settings.smoothing_do_power_pin_y:
                        row = sub_column.row(align=True)
                        row.prop(settings, "null_property", text="Max Degree")
                        row.prop(section_settings, "smoothing_power_pin_y_degree", text="")
                else:
                    sub_column.prop(section_settings, "smoothing_do_power_pin")
                    if section_settings.smoothing_do_power_pin or section_settings.smoothing_extrapolate:
                        sub_column.prop(section_settings, "smoothing_power_pin_degree")
                if section_settings.smoothing_use_different_model:



                    if section_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0) \
                                or \
                               ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0) \
                               :
                            if \
                               ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0) \
                               :
                                row.prop(section_settings, "smoothing_power_pin_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                row.prop(section_settings, "smoothing_power_pin_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if section_settings.smoothing_power_pin_x_regressor == section_settings.smoothing_power_pin_y_regressor and \
                               ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0) \
                                and \
                               ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                if section_settings.smoothing_power_pin_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_power_pin_x_huber_epsilon")
                                    row.prop(section_settings, "smoothing_power_pin_y_huber_epsilon", text="")
                                elif section_settings.smoothing_power_pin_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_power_pin_x_lasso_alpha")
                                    row.prop(section_settings, "smoothing_power_pin_y_lasso_alpha", text="")
                            else:
                                if section_settings.smoothing_power_pin_x_regressor == "HUBER" and \
                               ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_power_pin_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif section_settings.smoothing_power_pin_x_regressor == "LASSO" and \
                               ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_power_pin_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if section_settings.smoothing_power_pin_y_regressor == "HUBER" and \
                               ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(section_settings, "smoothing_power_pin_y_huber_epsilon", text="")
                                elif section_settings.smoothing_power_pin_y_regressor == "LASSO" and \
                               ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(section_settings, "smoothing_power_pin_y_lasso_alpha", text="")


                    else:

                        if (section_settings.smoothing_do_power_pin or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_degree != 0:

                            sub_column.prop(section_settings, "smoothing_power_pin_regressor")
                            if section_settings.smoothing_power_pin_regressor == "HUBER":
                                sub_column.prop(section_settings, "smoothing_power_pin_huber_epsilon")
                            elif section_settings.smoothing_power_pin_regressor == "LASSO":
                                sub_column.prop(section_settings, "smoothing_power_pin_lasso_alpha")




                if not section_settings.smoothing_use_different_model:





                    if section_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               (((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) or \
                                ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) or \
                                ((section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate) and section_settings.smoothing_rotation_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0)) \
                                or \
                               (((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) or \
                                ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                            if \
                               (((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) or \
                                ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) or \
                                ((section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate) and section_settings.smoothing_rotation_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0)) \
                               :
                                row.prop(section_settings, "smoothing_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               (((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) or \
                                ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                row.prop(section_settings, "smoothing_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if section_settings.smoothing_x_regressor == section_settings.smoothing_y_regressor and \
                               (((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) or \
                                ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) or \
                                ((section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate) and section_settings.smoothing_rotation_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0)) \
                                and \
                               (((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) or \
                                ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                if section_settings.smoothing_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_x_huber_epsilon")
                                    row.prop(section_settings, "smoothing_y_huber_epsilon", text="")
                                elif section_settings.smoothing_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_x_lasso_alpha")
                                    row.prop(section_settings, "smoothing_y_lasso_alpha", text="")
                            else:
                                if section_settings.smoothing_x_regressor == "HUBER" and \
                               (((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) or \
                                ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) or \
                                ((section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate) and section_settings.smoothing_rotation_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif section_settings.smoothing_x_regressor == "LASSO" and \
                               (((section_settings.smoothing_do_position_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_x_degree != 0) or \
                                ((section_settings.smoothing_do_scale_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_x_degree != 0) or \
                                ((section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate) and section_settings.smoothing_rotation_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_x or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_x_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(section_settings, "smoothing_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if section_settings.smoothing_y_regressor == "HUBER" and \
                               (((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) or \
                                ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(section_settings, "smoothing_y_huber_epsilon", text="")
                                elif section_settings.smoothing_y_regressor == "LASSO" and \
                               (((section_settings.smoothing_do_position_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_y_degree != 0) or \
                                ((section_settings.smoothing_do_scale_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_y_degree != 0) or \
                                ((section_settings.smoothing_do_power_pin_y or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(section_settings, "smoothing_y_lasso_alpha", text="")


                    else:


                        if ((section_settings.smoothing_do_position or section_settings.smoothing_extrapolate) and section_settings.smoothing_position_degree != 0) or \
                           ((section_settings.smoothing_do_scale or section_settings.smoothing_extrapolate) and section_settings.smoothing_scale_degree != 0) or \
                           ((section_settings.smoothing_do_rotation or section_settings.smoothing_extrapolate) and section_settings.smoothing_rotation_degree != 0) or \
                           ((section_settings.smoothing_do_power_pin or section_settings.smoothing_extrapolate) and section_settings.smoothing_power_pin_degree != 0):


                            sub_column.prop(section_settings, "smoothing_regressor")
                            if section_settings.smoothing_regressor == "HUBER":
                                sub_column.prop(section_settings, "smoothing_huber_epsilon")
                            elif section_settings.smoothing_regressor == "LASSO":
                                sub_column.prop(section_settings, "smoothing_lasso_alpha")








                if not settings.do_advanced_smoothing:
                    sub_column = column.column()
                    sub_column.enabled = clip_settings.do_smoothing
                    sub_column.prop(clip_settings, "do_predictive_smoothing")
                    column.separator(factor=0.22)

                    sub_column = column.column()
                    sub_column.enabled = clip_settings.do_smoothing
                    sub_column.use_property_split = False
                    sub_column.prop(settings, "do_advanced_smoothing", toggle=True)
                    column.separator(factor=0.0)


            else:
                if settings.do_advanced_smoothing:
                    row = column.row(align=True)
                    row.enabled = False
                    sub_row = row.row(align=True)
                    sub_row.enabled = False and \
                                      context.edit_movieclip.AAEExportSettingsSectionLL > 0 and \
                                      ((context.edit_movieclip.AAEExportSettingsSectionLI == context.edit_movieclip.AAEExportSettingsSectionLL - 1 and \
                                        context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame >= 2) or \
                                       (context.edit_movieclip.AAEExportSettingsSectionLI < context.edit_movieclip.AAEExportSettingsSectionLL - 1 and \
                                        (context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame >= 2 or \
                                         context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].start_frame >= 2)))
                    sub_row.operator("movieclip.aae_export_section_add_section")
                    sub_row = row.row(align=True)
                    sub_row.enabled = False and \
                                      context.edit_movieclip.AAEExportSettingsSectionLL >= 2
                    sub_row.operator("movieclip.aae_export_section_remove_section")
                    column.separator(factor=0.44)

                    row = column.row()
                    row.enabled = False
                    row.alignment = "CENTER"
                    row.label(text="Section Settings")
                    column.separator(factor=0.40)

                    sub_column = column.column()
                    sub_column.enabled = False
                    sub_column.prop(clip_settings, "start_frame")
                    sub_column.prop(clip_settings, "end_frame")
                    column.separator(factor=0.0)

                    sub_column = column.column(align=True)
                    sub_column.enabled = False
                    sub_column.prop(clip_settings, "disable_section")
                    sub_column.prop(clip_settings, "smoothing_extrapolate", text="Extrapolate section")
                    column.separator(factor=0.44)

                    row = column.row(align=True)
                    row.enabled = False and not clip_settings.disable_section
                    row.alignment = "CENTER"
                    row.label(text="Section Smoothing")
                    column.separator(factor=0.40)

                    row = column.row(heading="Split Settings for", align=True)
                    row.enabled = False and not clip_settings.disable_section
                    row.prop(clip_settings, "smoothing_use_different_x_y")
                    row.prop(clip_settings, "smoothing_use_different_model")
                    column.separator(factor=0.0)

                    sub_column = column.column()
                    sub_column.enabled = False and not clip_settings.disable_section and \
                                         (selected_plane_tracks == 1) is not (context.selected_movieclip_tracks.__len__() == 1)
                    sub_column.operator("movieclip.aae_export_plot_section")
                    column.separator(factor=0.0)










                sub_column = column.column(heading="Position")
                sub_column.enabled = False and not clip_settings.disable_section

                if clip_settings.smoothing_use_different_x_y:
                    row = sub_column.row(align=True)
                    row.prop(clip_settings, "smoothing_do_position_x")
                    row.prop(clip_settings, "smoothing_do_position_y")
                    if clip_settings.smoothing_do_position_x == clip_settings.smoothing_do_position_y == True or clip_settings.smoothing_extrapolate:
                        row = sub_column.row(align=True)
                        row.prop(clip_settings, "smoothing_position_x_degree")
                        row.prop(clip_settings, "smoothing_position_y_degree", text="")
                    elif clip_settings.smoothing_do_position_x:
                        row = sub_column.row(align=True)
                        row.prop(clip_settings, "smoothing_position_x_degree")
                        row.prop(settings, "null_property")
                    elif clip_settings.smoothing_do_position_y:
                        row = sub_column.row(align=True)
                        row.prop(settings, "null_property", text="Max Degree")
                        row.prop(clip_settings, "smoothing_position_y_degree", text="")
                else:
                    sub_column.prop(clip_settings, "smoothing_do_position")
                    if clip_settings.smoothing_do_position or clip_settings.smoothing_extrapolate:
                        sub_column.prop(clip_settings, "smoothing_position_degree")
                if clip_settings.smoothing_use_different_model:



                    if clip_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               ((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) \
                                or \
                               ((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) \
                               :
                            if \
                               ((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) \
                               :
                                row.prop(clip_settings, "smoothing_position_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               ((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) \
                               :
                                row.prop(clip_settings, "smoothing_position_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if clip_settings.smoothing_position_x_regressor == clip_settings.smoothing_position_y_regressor and \
                               ((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) \
                                and \
                               ((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) \
                               :
                                if clip_settings.smoothing_position_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_position_x_huber_epsilon")
                                    row.prop(clip_settings, "smoothing_position_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_position_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_position_x_lasso_alpha")
                                    row.prop(clip_settings, "smoothing_position_y_lasso_alpha", text="")
                            else:
                                if clip_settings.smoothing_position_x_regressor == "HUBER" and \
                               ((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_position_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif clip_settings.smoothing_position_x_regressor == "LASSO" and \
                               ((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_position_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if clip_settings.smoothing_position_y_regressor == "HUBER" and \
                               ((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(clip_settings, "smoothing_position_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_position_y_regressor == "LASSO" and \
                               ((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(clip_settings, "smoothing_position_y_lasso_alpha", text="")


                    else:

                        if (clip_settings.smoothing_do_position or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_degree != 0:

                            sub_column.prop(clip_settings, "smoothing_position_regressor")
                            if clip_settings.smoothing_position_regressor == "HUBER":
                                sub_column.prop(clip_settings, "smoothing_position_huber_epsilon")
                            elif clip_settings.smoothing_position_regressor == "LASSO":
                                sub_column.prop(clip_settings, "smoothing_position_lasso_alpha")







                sub_column = column.column(heading="Scale")
                sub_column.enabled = False and not clip_settings.disable_section

                if clip_settings.smoothing_use_different_x_y:
                    row = sub_column.row(align=True)
                    row.prop(clip_settings, "smoothing_do_scale_x")
                    row.prop(clip_settings, "smoothing_do_scale_y")
                    if clip_settings.smoothing_do_scale_x == clip_settings.smoothing_do_scale_y == True or clip_settings.smoothing_extrapolate:
                        row = sub_column.row(align=True)
                        row.prop(clip_settings, "smoothing_scale_x_degree")
                        row.prop(clip_settings, "smoothing_scale_y_degree", text="")
                    elif clip_settings.smoothing_do_scale_x:
                        row = sub_column.row(align=True)
                        row.prop(clip_settings, "smoothing_scale_x_degree")
                        row.prop(settings, "null_property")
                    elif clip_settings.smoothing_do_scale_y:
                        row = sub_column.row(align=True)
                        row.prop(settings, "null_property", text="Max Degree")
                        row.prop(clip_settings, "smoothing_scale_y_degree", text="")
                else:
                    sub_column.prop(clip_settings, "smoothing_do_scale")
                    if clip_settings.smoothing_do_scale or clip_settings.smoothing_extrapolate:
                        sub_column.prop(clip_settings, "smoothing_scale_degree")
                if clip_settings.smoothing_use_different_model:



                    if clip_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) \
                                or \
                               ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) \
                               :
                            if \
                               ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) \
                               :
                                row.prop(clip_settings, "smoothing_scale_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) \
                               :
                                row.prop(clip_settings, "smoothing_scale_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if clip_settings.smoothing_scale_x_regressor == clip_settings.smoothing_scale_y_regressor and \
                               ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) \
                                and \
                               ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) \
                               :
                                if clip_settings.smoothing_scale_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_scale_x_huber_epsilon")
                                    row.prop(clip_settings, "smoothing_scale_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_scale_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_scale_x_lasso_alpha")
                                    row.prop(clip_settings, "smoothing_scale_y_lasso_alpha", text="")
                            else:
                                if clip_settings.smoothing_scale_x_regressor == "HUBER" and \
                               ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_scale_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif clip_settings.smoothing_scale_x_regressor == "LASSO" and \
                               ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_scale_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if clip_settings.smoothing_scale_y_regressor == "HUBER" and \
                               ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(clip_settings, "smoothing_scale_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_scale_y_regressor == "LASSO" and \
                               ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(clip_settings, "smoothing_scale_y_lasso_alpha", text="")


                    else:

                        if (clip_settings.smoothing_do_scale or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_degree != 0:

                            sub_column.prop(clip_settings, "smoothing_scale_regressor")
                            if clip_settings.smoothing_scale_regressor == "HUBER":
                                sub_column.prop(clip_settings, "smoothing_scale_huber_epsilon")
                            elif clip_settings.smoothing_scale_regressor == "LASSO":
                                sub_column.prop(clip_settings, "smoothing_scale_lasso_alpha")








                sub_column = column.column(heading="Rotation")
                sub_column.enabled = False and not clip_settings.disable_section

                sub_column.prop(clip_settings, "smoothing_do_rotation")
                if clip_settings.smoothing_do_rotation or clip_settings.smoothing_extrapolate:
                    if clip_settings.smoothing_use_different_x_y and not clip_settings.smoothing_use_different_model:
                        row = sub_column.row(align=True)
                        row.prop(clip_settings, "smoothing_rotation_degree")
                        row.prop(settings, "null_property")
                    else:
                        sub_column.prop(clip_settings, "smoothing_rotation_degree")
                if clip_settings.smoothing_use_different_model:



                    if (clip_settings.smoothing_do_rotation or clip_settings.smoothing_extrapolate) and \
                       clip_settings.smoothing_rotation_degree != 0:
                        sub_column.prop(clip_settings, "smoothing_rotation_regressor")
                        if clip_settings.smoothing_rotation_regressor == "HUBER":
                            sub_column.prop(clip_settings, "smoothing_rotation_huber_epsilon")
                        elif clip_settings.smoothing_rotation_regressor == "LASSO":
                            sub_column.prop(clip_settings, "smoothing_rotation_lasso_alpha")








                sub_column = column.column(heading="Power Pin")
                sub_column.enabled = False and not clip_settings.disable_section

                if clip_settings.smoothing_use_different_x_y:
                    row = sub_column.row(align=True)
                    row.prop(clip_settings, "smoothing_do_power_pin_x")
                    row.prop(clip_settings, "smoothing_do_power_pin_y")
                    if clip_settings.smoothing_do_power_pin_x == clip_settings.smoothing_do_power_pin_y == True or clip_settings.smoothing_extrapolate:
                        row = sub_column.row(align=True)
                        row.prop(clip_settings, "smoothing_power_pin_x_degree")
                        row.prop(clip_settings, "smoothing_power_pin_y_degree", text="")
                    elif clip_settings.smoothing_do_power_pin_x:
                        row = sub_column.row(align=True)
                        row.prop(clip_settings, "smoothing_power_pin_x_degree")
                        row.prop(settings, "null_property")
                    elif clip_settings.smoothing_do_power_pin_y:
                        row = sub_column.row(align=True)
                        row.prop(settings, "null_property", text="Max Degree")
                        row.prop(clip_settings, "smoothing_power_pin_y_degree", text="")
                else:
                    sub_column.prop(clip_settings, "smoothing_do_power_pin")
                    if clip_settings.smoothing_do_power_pin or clip_settings.smoothing_extrapolate:
                        sub_column.prop(clip_settings, "smoothing_power_pin_degree")
                if clip_settings.smoothing_use_different_model:



                    if clip_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0) \
                                or \
                               ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0) \
                               :
                            if \
                               ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0) \
                               :
                                row.prop(clip_settings, "smoothing_power_pin_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                row.prop(clip_settings, "smoothing_power_pin_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if clip_settings.smoothing_power_pin_x_regressor == clip_settings.smoothing_power_pin_y_regressor and \
                               ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0) \
                                and \
                               ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                if clip_settings.smoothing_power_pin_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_power_pin_x_huber_epsilon")
                                    row.prop(clip_settings, "smoothing_power_pin_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_power_pin_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_power_pin_x_lasso_alpha")
                                    row.prop(clip_settings, "smoothing_power_pin_y_lasso_alpha", text="")
                            else:
                                if clip_settings.smoothing_power_pin_x_regressor == "HUBER" and \
                               ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_power_pin_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif clip_settings.smoothing_power_pin_x_regressor == "LASSO" and \
                               ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_power_pin_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if clip_settings.smoothing_power_pin_y_regressor == "HUBER" and \
                               ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(clip_settings, "smoothing_power_pin_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_power_pin_y_regressor == "LASSO" and \
                               ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(clip_settings, "smoothing_power_pin_y_lasso_alpha", text="")


                    else:

                        if (clip_settings.smoothing_do_power_pin or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_degree != 0:

                            sub_column.prop(clip_settings, "smoothing_power_pin_regressor")
                            if clip_settings.smoothing_power_pin_regressor == "HUBER":
                                sub_column.prop(clip_settings, "smoothing_power_pin_huber_epsilon")
                            elif clip_settings.smoothing_power_pin_regressor == "LASSO":
                                sub_column.prop(clip_settings, "smoothing_power_pin_lasso_alpha")




                if not clip_settings.smoothing_use_different_model:





                    if clip_settings.smoothing_use_different_x_y:
                        row = sub_column.row(align=True)


                        if \
                               (((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) or \
                                ((clip_settings.smoothing_do_rotation or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_rotation_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0)) \
                                or \
                               (((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                            if \
                               (((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) or \
                                ((clip_settings.smoothing_do_rotation or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_rotation_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0)) \
                               :
                                row.prop(clip_settings, "smoothing_x_regressor")
                            else:
                                row.prop(settings, "null_property", text="Linear Model")
                            if \
                               (((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                row.prop(clip_settings, "smoothing_y_regressor", text="")
                            else:
                                row.prop(settings, "null_property")

                            if clip_settings.smoothing_x_regressor == clip_settings.smoothing_y_regressor and \
                               (((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) or \
                                ((clip_settings.smoothing_do_rotation or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_rotation_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0)) \
                                and \
                               (((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                if clip_settings.smoothing_x_regressor == "HUBER":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_x_huber_epsilon")
                                    row.prop(clip_settings, "smoothing_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_x_regressor == "LASSO":
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_x_lasso_alpha")
                                    row.prop(clip_settings, "smoothing_y_lasso_alpha", text="")
                            else:
                                if clip_settings.smoothing_x_regressor == "HUBER" and \
                               (((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) or \
                                ((clip_settings.smoothing_do_rotation or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_rotation_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_x_huber_epsilon")
                                    row.prop(settings, "null_property")
                                elif clip_settings.smoothing_x_regressor == "LASSO" and \
                               (((clip_settings.smoothing_do_position_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_x_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_x_degree != 0) or \
                                ((clip_settings.smoothing_do_rotation or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_rotation_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_x or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_x_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(clip_settings, "smoothing_x_lasso_alpha")
                                    row.prop(settings, "null_property")
                                if clip_settings.smoothing_y_regressor == "HUBER" and \
                               (((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Epsilon")
                                    row.prop(clip_settings, "smoothing_y_huber_epsilon", text="")
                                elif clip_settings.smoothing_y_regressor == "LASSO" and \
                               (((clip_settings.smoothing_do_position_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_position_y_degree != 0) or \
                                ((clip_settings.smoothing_do_scale_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_scale_y_degree != 0) or \
                                ((clip_settings.smoothing_do_power_pin_y or clip_settings.smoothing_extrapolate) and clip_settings.smoothing_power_pin_y_degree != 0)) \
                               :
                                    row = sub_column.row(align=True)
                                    row.prop(settings, "null_property", text="Alpha")
                                    row.prop(clip_settings, "smoothing_y_lasso_alpha", text="")


                    else:


                        if True:


                            sub_column.prop(clip_settings, "smoothing_regressor")
                            if clip_settings.smoothing_regressor == "HUBER":
                                sub_column.prop(clip_settings, "smoothing_huber_epsilon")
                            elif clip_settings.smoothing_regressor == "LASSO":
                                sub_column.prop(clip_settings, "smoothing_lasso_alpha")








                if not settings.do_advanced_smoothing:
                    sub_column = column.column()
                    sub_column.enabled = False
                    sub_column.prop(clip_settings, "do_predictive_smoothing")
                    column.separator(factor=0.22)

                    sub_column = column.column()
                    sub_column.enabled = False
                    sub_column.use_property_split = False
                    sub_column.prop(settings, "do_advanced_smoothing", toggle=True)
                    column.separator(factor=0.0)









        else:
            clip_settings = context.edit_movieclip.AAEExportSettingsClip

            column = box.column(heading="Smoothing")
            column.enabled = False
            column.prop(clip_settings, "do_smoothing_fake")

        box = layout.box()
        column = box.column()
        row = column.row()
        row.alignment = "CENTER"
        row.label(text="Power Pin Remap")
        column.separator(factor=0.06)
        sub_column = column.column(align=True)
        sub_column.use_property_split = False
        row = sub_column.row(align=True)
        row.prop(clip_settings, "power_pin_remap_0002", text="")
        row.prop(clip_settings, "power_pin_remap_0003", text="")
        row = sub_column.row(align=True)
        row.prop(clip_settings, "power_pin_remap_0004", text="")
        row.prop(clip_settings, "power_pin_remap_0005", text="")

    @classmethod
    def poll(cls, context):
        return context.edit_movieclip is not None

class AAEExportSectionL(bpy.types.UIList):
    bl_label = "Export Section List"
    bl_idname = "SOLVE_PT_UL_aae_export_section_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in { "DEFAULT", "COMPACT" }:
            split = layout.split(factor=0.4)
            row = split.row()
            row.alignment = "RIGHT"
            row.label(text="Section")
            if item.disable_section:
                split.label(text=str(item.start_frame) + "‥" + str(item.end_frame) + " (disabled)")
            elif (context.selected_movieclip_tracks.__len__() == 1) is not ((selected_plane_tracks := [plane_track for plane_track in context.edit_movieclip.tracking.plane_tracks if plane_track.select]).__len__() == 1) and \
                 ((context.selected_movieclip_tracks.__len__() == 1 and \
                   not any([(item.start_frame < marker.frame < item.end_frame or \
                             marker.frame == item.start_frame == context.edit_movieclip.frame_start or \
                             marker.frame == item.end_frame == context.edit_movieclip.frame_start + context.edit_movieclip.frame_duration - 1) and \
                            not marker.mute for marker in context.selected_movieclip_tracks[0].markers])) or \
                  (selected_plane_tracks.__len__ == 1 and \
                   not any([(item.start_frame < marker.frame < item.end_frame or \
                             marker.frame == item.start_frame == context.edit_movieclip.frame_start or \
                             marker.frame == item.end_frame == context.edit_movieclip.frame_start + context.edit_movieclip.frame_duration - 1) and \
                            not marker.mute for marker in selected_plane_tracks[0]].markers))):
                split.label(text=str(item.start_frame) + "‥" + str(item.end_frame) + " (empty)")
            elif (context.selected_movieclip_tracks.__len__() == 1) is not ((selected_plane_tracks := [plane_track for plane_track in context.edit_movieclip.tracking.plane_tracks if plane_track.select]).__len__() == 1) and \
                 ((context.selected_movieclip_tracks.__len__() == 1 and \
                   any([item.start_frame <= marker.frame <= item.end_frame and \
                        marker.mute for marker in context.selected_movieclip_tracks[0].markers])) or \
                  (selected_plane_tracks.__len__ == 1 and \
                   any([item.start_frame <= marker.frame <= item.end_frame and \
                        marker.mute for marker in selected_plane_tracks[0]].markers))):
                if item.smoothing_extrapolate:
                    split.label(text=str(item.start_frame) + "‥" + str(item.end_frame) + " (extrapolated)")
                else:
                    split.label(text=str(item.start_frame) + "‥" + str(item.end_frame) + " (partial)")
            else:
                split.label(text=str(item.start_frame) + "‥" + str(item.end_frame))
        elif self.layout_type in { "GRID" }:
            layout.alignment = "CENTER"
            layout.label(text=str(item.start_frame))

class AAEExportSectionAddS(bpy.types.Operator):
    bl_label = "Add Section"
    bl_description = "Split the selected section"
    bl_idname = "movieclip.aae_export_section_add_section"

    def execute(self, context):
        from math import ceil

        context.edit_movieclip.AAEExportSettingsSectionL.add()
        context.edit_movieclip.AAEExportSettingsSectionLL += 1
        AAEExportSectionAddS._copy(context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI], context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLL - 1])

        if context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame >= 2:
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                = True
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLL - 1].start_frame \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame + ceil((context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame - context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame) / 2)
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                = False
        else:
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].frame_update_suppress \
                = True
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLL - 1].start_frame \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLL - 1].end_frame \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].start_frame \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame + 1
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].frame_update_suppress \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].frame_update_suppress \
                = False

        context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLL - 1].frame_update_suppress \
            = False
        context.edit_movieclip.AAEExportSettingsSectionLI += 1
        context.edit_movieclip.AAEExportSettingsSectionL.move(context.edit_movieclip.AAEExportSettingsSectionLL - 1, context.edit_movieclip.AAEExportSettingsSectionLI)

        return { "FINISHED" }

    @staticmethod
    def _copy(source, target):
        late = []
        later = []
        for name in dir(source):
            if name.startswith("_") or \
               name.startswith("bl") or name.startswith("rna") or \
               name.startswith("aa_"):
                continue

            match (("position" in name or "scale" in name or "rotation" in name or "power_pin" in name) << 1) + \
                  ("_x_" in name or name.endswith("_x") or "_y_" in name or name.endswith("_y")):
                case 0b00:
                    setattr(target, name, getattr(source, name))
                case 0b10 | 0b01:
                    late.append(name)
                case 0b11:
                    later.append(name)

        for name in late:
            setattr(target, name, getattr(source, name))
        for name in later:
            setattr(target, name, getattr(source, name))

class AAEExportSectionRemoveS(bpy.types.Operator):
    bl_label = "Remove Section"
    bl_description = "Remove the selected section"
    bl_idname = "movieclip.aae_export_section_remove_section"

    def execute(self, context):
        if context.edit_movieclip.AAEExportSettingsSectionLI != 0:
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI - 1].frame_update_suppress \
                = True
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI - 1].end_frame \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].end_frame
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI - 1].frame_update_suppress \
                = False

            context.edit_movieclip.AAEExportSettingsSectionL.remove(context.edit_movieclip.AAEExportSettingsSectionLI)
            context.edit_movieclip.AAEExportSettingsSectionLL -= 1
            context.edit_movieclip.AAEExportSettingsSectionLI -= 1
        else:
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].frame_update_suppress \
                = True
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].start_frame \
                = context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI].start_frame
            context.edit_movieclip.AAEExportSettingsSectionL[context.edit_movieclip.AAEExportSettingsSectionLI + 1].frame_update_suppress \
                = False

            context.edit_movieclip.AAEExportSettingsSectionL.remove(context.edit_movieclip.AAEExportSettingsSectionLI)
            context.edit_movieclip.AAEExportSettingsSectionLL -= 1

        return { "FINISHED" }

class AAEExportLegacy(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export motion tracking markers to Adobe After Effects 6.0 compatible files"""
    bl_label = "Export to Adobe After Effects 6.0 Keyframe Data"
    bl_idname = "export.aae_export_legacy"
    filename_ext = ""
    filter_glob = bpy.props.StringProperty(default="*", options={ "HIDDEN" })

    def execute(self, context):
        if bpy.data.movieclips.__len__() == 0:
            raise ValueError("Have you opened any movie clips?")
        # This could be fixed but I'm not going to spend time on this :)
        if bpy.data.movieclips.__len__() >= 2:
            raise ValueError("The legacy export method only allows one clip to be loaded into Blender at a time. You can either try the new export interface at „Clip Editor > Tools > Solve > AAE Export“ or use „File > New“ to create a new Blender file.")
        clip = bpy.data.movieclips[0]
        settings = context.screen.AAEExportSettings
        clip_settings = context.edit_movieclip.AAEExportSettingsClip
        section_settings_l = context.edit_movieclip.AAEExportSettingsSectionL
        section_settings_ll = context.edit_movieclip.AAEExportSettingsSectionLL

        for track in clip.tracking.tracks:
            AAEExportExportAll._export_to_file( \
                clip, track, \
                AAEExportExportAll._generate(clip, track, settings, clip_settings, section_settings_l, section_settings_ll), \
                self.filepath, True)

        for plane_track in clip.tracking.plane_tracks:
            AAEExportExportAll._export_to_file( \
            clip, track, \
            AAEExportExportAll._generate(clip, plane_track, settings, clip_settings, section_settings_l, section_settings_ll), \
            self.filepath, True)

        return { "FINISHED" }

classes = (AAEExportSettings,
           AAEExportSettingsClip,
           AAEExportSettingsSectionL,
           AAEExportExportAll,
           AAEExportCopySingleTrack,
           AAEExportCopyPlaneTrack,
           AAEExportPlotResult,
           AAEExportPlotSection,
           AAEExportPlot,
           AAEExport,
           AAEExportSelectedTrack,
           AAEExportAllTracks,
           AAEExportOptions,
           AAEExportSectionL,
           AAEExportSectionAddS,
           AAEExportSectionRemoveS,
           AAEExportLegacy)

class AAEExportRegisterSettings(bpy.types.PropertyGroup):
    bl_label = "AAEExportRegisterSettings"
    bl_idname = "AAEExportRegisterSettings"

class AAEExportRegisterSmoothingID(bpy.types.Operator):
    bl_label = "Install Dependencies for Smoothing (Optional)"
    bl_description = get_smoothing_modules_install_description()
    bl_idname = "preference.aae_export_register_smoothing_id"
    bl_options = { "REGISTER", "INTERNAL" }

    def execute(self, context):
        import importlib.util
        if importlib.util.find_spec("packaging") != None:
            import packaging.version
        elif importlib.util.find_spec("distutils") != None: # distutils deprecated in Python 3.12
            import distutils.version
        import os
        import platform
        import sys
        import threading

        if os.name == "nt":
            self._execute_sys_win32()
        elif sys.platform == "darwin" and \
             "aae_export_b_mac" in globals() and "aae_export_id_mac" in globals():
            self._execute_aae_export_id_mac()
        elif (sys.platform == "linux" or sys.platform.startwith("freebsd")) and platform.machine() in ["x86_64", "x86-64", "amd64", "x64"] and \
             "aae_export_b_linux_x86_64" in globals() and "aae_export_id_linux_x86_64" in globals():
            self._execute_aae_export_id_linux_x86_64()
        elif sys.platform == "linux" or sys.platform.startwith("freebsd"):
            self._execute_sys_linux()
        else:
            self._execute_direct_unspecified(context)
            
        for module in smoothing_modules:
            if importlib.util.find_spec(module[0]) == None:
                return { "FINISHED" }
                
            if module[2]:
                exec("import " + module[0])
                module_version = eval(module[0] + ".__version__")
                if "packaging" in locals():
                    if packaging.version.parse(module_version) < packaging.version.parse(module[2]):
                        return { "FINISHED" }
                elif "distutils" in locals(): # distutils deprecated in Python 3.12
                    if distutils.version.LooseVersion(module_version) < distutils.version.LooseVersion(module[2]):
                        return { "FINISHED" }

        global is_smoothing_modules_available
        is_smoothing_modules_available = True
        
        self.report({ "INFO" }, "Dependencies installed successfully.")

        def unregister_register_class_():
            global is_register_classes_registered
            unregister_register_class()
            is_register_classes_registered = False
        threading.Timer(300, unregister_register_class_).start()

        return { "FINISHED" }

    def _execute_sys_win32(self):
        from pathlib import PurePath
        import os
        import sys
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".py", delete=False) as f:
            f.write("import os, subprocess, sys, traceback\n")
            f.write("if __name__ == \"__main__\":\n")
            f.write("\ttry:\n")

            f.write("\t\tsubprocess.run([\"" + PurePath(sys.executable).as_posix() + "\", \"-m\", \"ensurepip\"], check=True)\n")
            f.write("\t\tsubprocess.run([\"" + PurePath(sys.executable).as_posix() + "\", \"-m\", \"pip\", \"install\", \"--no-input\", \"" + \
                                        "\", \"".join([module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules]) + \
                                        "\"], check=True)\n")

            f.write("\texcept:\n")
            f.write("\t\ttraceback.print_exc()\n")
            f.write("\t\tos.system(\"pause\")\n")

        # Python, in a Python, in a PowerShell, in a Python
        print("aae-export: " + "PowerShell -Command \"& {Start-Process \\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\" -Verb runAs -Wait}\"")
        if os.system("PowerShell -Command \"& {Start-Process \\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\" -Verb runAs -Wait}\"") != 0:
            self._execute_direct_unspecified()

    def _execute_sys_linux(self):
        from pathlib import PurePath
        import os
        import sys
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".py", delete=False) as f:
            f.write("import os, subprocess, sys, traceback\n")
            f.write("if __name__ == \"__main__\":\n")
            f.write("\ttry:\n")

            f.write("\t\tsubprocess.run([\"" + PurePath(sys.executable).as_posix() + "\", \"-m\", \"ensurepip\"])\n")
            f.write("\t\tsubprocess.run([\"" + PurePath(sys.executable).as_posix() + "\", \"-m\", \"pip\", \"install\", \"--no-input\", \"" + \
                                        "\", \"".join([module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules]) + \
                                        "\"], check=True)\n")

            f.write("\texcept:\n")
            f.write("\t\ttraceback.print_exc()\n")
            f.write("\t\tprint()\n")
            f.write("\t\tinput(\"Press Enter to continue ... \")\n")

        print("aae-export: terminal -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"")
        if os.system("terminal -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"") != 0:
            print("aae-export: gnome-terminal -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"")
            if os.system("gnome-terminal -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"") != 0:
                print("aae-export: konsole -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"")
                if os.system("konsole -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"") != 0:
                    print("aae-export: xterm -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"")
                    if os.system("xterm -e \"\\\"" + sys.executable + "\\\" \\\"" + PurePath(f.name).as_posix() + "\\\"\"") != 0:
                        self._execute_direct_unspecified()

    def _execute_aae_export_id_mac(self):
        import base64
        from ctypes import CDLL, c_char_p, c_size_t, create_string_buffer
        from io import BytesIO
        from math import ceil
        import subprocess
        import sys
        import tarfile
        import tempfile
        from pathlib import PurePath

        path = tempfile.mkdtemp()

        try:
            with tarfile.open(fileobj=BytesIO(base64.standard_b64decode(aae_export_b_mac)), mode="r", errorlevel=1) as tar:
                tar.extractall(path=path)

            print("aae-export: \"" + PurePath(path, "libbase122.dylib").as_posix() + "\"")
            base122 = CDLL(PurePath(path, "libbase122.dylib").as_posix())
            base122.decode.argtypes = (c_char_p, c_size_t, c_char_p, c_size_t)
            base122.decode.restype = c_size_t
            out_size = base122.decode(c_char_p(aae_export_id_mac), c_size_t((size := 17)),
                                      (out := create_string_buffer(ceil(size * 1.20))), c_size_t(ceil(size * 1.20)))
            with tarfile.open(fileobj=BytesIO(out.raw[:out_size]), mode="r", errorlevel=1) as tar:
                tar.extractall(path=path)

            print("aae-export: \"" + \
                  PurePath(path, "aae-export-install-dependencies.app", "Contents", "MacOS", "aae-export-install-dependencies").as_posix() + "\" \"" + \
                  sys.executable + "\" " + \
                  " ".join([module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules]))
            subprocess.run([PurePath(path, "aae-export-install-dependencies.app", "Contents", "MacOS", "aae-export-install-dependencies").as_posix(), \
                            sys.executable] + \
                           [module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules], check=True)
        except:
            self._execute_direct_unspecified()

    def _execute_aae_export_id_linux_x86_64(self):
        import base64
        from ctypes import CDLL, c_char_p, c_size_t, create_string_buffer
        from io import BytesIO
        from math import ceil
        import subprocess
        import sys
        import tarfile
        import tempfile
        from pathlib import PurePath

        path = tempfile.mkdtemp()

        try:
            with tarfile.open(fileobj=BytesIO(base64.standard_b64decode(aae_export_b_linux_x86_64)), mode="r", errorlevel=1) as tar:
                tar.extractall(path=path)

            print("aae-export: \"" + PurePath(path, "libbase122.so").as_posix() + "\"")
            base122 = CDLL(PurePath(path, "libbase122.so").as_posix())
            base122.decode.argtypes = (c_char_p, c_size_t, c_char_p, c_size_t)
            base122.decode.restype = c_size_t
            out_size = base122.decode(c_char_p(aae_export_id_linux_x86_64), c_size_t((size := 26)),
                                      (out := create_string_buffer(ceil(size * 1.20))), c_size_t(ceil(size * 1.20)))
            with tarfile.open(fileobj=BytesIO(out.raw[:out_size]), mode="r", errorlevel=1) as tar:
                tar.extractall(path=path)

            print("aae-export: \"" + \
                  PurePath(path, "aae-export-install-dependencies").as_posix() + "\" \"" + \
                  sys.executable + "\" " + \
                  " ".join([module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules]))
            subprocess.run([PurePath(path, "aae-export-install-dependencies").as_posix(), \
                            sys.executable] + \
                           [module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules], check=True)
        except:
            self._execute_sys_linux()

    def _execute_direct_unspecified(self):
        import subprocess
        import sys

        print("aae-export: \"" + sys.executable + "\" -m ensurepip")
        subprocess.run([sys.executable, "-m", "ensurepip"]) # sys.executable requires Blender 2.93
        print("aae-export: \"" + sys.executable + "\" -m pip install --no-input " + " ".join([module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules]))
        subprocess.run([sys.executable, "-m", "pip", "install", "--no-input"] + [module[1] + ">=" + module[2] if module[2] else module[1] for module in smoothing_modules], check=True)

class AAEExportRegisterPreferencePanel(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    def draw(self, context):
        layout = self.layout
        settings = context.window_manager.AAEExportRegisterSettings

        if not is_smoothing_modules_available:
            layout.operator("preference.aae_export_register_smoothing_id", icon="CONSOLE")
        else:
            layout.label(text="Dependencies installed successfully.")

register_classes = (AAEExportRegisterSettings,
                    AAEExportRegisterSmoothingID,
                    AAEExportRegisterPreferencePanel)

is_register_classes_registered = False

def register():
    import importlib.util
    if importlib.util.find_spec("packaging") != None:
        import packaging.version
    elif importlib.util.find_spec("distutils") != None: # distutils deprecated in Python 3.12
        import distutils.version
    
    global is_smoothing_modules_available
    global is_register_classes_registered

    for module in smoothing_modules:
        if importlib.util.find_spec(module[0]) == None:
            register_register_classes()
            is_register_classes_registered = True

            is_smoothing_modules_available = False
            break

        if module[2]:
            exec("import " + module[0])
            module_version = eval(module[0] + ".__version__")
            if "packaging" in locals():
                if packaging.version.parse(module_version) < packaging.version.parse(module[2]):
                    register_register_classes()
                    is_register_classes_registered = True

                    is_smoothing_modules_available = False
                    break
            elif "distutils" in locals(): # distutils deprecated in Python 3.12
                if distutils.version.LooseVersion(module_version) < distutils.version.LooseVersion(module[2]):
                    register_register_classes()
                    is_register_classes_registered = True

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
    bpy.types.MovieClip.AAEExportSettingsClip = bpy.props.PointerProperty(type=AAEExportSettingsClip)
    bpy.types.MovieClip.AAEExportSettingsSectionL = bpy.props.CollectionProperty(type=AAEExportSettingsSectionL)
    bpy.types.MovieClip.AAEExportSettingsSectionLI = bpy.props.IntProperty(name="AAEExportSettingsSectionLI")
    bpy.types.MovieClip.AAEExportSettingsSectionLL = bpy.props.IntProperty(name="AAEExportSettingsSectionLL", default=0)
        
    bpy.types.TOPBAR_MT_file_export.append(register_export_legacy)

def register_register_classes():
    for class_ in register_classes:
        bpy.utils.register_class(class_)

    bpy.types.WindowManager.AAEExportRegisterSettings = bpy.props.PointerProperty(type=AAEExportRegisterSettings)
    
def unregister():
    global is_register_classes_registered
    if is_register_classes_registered:
        unregister_register_class()
        is_register_classes_registered = False
    
    unregister_main_class()

def unregister_main_class():
    bpy.types.TOPBAR_MT_file_export.remove(register_export_legacy)
    
    del bpy.types.Screen.AAEExportSettings
    del bpy.types.MovieClip.AAEExportSettingsClip
    del bpy.types.MovieClip.AAEExportSettingsSectionL
    del bpy.types.MovieClip.AAEExportSettingsSectionLI
    del bpy.types.MovieClip.AAEExportSettingsSectionLL
    
    for class_ in classes:
        bpy.utils.unregister_class(class_)

def unregister_register_class():
    del bpy.types.WindowManager.AAEExportRegisterSettings

    for class_ in register_classes:
        bpy.utils.unregister_class(class_)

if __name__ == "__main__":
    register()
#    unregister() 
