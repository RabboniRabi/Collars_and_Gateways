# Code to simulate broadcasting of realtime collar information from an elephant

import json
import time
import sys
import paho.mqtt.client as mqtt

# Delay time between message publications
delay_time = 5

# Declare a client
client = None

# Initialise the MQTT client
def initialise_client():
	global client
	client = mqtt.Client()
	client.on_connect = on_connect

# publisher to publish on a topic

# Read simulated collar data in JSON format from given file
# and publish data to the MQTT broker periodically
def read_and_publish(collar_sim_file_name):

	# Read the json file
	with open(collar_sim_file_name) as sim_file:
		file_data = json.load(sim_file)

	# Get the data list
	data_list = file_data['data']

	# Publish data in elephant topic
	for data in data_list:
		client.publish("animal/elephant", json.dumps(data), 0, False)
		publish_time = time.ctime(time.time())
		print("Real time collar data at time - " , publish_time , " : " , json.dumps(data))
		time.sleep(delay_time)
	sys.exit()


# Function called on connection to MQTT broker
def on_connect(client, userdata, flags, rc):
	print("Connected to broker")


# start of the application
if __name__ == "__main__":
	# Check that file name of simulated collar data is passed in the program argument
	if len(sys.argv) == 1 or ".json" not in sys.argv[-1]:
		print("No argument found for name of JSON file containing simulated collar information!")
		sys.exit()
	collar_sim_file_name = sys.argv[-1]
	# Initialise the client
	initialise_client()
	# Connect to local broker. Replace with your broker IP here.
	client.connect("192.168.1.107", 1883, 60)
	# Call the function to read and publish the simulated collar data
	read_and_publish(collar_sim_file_name)
	#print(collar_sensor_data)
	client.loop_forever()
