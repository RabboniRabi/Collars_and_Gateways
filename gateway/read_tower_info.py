# Code to read tower information from file

import json

tower_info = None

def read_tower_info(tower_info_file_name):
	global tower_info
	#Read the json file
	with open(tower_info_file_name) as tower_info_file:
		tower_info = json.load(tower_info_file)
	return tower_info

def get_tower_info(tower_info_file_name):
	if (tower_info is None):
		return read_tower_info(tower_info_file_name)
	else:
		return tower_info

if __name__ == "__main__":

	print(read_tower_info())
