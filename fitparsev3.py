from fitparse import FitFile
from datetime import timedelta
from influxdb import InfluxDBClient


client = InfluxDBClient(host='192.168.1.155', port=8086) # Connect to the InfluxDB instance
client.drop_database('strava')      # Drop Old DB
client.create_database('strava')    # Create DB

# create list of fitFiles
files = {"quarq":FitFile('FTP-Quarq.fit'),  "kickr":FitFile('FTP-Kickr.fit'),  "assioma": FitFile('FTP-Assioma.fit')}

#Loop through file
for id in files: 
    file = files[id]

    print(f"Processing file {id}")
    
    # Iterate through all the data messages in the file
    dataPoints=[]
    for record in file.get_messages("record"):
        
        power = record.get_value('power') # Get the power data

        if power == None: power=0 # replace none with zero

        timestamp = record.get_value('timestamp') # Get the timestamp
        
        #make some minor adjustments to timestamps
        if id=="kirkr": timestamp = timestamp  - timedelta(seconds=3)
        if id=="quarq": timestamp = timestamp  - timedelta(seconds=2)
        
        #build the data point to write
        data = {
                'measurement': 'strava',
                'time': timestamp,
                'tags': { 'powerMeter': id},
                'fields': {'power': power}
            }

        dataPoints.append(data)
        
    print(f"{id} - Data Loaded - Writing to influx")
    client.write_points(dataPoints, database='strava')
    print(f"{id} Data written")