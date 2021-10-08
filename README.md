# OBS Audio Track Hotkey Script

This is a Python script for OBS Studio that allows you to use hotkeys to set the active tracks for a given audio source.

## Script Installation and Setup
The script only works with OBS Studio versions 21.x and later. If you have an older version you will need to update.

### Python Configuration
As of this writing OBS seems to have issues with the newest versions of Python (3.7+). This script was developed and tested using Python 3.6.8.

You need [Python 3.6](https://www.python.org/downloads/) installed on your PC. The bit version of your Python installation must match your OBS installation - use "x86-64" for 64 bit OBS Studio and "x86" for 32 bit OBS Studio. In the menu in OBS Studio, go to `Tools` and then `Scripts`. Then in the "Python Settings" tab, set the path to point to the Python installation folder.

Add the script to the OBS "Scripts" window using the '+' icon on the bottom left. Select the script in the "Loaded Scripts" panel, and if everything is set up correctly you should see the script properties show up on the right.

### Script Options
Fill out the configuration settings in the script properties:

* **Audio Source**: the audio source to modify. At the moment only one audio source can be used for each instance of the script.
* **Track Group A**: the first set of track options to be set with a hotkey.
* **Track Group B**: the second set of track options to be set with a hotkey.

You can access the hotkey settings using the standard OBS hotkeys panel (`File -> Settings -> Hotkeys`). The track assignments can be tested using the "Apply Track Settings" buttons on the script properties page.

Track assignment changes occur in real time. On certain versions of OBS the "Advanced Audio Properties" window may not refresh when track changes are made outside of the GUI. Close and re-open the audio properties window to see the changes.

## License
This script is licensed under the terms of the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html), either version 3 of the License, or (at your option) any later version.
