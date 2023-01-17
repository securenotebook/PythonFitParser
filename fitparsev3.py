from fitparse import FitFile
from datetime import timedelta
from influxdb import InfluxDBClient
import os, time,subprocess, sys
import ipcalc
from rich import inspect

from dotenv import load_dotenv
load_dotenv()

def log(string):
    print(string, flush=True)

# wait 5 second as the DB maybe not be up yet. 
time.sleep(5)

# Load Enviroment
log("Loading .env")
DEV = os.getenv('FIT_MODE')
INFLUX_HOST = os.getenv('INFLUX_HOST'+DEV)
GRAFANA_URL = os.getenv('GRAFANA_URL'+DEV)

log("Running in Mode: " + DEV)
log("Connection to infuxdb: " + str(INFLUX_HOST))

client = InfluxDBClient(host=INFLUX_HOST, port=8086, username='admin', password='admin') # Connect to the InfluxDB instance

log(f"Dropping DB Strava")
client.drop_database('strava')      # Drop Old DB

log(f"Creating DB Strava")
client.create_database('strava')    # Create DB

dir = os.getcwd() + "/fitFiles/"
dir_list = os.listdir(dir)

fit_files = []
for x in dir_list:
    if x.endswith(".fit"):
        path = dir + x
        newFitFile = FitFile(path)
        fit_files.append(newFitFile)

grafana_link = ""
min_timestamp =0
max_timestamp =0

#Loop through the fit files
for file in fit_files: 
    
    #get device details
    deviceDetails   = file.messages[0].get_values()
    manufacturer    = deviceDetails['manufacturer']
    serial          = deviceDetails['serial_number']
    
    manufactor = f"{manufacturer}_{serial}" 

    log(f"Processing file, manufacturer {manufacturer}, Serial: {serial}")
    
    
    # Iterate through all the data messages in the file
    dataPoints=[]
    for record in file.get_messages("record"):
        
        power = record.get_value('power') # Get the power data
        cad = record.get_value('cadence') # Get the power data

        if power == None: power=0 # replace none with zero
        if cad == None:cad = 0
        
        timestamp = record.get_value('timestamp') # Get the timestamp
        # utc = timestamp  + timedelta(hours=1)
        
        epoch = int(timestamp.timestamp()*1000)
        
        # log(epoch)
        if min_timestamp == 0: min_timestamp = epoch
        if epoch < min_timestamp : min_timestamp = epoch
        if epoch > max_timestamp: max_timestamp = epoch

       
        # record.get_value('timestamp').
        
        #make some minor adjustments to timestamps
        # 
        # if id=="assioma": timestamp = timestamp  - timedelta(seconds=4)
        
        #build the data point to write
        data = {'measurement': 'strava',
                'time': timestamp,
                'tags': { 'powerMeter': manufacturer},
                 'fields':   {'power': power, 'cadence':cad}
                }

        dataPoints.append(data)
        
    log(f"{id} - Data Loaded - Writing to influx")
    client.write_points(dataPoints, database='strava')
    log(f"{id} Data written")

GRAFANA_URL=GRAFANA_URL.replace("{min}", str(min_timestamp))
GRAFANA_URL=GRAFANA_URL.replace("{max}", str(max_timestamp))
log(GRAFANA_URL)