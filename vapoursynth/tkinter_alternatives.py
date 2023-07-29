# tkinter_alternatives.py
# Copyright (c) Akatsumekusa and contributors

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

# ---------------------------------------------------------------------
# This is a fix for Aegisub VapourSynth Default Video Script if your
# Python installation does not come with Tkinter.
#
# Put this file in `?data/automation/vapoursynth`` and edit your video
# script.
# Include the file by adding this line below `import aegisub_vs as a`
#   import tkinter_alternatives as ask
# Replace the line to generate keyframe:
#   __aegi_keyframes = a.get_keyframes(filename, clip, __aegi_keyframes, generate=a.GenKeyframesMode.ASK)
# with:
#   __aegi_keyframes = a.get_keyframes(filename, clip, __aegi_keyframes, generate=a.GenKeyframesMode.ASK, ask_callback=ask.callback)
# ---------------------------------------------------------------------

__version__ = "1.0.2"

def _askyesno_windows(title: str, message: str, _):
    """
    Display a simple yes no alert dialogue on Windows.
    Call _askyesno() instead.
    """
    import subprocess

    try:
        process = subprocess.run(["powershell", "-WindowStyle", "hidden", "-Command", "$wshell = New-Object -ComObject Wscript.Shell; $answer = $wshell.Popup(\"" + message + "\", 0, \"" + title + "\", 4 + 32); Write-Host $answer"], \
                                 capture_output=True)
        if process.stdout.decode("utf-8").startswith("6"):
            return True
        elif process.stdout.decode("utf-8").startswith("7"):
            return False
        else:
            return None
    except:
        return None

def _askyesno_linux(title: str, message: str, default: bool = True):
    """
    Display a simple yes no alert dialogue on Linux.
    Call _askyesno() instead.
    """
    import subprocess

    try:
        if default:
            process = subprocess.run(["dialog", "--title", title, "--backtitle", title, "--yesno", message, 8, 20, 60])
        else:
            process = subprocess.run(["dialog", "--defaultno",  "--title", title, "--backtitle", title, "--yesno", message, 8, 20, 60])

        if process.returncode == 0:
            return True
        elif process.returncode == 1:
            return False
        else:
            return None
    except:
        try:
            """
echo MESSAGE
switch yn in Yes No
do
    case $yn in
        Yes ) exit 0;;
        No ) exit 1;;
    esac
done
            """
            process = subprocess.run(["terminal", "-e", "bash -c \"echo " + message + "; select yn in Yes No; do case \\$yn in Yes ) exit 0;; No ) exit 1;; esac; done;\""])
            if process.returncode == 0: return True
            elif process.returncode == 1: return False
            else: return None
        except:
            try:
                process = subprocess.run(["gnome-terminal", "-e", "bash -c \"echo " + message + "; select yn in Yes No; do case \\$yn in Yes ) exit 0;; No ) exit 1;; esac; done;\""])
                if process.returncode == 0: return True
                elif process.returncode == 1: return False
                else: return None
            except:
                try:
                    process = subprocess.run(["konsole", "-e", "bash -c \"echo " + message + "; select yn in Yes No; do case \\$yn in Yes ) exit 0;; No ) exit 1;; esac; done;\""])
                    if process.returncode == 0: return True
                    elif process.returncode == 1: return False
                    else: return None
                except:
                    try:
                        process = subprocess.run(["xterm", "-e", "bash -c \"echo " + message + "; select yn in Yes No; do case \\$yn in Yes ) exit 0;; No ) exit 1;; esac; done;\""])
                        if process.returncode == 0: return True
                        elif process.returncode == 1: return False
                        else: return None
                    except:
                        return None

def _askyesno_darwin(title: str, message: str, default: bool = True):
    """
    Display a simple yes no alert dialogue on Mac.
    Call _askyesno() instead.
    """
    import subprocess

    if default:
        default = "Yes"
    else:
        default = "No"

    try:
        process = subprocess.run(["osascript", "-e", "display alert \"" + message + "\" buttons { \"Yes\", \"No\" } default button \"" + default + "\"", "-e", "button returned of result"], \
                                 capture_output=True)
        if process.stdout.decode("utf-8").startswith("Yes"):
            return True
        elif process.stdout.decode("utf-8").startswith("No"):
            return False
        else:
            return None
    except:
        return None

def _askyesno_tkinter(title: str, message: str, default: bool = True):
    """
    Display a simple yes no alert dialogue using tkinter.
    Call _askyesno() instead.
    """
    from tkinter.messagebox import askyesno

    if default:
        default = "yes"
    else:
        default = "no"

    return askyesno(title, message, default=default)

def askyesno(title: str, message: str, default: bool = True):
    """
    Display a simple yes no alert dialogue.
    Similar to tkinter.messagebox.askyesno but note the parameter
    default accepts a bool instead of a string.
    May throw if both platform-dependent and tkinter solution fails.
    """
    import platform

    yesno = None

    if platform.system() == "Windows":
        yesno = _askyesno_windows(title, message, default)
    elif platform.system() == "Linux":
        yesno = _askyesno_linux(title, message, default)
    elif platform.system() == "Darwin":
        yesno = _askyesno_darwin(title, message, default)

    if yesno is None:
        yesno = _askyesno_tkinter(title, message, default)

    return yesno

def callback(_):
    """
    A callback function for ask_callback in aegisub_vs.get_keyframes
    Fix the problem if your Python installation does not come with Tkinter.
    """
    return askyesno("Generate Keyframes", \
                    "No keyframes file was found for this video file.\nShould Aegisub detect keyframes from the video?\nThis will take a while", \
                    default=False)
