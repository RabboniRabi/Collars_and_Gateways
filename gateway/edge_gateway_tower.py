# Main python script that combines the functionalities of a gateway tower

# In the real-world, the sensors in the tower will detect the presence of animals (collars) through LoRa and bluetooth mesh.
# Here we are using MQTT to listen for animal location broadcasts and then choose to send the data of those positions that are in "range".

# LoRa can also be used to estimate the location using LoRa cloud Geolocation. This capability will be used by gateway devices to
# estimate the location of animals(collars) using the meta data received from collars. For this simulation, the collars(device nodes) 
# will send aritificial position values.

import paho.mqtt.client  as mqtt
import json
import sys
from read_tower_info import get_tower_info
from send_to_cloud import send_to_iot_connect_dash
from edge_monitoring import alert_events_check
from haversine import haversine



# The MQTT client
client = None

# This number is used to simulate range of gateway towers in communication with animal collars. Distance is given in meters.
# This estimated value is based on some available studies of LoRa range in forest environments.
lora_range = 1200

# The name of the file to read the tower information. This name is fetched from command line during program execution.
tower_info_file_name = None

# Function to initialise the MQTT client and declare methods to be called on connection and messages	
def initialise_client():
	global client
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	# Connect to the broker running on the same machine.
	# You can replace this with the IP address of your broker
	client.connect("localhost", 1883, 60)
	client.loop_forever()
	
# On connection callback, subscribe to animal topics
def on_connect(client, userdata, flags, rc):
	print("Connected to broker")
	
	#subscribe to all aninmal topics
	client.subscribe("animal/#")
	print("Listening for animal collars!")
	

# Function called on receiving messages on subscribed topic
def on_message(client, userdata, msg):
	#print("Message received")
	# Get the collar info from the message
	collar_info = msg.payload.decode("utf-8")
	# Convert the JSON string of collar info to dictionary type
	collar_info = json.loads(collar_info)
	#print(collar_info)
	# Get the tower info
	tower_info = get_tower_info(tower_info_file_name)
	# Check if the animal is in range
	in_range = check_animal_in_range(collar_info['animal_position'], tower_info['position'])
	# Check for gateway, sensor or Tiny ML events and pass them on to be sent to the dashboard
	if in_range:
		gateway_events = alert_events_check(collar_info, tower_info)
		if gateway_events is not None:
			send_to_iot_connect_dash(collar_info, tower_info, gateway_events['dashboard'])
		if 'sensor_events' in collar_info:
			send_to_iot_connect_dash(collar_info, tower_info, collar_info['sensor_events'][0])
		if 'tiny_ml_detected_events' in collar_info:
			send_to_iot_connect_dash(collar_info, tower_info, collar_info['tiny_ml_detected_events'][0])
		else:
			send_to_iot_connect_dash(collar_info, tower_info, None)
	

# Function to check if given collar of animal is in range of the tower.
# The purpose of this function is to simulate an animal coming within range of a tower.
def check_animal_in_range(animal_position, tower_position):

	animal_pos_tuple = (animal_position['latitude'], animal_position['longitude'])
	tower_pos_tuple = (tower_position['latitude'], tower_position['longitude'])
	distance_from_tower = haversine(animal_pos_tuple, tower_pos_tuple, unit='m')
	#print("distance_from_tower: ", distance_from_tower)
	global lora_range
	if (distance_from_tower < lora_range):
		print("Animal in range of tower")
		return True
	else:
		return False
	

# Main function called on execution of this script
if __name__ == "__main__":

	# Check that file name of tower info is passed in the program argument
	if len(sys.argv) == 1 or ".json" not in sys.argv[-1]:
		print("No argument found for name of JSON file containing tower information")
		sys.exit()
	tower_info_file_name = sys.argv[-1]
	# Initialise the MQTT client to connect and listen for messages
	initialise_client()
	
	


