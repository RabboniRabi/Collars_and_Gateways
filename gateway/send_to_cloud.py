# Code to connect to the IoTConnect SDK and send device information to the cloud

import sys
import json
import time
import threading
from datetime import datetime
from iotconnect import IoTConnectSDK

# IoT Conect credentials
env = "Avnet"
uniqueId = "gatewayDev1"
cpId = "2f8e8b8ebd06464e97501f86292e015a"

# Global thread, data variables
tProcess = None
dataArray = []
d2cMsg = None

interval = 2


# Uses the collar information and tower information to send a message to the IoT Connect dashboard using the SDK
def send_to_iot_connect_dash(collar_info, tower_info, events):

    global tProcess, dataArray, d2cMsg
    # Update unique id with the tower id
    global uniqueId
    uniqueId = tower_info['id']
    try:
        with IoTConnectSDK(cpId, uniqueId, callbackMessage, callbackTwinMessage, env) as sdk:
            try:
                dataArray = [{
                    "data" : {
                        "tower_id": tower_info['id'],
                        "tower_area": tower_info['area'],
                        "tower_position": tower_info['position'],
                        "tower_type": tower_info['type'],
                        "tower_zone": tower_info['zone'],
                        "event_message": events
                    },
                    "uniqueId": uniqueId,
                    "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
                },{
                    "data" : collar_info,
                    "uniqueId": "collarInfo",
                    "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
                }]
                                        
                if tProcess == None and len(dataArray) > 0:
                    tProcess = threading.Thread(target = sendBackToSDK, args = [sdk, dataArray])
                    tProcess.setName("SEND")
                    tProcess.daemon = True
                    tProcess.start()
                    tProcess.join(1)
                    
                if d2cMsg != None:
                    sdk.SendACK(11, d2cMsg) # 11 : Firmware acknowledgement
                    d2cMsg = None
            except KeyboardInterrupt:
                sys.exit(0)
    except Exception as ex:
        print(ex.message)
        sys.exit(0)
        
def callbackMessage(msg):
    global d2cMsg
    print("\n--- Command Message Received ---")
    cmdType = None
    if msg != None and len(msg.items()) != 0:
        cmdType = msg["cmdType"] if msg["cmdType"] != None else None
    
    # Other Command
    if cmdType == "0x01":
        print(json.dumps(msg))
    
    # Firmware Upgrade
    if cmdType == "0x02":
        data = msg["data"] if msg["data"] != None else None
        if data != None:
            print(json.dumps(data))
            d2cMsg = {
                "guid" : data['guid'],
                "st" : 3,
                "msg" : ""
            }

def callbackTwinMessage(msg):
    if msg:
        print("\n--- Twin Message Received ---")
        #print(json.dumps(msg))
        
def sendBackToSDK(sdk, dataArray):
    global tProcess
    #print(dataArray)
    sdk.SendData(dataArray)
    time.sleep(interval)
    tProcess = None

