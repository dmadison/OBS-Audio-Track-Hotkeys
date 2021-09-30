#
# Project     OBS Audio Track Hotkey Script
# @author     David Madison
# @link       github.com/dmadison/OBS-Track-Hotkeys
# @license    GPLv3 - Copyright (c) 2021 David Madison
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from os import name
import obspython as obs


# ------------------------------------------------------------

# Script Properties

debug = True  # default to "True" until overwritten by properties
source_name = ""  # source name to monitor, stored from properties

num_groups = 2  # number of track groups to create for the source

# ------------------------------------------------------------

class TrackGroup:
	track_name_format = "track_{}{}"  # track_{number}{id}
	track_hotkey_format = "track_hotkey_{}"  # track_{id}

	num_tracks = 6  # number of tracks per source
	max_description_length = 32  # max length of the hotkey description string
	obs_data = None  # reference to OBS data saved with the script

	def __init__(self, id):
		self.id = id  # unique identifier, used as a suffix for properties selection
		self.mask = 0  # bitmask for track selection (set in script properties)

		self.callback = None  # function callback for the hotkey (unique)
		self.hotkey_id = obs.OBS_INVALID_HOTKEY_ID  # the hotkey property reference, used for setting the key itself
		self.hotkey_saved_key = None  # the key assigned to the hotkey (if there is one)

		self.__load_hotkey()      # load hotkey key from settings
		self.__register_hotkey()  # register hotkey callback with OBS hotkey manager

	def __del__(self):
		self.__cleanup()

	def set_track_mask(self, mask):
		self.mask = mask  # bitmask for track selection

	def apply_track_mask(self):
		set_source_tracks(self.mask)  # apply saved track selection mask to the source mixer

	def __cleanup(self):
		self.deregister_hotkey()   # remove the hotkey from the hotkey manager
		self.__release_memory()      # and release the C memory for the saved reference

	def __release_memory(self):
		obs.obs_data_array_release(self.hotkey_saved_key)

	def update_source(self):
		self.__deregister_hotkey()  # source has changed! remove the existing hotkey...
		self.__unsave_hotkey()      # remove the saved reference to its name/value
		self.__register_hotkey()    # and re-register it under a new name

	def __register_hotkey(self):
		key_description = "Track Group {} for '{}'".format(self.id.upper(), source_name)
		if(len(key_description) > TrackGroup.max_description_length):
			key_description = key_description[:TrackGroup.max_description_length - 3] + "..."  # truncate if too long

		self.callback = lambda pressed: self.__key_passthrough(pressed)  # small hack to get around the callback signature reqs.
		self.hotkey_id = obs.obs_hotkey_register_frontend("track_hotkey", key_description, self.callback)
		obs.obs_hotkey_load(self.hotkey_id, self.hotkey_saved_key)  # register new hotkey with GUI

	def __deregister_hotkey(self):
		if self.callback is not None:
			obs.obs_hotkey_unregister(self.callback)

	def __load_hotkey(self):
		# load the assigned key from the script data array
		self.hotkey_saved_key = obs.obs_data_get_array(TrackGroup.obs_data, TrackGroup.track_hotkey_format.format(str(self.id)))

	def save_hotkey(self):
		# save the assigned key from the GUI and store it in the script's data array
		self.hotkey_saved_key = obs.obs_hotkey_save(self.hotkey_id)
		obs.obs_data_set_array(TrackGroup.obs_data, TrackGroup.track_hotkey_format.format(str(self.id)), self.hotkey_saved_key)

	def __unsave_hotkey(self):
		# clear the assigned key from the script's data array (when changing )
		obs.obs_data_erase(TrackGroup.obs_data, TrackGroup.track_hotkey_format.format(str(self.id)))

	def __key_passthrough(self, pressed):
		if pressed:
			self.apply_track_mask()


track_groups = []  # list of track groups for iteration

# ------------------------------------------------------------


def dprint(*args, **kwargs):
	if debug == True:
		print(*args, **kwargs)


def list_audio_sources():
	audio_sources = []
	sources = obs.obs_enum_sources()

	for source in sources:
		if obs.obs_source_get_type(source) == obs.OBS_SOURCE_TYPE_INPUT:
			# output flag bit field: https://obsproject.com/docs/reference-sources.html?highlight=sources#c.obs_source_info.output_flags
			capabilities = obs.obs_source_get_output_flags(source)

			has_audio = capabilities & obs.OBS_SOURCE_AUDIO
			# has_video = capabilities & obs.OBS_SOURCE_VIDEO
			# composite = capabilities & obs.OBS_SOURCE_COMPOSITE

			if has_audio:
				audio_sources.append(obs.obs_source_get_name(source))

	obs.source_list_release(sources)

	return audio_sources


def get_mask_track_pretty(mask):
	output = ""
	for track in range(TrackGroup.num_tracks):
		track_state = mask & (1 << track)  # extract bit from packed mask
		track_char = 'X' if track_state else ''
		output += "Track {:1d}: {:1s}".format(track + 1, track_char)
		if(track < TrackGroup.num_tracks - 1): output += " | "  # append separator if not at end of line
	return output


def set_source_tracks(mask):
	if not isinstance(mask, int):
		dprint("Error: Mask is not of expected type")
		return

	source = obs.obs_get_source_by_name(source_name)
	if source is None:
		dprint("Error: Could not find selected source")
		return

	obs.obs_source_set_audio_mixers(source, mask)  # actually do the thing
	obs.obs_source_release(source)  # prevent memory leaks

	dprint("Successfully set tracks of '{}' to mask {:#04x} ({})".format(source_name, mask, get_mask_track_pretty(mask)))


def test_track_group(props, prop):
	button_name = obs.obs_property_name(prop)
	id = button_name.split('_')[-1]  # use suffix of property name as identifier

	# iterate through groups to find the identifier matching the button
	for group in track_groups:
		if id == group.id:
			set_source_tracks(group.mask)
			break


# ------------------------------------------------------------

# OBS Script Functions

def script_description():
	return "<b>OBS Audio Track Hotkey Script</b>" + \
			"<hr>" + \
			"Python script for setting audio track options using hotkeys." + \
			"<br/><br/>" + \
			"Made by David Madison, © 2021" + \
			"<br/><br/>" + \
			"partsnotincluded.com" + \
			"<br/>" + \
			"github.com/dmadison/OBS-Track-Hotkeys"


def script_update(settings):
	global debug, source_name, track_groups

	# check for updated source name
	new_source_name = obs.obs_data_get_string(settings, "source")
	source_updated = new_source_name != source_name  # flag for if the source is updated to a new value
	if source_updated and source_name != "":
		dprint("Changed source from '{}' to '{}'".format(source_name, new_source_name))
	source_name = new_source_name  # save new source name to global var

	debug = obs.obs_data_get_bool(settings, "debug")  # for printing debug messages

	for group in track_groups:
		# update hotkeys descriptions with new source name if needed
		if source_updated: group.update_source()
		
		# update track masks from settings
		mask = 0x00
		for track in range(TrackGroup.num_tracks):
			track_state = obs.obs_data_get_bool(settings, TrackGroup.track_name_format.format(track + 1, group.id))  # 1 if set, 0 otherwise
			mask |= (1 << track) if track_state else 0  # set relevant bit 'high' if box checked
		group.mask = mask
		# dprint("Mask for track group '{}' is '{:#04x}'".format(group.id.upper(), mask))


def script_properties():
	props = obs.obs_properties_create()

	# Create list of audio sources and add them to properties list
	audio_sources = list_audio_sources()
	source_list = obs.obs_properties_add_list(props, "source", "Audio Source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)

	for name in audio_sources:
		obs.obs_property_list_add_string(source_list, name, name)

	# Create "Print Debug" toggle checkbox 
	obs.obs_properties_add_bool(props, "debug", "Print Debug Messages")

	# Create track groups
	for group in track_groups:
		track_props = obs.obs_properties_create()
		for track in range(TrackGroup.num_tracks):
			track_str = str(track + 1)
			obs.obs_properties_add_bool(track_props, TrackGroup.track_name_format.format(track_str, group.id), "Track " + track_str)

		obs.obs_properties_add_button(track_props, "test_track_group_" + group.id, "Apply Track Settings", test_track_group)
		obs.obs_properties_add_group(props, "tracks_" + group.id, "Track Group " + group.id.upper(), obs.OBS_GROUP_NORMAL, track_props)

	return props


def script_load(settings):
	global debug, source_name, track_groups

	debug = obs.obs_data_get_bool(settings, "debug")
	source_name = obs.obs_data_get_string(settings, "source")

	TrackGroup.obs_data = settings  # save settings reference to class

	# creates a list of groups starting at 'a' and proceeding through the lowercase letters
	track_groups = [ TrackGroup(chr(ord('a') + i)) for i in range(num_groups) ]

	dprint("OBS Audio Track Hotkey Script Loaded")


def script_unload():
	dprint("OBS Audio Track Hotkey Script Unloaded. Goodbye! <3")


def script_save(settings):
	# save all hotkey values to the script settings array
	for group in track_groups:
		group.save_hotkey()
