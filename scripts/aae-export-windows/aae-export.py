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
    "version": (1, 1, 6),
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
                                                description="Generate unique files every time",
                                                default=False)
    do_also_export: bpy.props.BoolProperty(name="Auto export",
                                           description="Automatically export the selected track to file while copying",
                                           default=True)

    do_smoothing_fake: bpy.props.BoolProperty(name="Enable",
                                              description="Perform smoothing on tracking data.\nThis feature requires additional packages to be installed. Please head to „Edit > Preference > Add-ons > Video Tools: AAE Export > Preferences“ to install the dependencies",
                                              default=False)
    do_smoothing: bpy.props.BoolProperty(name="Enable",
                                         description="Perform smoothing on tracking data.\nThis uses position data, scale data, rotation data and Power Pin data of individual tracks and plane tracks to fit polynomial regression models, and then uses the fit models to generate smoothed data.\n\nPlease note that this smoothing feature is very rudimentary and may cause more problems than it solves. Akatsumekusa recommends trying it only if the tracking is unbearably poor.\n\nAlso, Akatsumekusa is working on a new script that will provide this feature much better than it is right now. Please expect Non Carbonated AAE Export to come out sometime in the year",
                                         default=False)

class AAEExportSettingsSectionL(bpy.types.PropertyGroup):
    bl_label = "AAEExportSettingsSectionL"
    bl_idname = "AAEExportSettingsSectionL"

    section_start_frame: bpy.props.IntProperty(name="Start frame",
                                               description="The first frame of the section",
                                               default=-2147483648)
    section_end_frame: bpy.props.IntProperty(name="End frame",
                                             description="The last frame of the section",
                                             default=2147483647)
                                               
    smoothing_use_different_x_y: bpy.props.BoolProperty(name="Split x/y",
                                               description="Use different regression settings for x and y axis of each data",
                                               default=False)
    smoothing_use_different_model: bpy.props.BoolProperty(name="Split data",
                                               description="Use different regression model for each data",
                                               default=False)









    smoothing_do_position: bpy.props.BoolProperty(name="Smooth",
                                            description="Perform smoothing on position data",
                                            default=True)

    smoothing_position_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of position  data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_position_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_position_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_position_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)

    smoothing_position_x_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of position x data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_position_x_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_position_x_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_position_x_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)

    smoothing_position_y_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of position y data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_position_y_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_position_y_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_position_y_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)


    smoothing_do_scale: bpy.props.BoolProperty(name="Smooth",
                                            description="Perform smoothing on scale data",
                                            default=True)

    smoothing_scale_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of scale  data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_scale_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_scale_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_scale_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)

    smoothing_scale_x_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of scale x data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_scale_x_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_scale_x_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_scale_x_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)

    smoothing_scale_y_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of scale y data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_scale_y_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_scale_y_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_scale_y_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)


    smoothing_do_rotation: bpy.props.BoolProperty(name="Smooth",
                                            description="Perform smoothing on rotation data",
                                            default=True)

    smoothing_rotation_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of rotation  data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=1,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_rotation_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_rotation_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_rotation_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)


    smoothing_do_power_pin: bpy.props.BoolProperty(name="Smooth",
                                            description="Perform smoothing on Power Pin data",
                                            default=True)

    smoothing_power_pin_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of Power Pin  data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_power_pin_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_power_pin_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_power_pin_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)

    smoothing_power_pin_x_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of Power Pin x data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_power_pin_x_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_power_pin_x_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_power_pin_x_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)

    smoothing_power_pin_y_degree: bpy.props.IntProperty(name="Max Degree",
                                                                                        description="The maximal polynomial degree of Power Pin y data.\nA degree of 1 means the data scales linearly.\nA degree of 2 means the data scales quadratically.\nA degree of 3 means the data scales cubically.\n\nAkatsumekusa recommends setting this value to the exact polynomial degree of the data, as setting it too high may cause overfitting.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#polynomial-regression-extending-linear-models-with-basis-functions“ and „https://en.wikipedia.org/wiki/Polynomial_regression“",
                                                                                        default=2,
                                                                                        min=1,
                                                                                        soft_max=16)
    smoothing_power_pin_y_regressor: bpy.props.EnumProperty(items=(("HUBER", "Huber Regressor", "Huber Regressor is an L2-regularised regression model that is robust to outliers.\n\nFor more information, visit „https://scikit-learn.org/stable/modules/linear_model.html#robustness-regression-outliers-and-modeling-errors“ and „https://en.wikipedia.org/wiki/Huber_loss“"),
                                                                                                   ("LASSO", "Lasso Regressor", "Lasso Regressor is an L1-regularised regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#lasso“ and „https://en.wikipedia.org/wiki/Lasso_(statistics)“"),
                                                                                                   ("LINEAR", "Linear Regressor", "Ordinary least squares regression model.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares“ and „https://en.wikipedia.org/wiki/Ordinary_least_squares“")),
                                                                                            name="Linear Model",
                                                                                            default="LINEAR")
    smoothing_power_pin_y_huber_epsilon: bpy.props.FloatProperty(name="Epsilon",
                                                                                                 description="The epsilon of a Huber Regressor controls the number of samples that should be classified as outliers. The smaller the epsilon, the more robust it is to outliers.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html“",
                                                                                                 default=1.50,
                                                                                                 min=1.00,
                                                                                                 soft_max=10.00,
                                                                                                 step=1,
                                                                                                 precision=2)
    smoothing_power_pin_y_lasso_alpha: bpy.props.FloatProperty(name="Alpha",
                                                                                               description="The alpha of a Lasso Regressor controls the regularisation strength.\n\nFor more information, please visit „https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html“",
                                                                                               default=0.10,
                                                                                               min=0.00,
                                                                                               soft_max=100.0,
                                                                                               step=1,
                                                                                               precision=2)








    smoothing_do_predictive_smoothing: bpy.props.BoolProperty(name="Predictive Filling",
                                                              description="Generates position data, scale data, rotation data and Power Pin data over the whole length of the clip, even if the track or plane track is only enabled on a section of the clip.\n\nThe four options above, „Smooth Position“, „Smooth Scale“, „Smooth Rotation“ and „Smooth Power Pin“, decides whether to use predicted data to replace the existing data on frames where the track is enabled, while this option decides whether to use predicted data to fill the gaps in the frames where the marker is not enabled.\n\nAkatsumekusa recommends enabling this option only if the subtitle line covers the whole length of the trimmed clip",
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
        
        return { "FINISHED" }

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
                          settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

                scale \
                    = AAEExportExportAll._smoothing( \
                          scale, \
                          settings.smoothing_do_scale, settings.smoothing_do_predictive_smoothing, \
                          settings.smoothing_scale_degree, \
                          settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

                rotation \
                    = AAEExportExportAll._unlimit_rotation( \
                          semilimited_rotation)
                
                rotation \
                    = AAEExportExportAll._smoothing( \
                          rotation, \
                          settings.smoothing_do_rotation, settings.smoothing_do_predictive_smoothing, \
                          settings.smoothing_rotation_degree, \
                          settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

                limited_rotation \
                    = AAEExportExportAll._limit_rotation( \
                          rotation)

                for i in range(4):
                    power_pin[i] \
                        = AAEExportExportAll._smoothing( \
                              power_pin[i], \
                              settings.smoothing_do_power_pin, settings.smoothing_do_predictive_smoothing, \
                              settings.smoothing_power_pin_degree, \
                              settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

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
    def _plot_graph(clip, track, settings):
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
        import numpy as np
        
        ratio, multiplier \
            = AAEExportExportAll._calculate_aspect_ratio( \
                  clip)

        position, scale, semilimited_rotation, power_pin \
            = AAEExportExportAll._prepare_data( \
                  clip, track, ratio)

        smoothed_position \
            = AAEExportExportAll._smoothing( \
                  position, \
                  settings.smoothing_do_position, settings.smoothing_do_predictive_smoothing, \
                  settings.smoothing_position_degree, \
                  settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

        smoothed_scale \
            = AAEExportExportAll._smoothing( \
                  scale, \
                  settings.smoothing_do_scale, settings.smoothing_do_predictive_smoothing, \
                  settings.smoothing_scale_degree, \
                  settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

        rotation \
            = AAEExportExportAll._unlimit_rotation( \
                  semilimited_rotation)
            
        smoothed_rotation \
            = AAEExportExportAll._smoothing( \
                  rotation, \
                  settings.smoothing_do_rotation, settings.smoothing_do_predictive_smoothing, \
                  settings.smoothing_rotation_degree, \
                  settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

        smoothed_power_pin \
            = np.empty_like(power_pin)
        for i in range(4):
            smoothed_power_pin[i] \
                = AAEExportExportAll._smoothing( \
                      power_pin[i], \
                      settings.smoothing_do_power_pin, settings.smoothing_do_predictive_smoothing, \
                      settings.smoothing_power_pin_degree, \
                      settings.smoothing_position_regressor, settings.smoothing_position_huber_epsilon, settings.smoothing_position_lasso_alpha)

        AAEExportExportAll._plot( \
            position, scale, rotation, power_pin, \
            smoothed_position, smoothed_scale, smoothed_rotation, smoothed_power_pin, \
            settings.smoothing_do_position, settings.smoothing_do_scale, settings.smoothing_do_rotation, settings.smoothing_do_power_pin)

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
        import numpy.linalg as LA

        if not clip.frame_duration >= 1:
            raise ValueError("clip.frame_duration must be greater than or equal to 1")
            
        # As explained in _prepare_position_and_power_pin_marker_track()
        misshapen_power_pin = np.full((clip.frame_duration, 8), np.nan, dtype=np.float64)

        for marker in track.markers:
            if not 0 < marker.frame <= clip.frame_duration:
                continue
            if marker.mute:
                continue
            misshapen_power_pin[marker.frame - 1] = [marker.corners[3][0], 1 - marker.corners[3][1],
                                                     marker.corners[2][0], 1 - marker.corners[2][1],
                                                     marker.corners[0][0], 1 - marker.corners[0][1],
                                                     marker.corners[1][0], 1 - marker.corners[1][1]]
          
        misshapen_power_pin *= np.tile(ratio, 4)

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
        def eat_(slice):
            if np.isnan(slice[0]):
                return np.full((2), np.nan, dtype=np.float64)
            try:
                t = LA.solve(np.transpose(np.vstack((slice[6:8] - slice[0:2], slice[2:4] - slice[4:6]))), slice[2:4] - slice[0:2])[0]
            except LA.LinAlgError:
                return np.mean(slice.reshape((4, 2)), axis=0)
            else:
                return (1 - t) * slice[0:2] + t * slice[6:8]
        position = np.apply_along_axis(eat_, 1, misshapen_power_pin)
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
            predicted_data \
                = np.empty_like(data)
            for i in range(data.shape[1]):
                predicted_data[:, i] \
                    = AAEExportExportAll._smoothing( \
                          data[:, i], do_smoothing, do_predictive_smoothing, degree, regressor, huber_epsilon, lasso_alpha)
            return predicted_data
        
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
        limited_rotation[limited_rotation >= 359.9995] = 0.0
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
            if not np.isnan(position[frame][0]):
                aae_position.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(frame + 1, *position[frame], 0.0))
            if not np.isnan(scale[frame][0]):
                aae_scale.append("\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}".format(frame + 1, *scale[frame], 100.0))
            if not np.isnan(limited_rotation[frame]):
                aae_rotation.append("\t{:d}\t{:.3f}".format(frame + 1, limited_rotation[frame]))
            if not np.isnan(power_pin[0][frame][0]):
                aae_power_pin_0002.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[0][frame]))
                aae_power_pin_0003.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[1][frame]))
                aae_power_pin_0004.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[2][frame]))
                aae_power_pin_0005.append("\t{:d}\t{:.3f}\t{:.3f}".format(frame + 1, *power_pin[3][frame]))

        return aae_position, aae_scale, aae_rotation, aae_power_pin_0002, aae_power_pin_0003, aae_power_pin_0004, aae_power_pin_0005
        
    @staticmethod
    def _plot(position, scale, rotation, power_pin, smoothed_position, smoothed_scale, smoothed_rotation, smoothed_power_pin, smoothing_do_position, smoothing_do_scale, smoothing_do_rotation, smoothing_do_power_pin):
        """
        Plot the data.

        Parameters
        ----------
        position : npt.NDArray[float64]
        scale : npt.NDArray[float64]
        rotation : npt.NDArray[float64]
        power_pin : npt.NDArray[float64]
        smoothed_position : npt.NDArray[float64]
        smoothed_scale : npt.NDArray[float64]
        smoothed_rotation : npt.NDArray[float64]
        smoothed_power_pin : npt.NDArray[float64]
        """
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import numpy as np
        import PIL
        import re

        def plot_position(row, position, smoothed_position, label, do_smoothing):
            def test_z_score(data):
                # Iglewicz and Hoaglin's modified Z-score
                return np.nonzero(0.6745 * (d := np.absolute(data - np.median(data))) / np.median(d) >= 3)[0]

            row[0].invert_yaxis()
            row[0].scatter(position[:, 0], position[:, 1], color="red", marker="x", s=1, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if do_smoothing:
                row[0].plot(smoothed_position[:, 0], smoothed_position[:, 1], color="blue", label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[0].legend()
            row[0].set_xlabel("X")
            row[0].set_ylabel("Y")

            row[1].scatter(np.arange(1, position.shape[0] + 1), position[:, 0], color="red", s=1, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if do_smoothing:
                row[1].plot(np.arange(1, position.shape[0] + 1), smoothed_position[:, 0], color="blue", label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[1].legend()
            row[1].set_xlabel("Frame")
            row[1].set_ylabel(" ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " X")

            if do_smoothing:
                row[2].plot(np.arange(1, position.shape[0] + 1), (p := position[:, 0] - smoothed_position[:, 0]), color="red", label="_".join(re.split(" |_", label.lower())), zorder=2.002)
                row[2].plot(np.arange(1, position.shape[0] + 1), smoothed_position[:, 0] - smoothed_position[:, 0], color="blue", label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.001)
                for i in test_z_score(p):
                    row[2].annotate(i + 1, (i + 1, p[i]))
                row[2].legend()
                row[2].set_xlabel("Frame")
                row[2].set_ylabel("Residual of " + " ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " X")
            else:
                row[2].axis("off")

            row[3].scatter(np.arange(1, position.shape[0] + 1), position[:, 1], color="red", s=1, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if do_smoothing:
                row[3].plot(np.arange(1, position.shape[0] + 1), smoothed_position[:, 1], color="blue", label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[3].legend()
            row[3].set_xlabel("Frame")
            row[3].set_ylabel(" ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " Y")

            if do_smoothing:
                row[4].plot(np.arange(1, position.shape[0] + 1), (p := position[:, 1] - smoothed_position[:, 1]), color="red", label="_".join(re.split(" |_", label.lower())), zorder=2.002)
                row[4].plot(np.arange(1, position.shape[0] + 1), smoothed_position[:, 1] - smoothed_position[:, 1], color="blue", label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.001)
                for i in test_z_score(p):
                    row[4].annotate(i + 1, (i + 1, p[i]))
                row[4].legend()
                row[4].set_xlabel("Frame")
                row[4].set_ylabel("Residual of " + " ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))) + " Y")
            else:
                row[4].axis("off")
        
        def plot_univariate(row, rotation, smoothed_rotation, label, do_smoothing):
            row[0].axis("off")
            
            row[1].scatter(np.arange(1, rotation.shape[0] + 1), rotation, color="red", s=1, label="_".join(re.split(" |_", label.lower())), zorder=2.001)
            if do_smoothing:
                row[1].plot(np.arange(1, rotation.shape[0] + 1), smoothed_rotation, color="blue", label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.002)
            row[1].legend()
            row[1].set_xlabel("Frame")
            row[1].set_ylabel(label.title())

            if do_smoothing:
                row[2].plot(np.arange(1, rotation.shape[0] + 1), rotation - smoothed_rotation, color="red", label="_".join(re.split(" |_", label.lower())), zorder=2.002)
                row[2].plot(np.arange(1, rotation.shape[0] + 1), smoothed_rotation - smoothed_rotation, color="blue", label="_".join(["smoothed"] + re.split(" |_", label.lower())), zorder=2.001)
                row[2].legend()
                row[2].set_xlabel("Frame")
                row[2].set_ylabel("Residual of " + " ".join(list(map(lambda w : w.capitalize(), re.split(" |_", label)))))
            else:
                row[2].axis("off")
            
            row[3].axis("off")
            row[4].axis("off")
        
        fig, axs = plt.subplots(ncols=5, nrows=7, figsize=(5 * 5.4, 7 * 4.05), dpi=250, layout="constrained")
        plot_position(axs[0], position, smoothed_position, "position", smoothing_do_position)
        plot_position(axs[1], scale, smoothed_scale, "scale", smoothing_do_scale)
        plot_univariate(axs[2], rotation, smoothed_rotation, "rotation", smoothing_do_rotation)
        plot_position(axs[3], power_pin[0], smoothed_power_pin[0], "power_pin_0002", smoothing_do_power_pin)
        plot_position(axs[4], power_pin[1], smoothed_power_pin[1], "power_pin_0003", smoothing_do_power_pin)
        plot_position(axs[5], power_pin[2], smoothed_power_pin[2], "power_pin_0004", smoothing_do_power_pin)
        plot_position(axs[6], power_pin[3], smoothed_power_pin[3], "power_pin_0005", smoothing_do_power_pin)

        fig.canvas.draw()
        with PIL.Image.frombytes("RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb()) as im:
            im.show()

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

        aae = AAEExportExportAll._generate(clip, context.selected_movieclip_tracks[0], settings)
        
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

        aae = None
        for plane_track in context.edit_movieclip.tracking.plane_tracks:
            if plane_track.select == True:
                aae = AAEExportExportAll._generate(clip, plane_track, settings)
                break

        AAEExportExportAll._copy_to_clipboard(context, aae)
        if settings.do_also_export:
            AAEExportExportAll._export_to_file(clip, clip.tracking.plane_tracks[0], aae, None, settings.do_do_not_overwrite)
        
        return { "FINISHED" }

class AAEExportPlotGraph(bpy.types.Operator):
    bl_label = "Plot Graph"
    bl_description = "Plot the data and the smoothed data on graph"
    bl_idname = "movieclip.aae_export_plot_graph"

    def execute(self, context):
        clip = context.edit_movieclip
        settings = context.screen.AAEExportSettings

        if 33 == 1:
            AAEExportExportAll._plot_graph(clip, context.selected_movieclip_tracks[0], settings)
        else:
            for plane_track in context.edit_movieclip.tracking.plane_tracks:
                if plane_track.select == True:
                    AAEExportExportAll._plot_graph(clip, plane_track, settings)
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
        
        settings = context.screen.AAEExportSettings
        
        column = layout.column()
        column.label(text="Selected track")

        row = layout.row()
        row.scale_y = 2
        row.enabled = 33 == 1
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
        row.enabled = 38 >= 1 or \
                      44 >= 1
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
        #   Smoothing [x] Enabled
        # [      Plot Result      ]
        # Detect para [           ]
        # Detect para [           ]
        # [    Detect Sections    ]
        # Sections
        # > Section 1 1..20   < [+]
        # > Section 2 20..69  < [-]
        # > Section 3 69..122 <
        # Section 1
        # Start Frame [     1     ]
        #   End Frame [    20     ]
        # [       Plot Graph      ]
        #             [ ] Split...
        #    Position [x] Apply...
        #  Max Degree [     3     ]
        #       Scale [x] Apply...
        #  Max Degree [     2     ]
        #    Rotation [x] Apply...
        #  Max Degree [     1     ]
        #   Power Pin [x] Apply...
        #  Max Degree [     2     ]
        # Linear M... [Huber Re...]
        #     Epsilon [   1.50    ]
        # Predicti... [ ] Apply

        #             [x] Split...
        #    Position [x] Apply...
        #  Max Degree [  3  ][  2  ]

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        clip = context.edit_movieclip
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
            column = box.column(heading="Smoothing")
            column.prop(settings, "do_smoothing")
            column.separator(factor=0.0)
            
            sub_column = column.column()
            sub_column.template_list("SOLVE_PT_aae_export_section_list", "SOLVE_PT_aae_export_section_list", clip, "AAEExportSettingsSectionL", clip, "AAEExportSettingsSectionLI")

            selected_plane_tracks = 0
            for plane_track in context.edit_movieclip.tracking.plane_tracks:
                if plane_track.select == True:
                    selected_plane_tracks += 1
            sub_column = column.column()
            sub_column.enabled = settings.do_smoothing and \
                                 (selected_plane_tracks == 1) is not (33 == 1)
            sub_column.operator("movieclip.aae_export_plot_graph")
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

    @classmethod
    def poll(cls, context):
        return context.edit_movieclip is not None

class AAEExportSectionL(bpy.types.UIList):
    bl_label = "Export Section List"
    bl_idname = "SOLVE_PT_aae_export_section_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in { "Default", "Compact" }:
            layout.label(text="Section " + str(item.section_start_frame) + "‥" + str(item.section_end_frame))
        elif self.layout_type in { "GRID" }:
            layout.alignment = "CENTER"
            layout.label(text=str(item.section_start_frame))

class AAEExportLegacy(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export motion tracking markers to Adobe After Effects 6.0 compatible files"""
    bl_label = "Export to Adobe After Effects 6.0 Keyframe Data"
    bl_idname = "export.aae_export_legacy"
    filename_ext = ""
    filter_glob = bpy.props.StringProperty(default="*", options={ "HIDDEN" })

    def execute(self, context):
        if 19 == 0:
            raise ValueError("Have you opened any movie clips?")
        # This is broken but I don't want to fix...
        if 19 >= 2:
            raise ValueError("The legacy export method only allows one clip to be loaded into Blender at a time. You can either try the new export interface at „Clip Editor > Tools > Solve > AAE Export“ or use „File > New“ to create a new Blender file.")
        clip = bpy.data.movieclips[0]
        settings = context.screen.AAEExportSettings

        for track in clip.tracking.tracks:
            AAEExportExportAll._export_to_file(clip, track, AAEExportExportAll._generate(clip, track, None), self.filepath, True)

        for plane_track in clip.tracking.plane_tracks:
            AAEExportExportAll._export_to_file(clip, track, AAEExportExportAll._generate(clip, plane_track, None), self.filepath, True)

        return { "FINISHED" }

classes = (AAEExportSettings,
           AAEExportSettingsSectionL,
           AAEExportExportAll,
           AAEExportCopySingleTrack,
           AAEExportCopyPlaneTrack,
           AAEExportPlotGraph,
           AAEExport,
           AAEExportSelectedTrack,
           AAEExportAllTracks,
           AAEExportOptions,
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
    bpy.types.MovieClip.AAEExportSettingsSectionL = bpy.props.CollectionProperty(type=AAEExportSettingsSectionL)
    bpy.types.MovieClip.AAEExportSettingsSectionLI = bpy.props.IntProperty(name="AAEExportSettingsSectionLI")
        
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
    del bpy.types.MovieClip.AAEExportSettingsSectionL
    del bpy.types.MovieClip.AAEExportSettingsSectionLI
    
    for class_ in classes:
        bpy.utils.unregister_class(class_)

def unregister_register_class():
    del bpy.types.WindowManager.AAEExportRegisterSettings

    for class_ in register_classes:
        bpy.utils.unregister_class(class_)

if __name__ == "__main__":
    register()
#    unregister() 
