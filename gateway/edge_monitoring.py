# Code to perfom edge monitoring on a gateway tower

from haversine import haversine
import nvector as nv

# Function to check for events that would need warning/alerts
# If there is any such event, the function will return a message
# collar information and tower information are taken as function parameters
def alert_events_check(collar_info, tower_info):
	# Check for perimeter based events
	if(tower_info['zone'] == "CONFLICT" and 'perimeter_info' in tower_info):
		perimeter_message = perimeter_check(collar_info['animal_position'], tower_info['perimeter_info'])
		if (perimeter_message is not None):
			# Build and return messages to be used in dashboard and local alerts
			return build_breach_messages(collar_info, tower_info, perimeter_message)

# Check for perimeter based events.
# Returns None if are no perimeter breaches
def perimeter_check(animal_position, perimeter_info):

	# Define a perimeter message to return with a breach message if any
	perimeter_message = {}

	# If an alert perimeter is defined for the tower, check if perimeter based alert has to be triggered
	if('alert_perimeter' in perimeter_info):
		print("checking alert perimeter")
		# get the alert perimeter
		alert_perimeter = perimeter_info['alert_perimeter']	

		# Get the width and length of the bounding rectangle
		perimeter_length = get_haversine_distance(alert_perimeter['north_west_corner'], alert_perimeter['north_east_corner'])
		perimeter_width = get_haversine_distance(alert_perimeter['north_west_corner'], alert_perimeter['south_west_corner'])

		# Flags to check that the animal position is within the perimeter
		within_width = False
		within_length = False
		
		# Get the absolute distance of the animal from the four boundaries
		distance_to_boundaries = get_distance_from_boundaries(animal_position, alert_perimeter)

		if (distance_to_boundaries['west'] <= perimeter_length and distance_to_boundaries['east'] <= perimeter_length):
			within_length = True
		if (distance_to_boundaries['north'] <= perimeter_width and distance_to_boundaries['south'] <= perimeter_width):
			within_width = True
		
		# If alert event is for animal inside perimeter
		if (perimeter_info['perimeter_check'] == "INSIDE"):
			if (within_width and within_length):
				# Build and return the breach message
				perimeter_message['level'] = "ALERT"
				perimeter_message['text'] = "inside alert perimeter"
				return perimeter_message
		
		# If alert event is for animal going outside perimeter
		if (perimeter_info['perimeter_check'] == "OUTSIDE"):
			if (within_width == False or within_length == False):
				# Build and return the breach message
				perimeter_message['level'] = "ALERT"
				perimeter_message['text'] = "outside alert perimeter"
				return perimeter_message
				
	
	
	# If a warning perimeter is defined for the tower, check if perimeter based warning has to be triggered
	if('warning_perimeter' in perimeter_info):
		
		print("checking warning perimeter")
		# get the warning perimeter
		warning_perimeter = perimeter_info['warning_perimeter']
		
		perimeter_length = get_haversine_distance(warning_perimeter['north_west_corner'], warning_perimeter['north_east_corner'])
		perimeter_width = get_haversine_distance(warning_perimeter['north_west_corner'], warning_perimeter['south_west_corner'])
		
		# Flags to check that the animal position is within the perimeter
		within_width = False
		within_length = False
		
		# Get the absolute distance of the animal from the four boundaries
		distance_to_boundaries = get_distance_from_boundaries(animal_position, warning_perimeter)
		
		
		if (distance_to_boundaries['west'] <= perimeter_length and distance_to_boundaries['east'] <= perimeter_length):
			within_length = True
		if (distance_to_boundaries['north'] <= perimeter_width and distance_to_boundaries['south'] <= perimeter_width):
			within_width = True
		
		# If warning event is for animal inside perimeter
		if (perimeter_info['perimeter_check'] == "INSIDE"):
			if (within_width and within_length):
				# Build and return the breach message
				perimeter_message['level'] = "WARNING"
				perimeter_message['text'] = "inside warning perimeter"
				return perimeter_message
		
		# If warning event is for animal going outside perimeter
		elif (perimeter_info['perimeter_check'] == "OUTSIDE"):
			if (within_width == False or within_length == False):
				# Build and return the breach message
				perimeter_message['level'] = "WARNING"
				perimeter_message['text'] = "outside warning perimeter"
				return perimeter_message
				
	
	return None
		
		
# Function to calculate the haversine distance between two locations	
def get_haversine_distance(position_a, position_b):
	position_a_tuple = (position_a['latitude'], position_a['longitude'])
	position_b_tuple = (position_b['latitude'], position_b['longitude'])
	return haversine(position_a_tuple, position_b_tuple, unit='m')
	
# Function to get the distance of the animal from each of the four sides of the perimeter
# This function uses the nvector library to calculate the cross track distance of the animal
# from each of the four boundaries of a bounded rectangle perimeter
def get_distance_from_boundaries(animal_position, perimeter):

	north_west_corner = perimeter['north_west_corner']
	north_east_corner = perimeter['north_east_corner']
	south_west_corner = perimeter['south_west_corner']
	south_east_corner = perimeter['south_east_corner']

	earth_radius = 6371e3
	frame = nv.FrameE(a=earth_radius, f=0)
	
	# Convert the positions to the format used by the nvector library
	animal_geo_point = frame.GeoPoint(animal_position['latitude'], animal_position['longitude'], degrees=True)

	north_west_geo_point = frame.GeoPoint(north_west_corner['latitude'], north_west_corner['longitude'], degrees=True)
	north_east_geo_point = frame.GeoPoint(north_east_corner['latitude'], north_east_corner['longitude'], degrees=True)
	south_west_geo_point = frame.GeoPoint(south_west_corner['latitude'], south_west_corner['longitude'], degrees=True)
	south_east_geo_point = frame.GeoPoint(south_east_corner['latitude'], south_east_corner['longitude'], degrees=True)
	
	# Get the four boundaries
	west_boundary = nv.GeoPath(north_west_geo_point, south_west_geo_point)
	east_boundary = nv.GeoPath(north_east_geo_point, south_east_geo_point)
	north_boundary = nv.GeoPath(north_west_geo_point, north_east_geo_point)
	south_boundary = nv.GeoPath(south_west_geo_point, south_east_geo_point)
	
	
	# Caclulate the absolute distance of the animal from each of the four boundaries
	dist_to_west_boundary = abs((west_boundary.cross_track_distance(animal_geo_point, method='greatcircle').ravel())[0])
	dist_to_east_boundary = abs((east_boundary.cross_track_distance(animal_geo_point, method='greatcircle').ravel())[0])
	dist_to_north_boundary = abs((north_boundary.cross_track_distance(animal_geo_point, method='greatcircle').ravel())[0])
	dist_to_south_boundary = abs((south_boundary.cross_track_distance(animal_geo_point, method='greatcircle').ravel())[0])
	
	# Put the distances in a dictonary and return
	distance_to_boundaries = {}
	distance_to_boundaries['west'] = dist_to_west_boundary
	distance_to_boundaries['east'] = dist_to_east_boundary
	distance_to_boundaries['north'] = dist_to_north_boundary
	distance_to_boundaries['south'] = dist_to_south_boundary
	
	return distance_to_boundaries

# Helper function to build perimeter breach messages for dashboard and local notifications
def build_breach_messages(collar_info, tower_info, perimeter_message):
	# Build a human readable message that can be sent straight to dashboard notifications
	breach_messages = {}
	dash_message = {}
	dash_message['level'] = perimeter_message['level']
	dash_message['text'] = collar_info['animal_name'] + " " + perimeter_message['text']
	dash_message['text'] = dash_message['text'] + " of: " + tower_info["id"] + "; type: " + tower_info["type"] + "; zone: " + tower_info["zone"]
	
	
	local_message = {}
	local_message['level'] = perimeter_message['level']
	local_message['text'] = collar_info['animal_name'] + " " + perimeter_message['text'] + "; "
	distance_from_tower = get_haversine_distance(collar_info['animal_position'], tower_info['position'])
	local_message['text'] = local_message['text'] + "Approximate distance from tower: " + str(distance_from_tower)
	
	breach_messages['dashboard'] = dash_message
	breach_messages['local'] = local_message
	
	print("Local Message: ", breach_messages['local']) 
	
	#print("breach_message: ", breach_messages)
	
	return breach_messages
	
	
		

