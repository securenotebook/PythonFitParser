from fitHelperMethods import *

client = getInfluxConnection()
        
if client == False:
    log(f"Could not connect to database {INFLUX_HOST} exiting")
    exit(0)


def loadFitFiles():

    #Load .fit files from fitFiles dir
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
            
            # create start and stop time stamp per file
            if min_timestamp == 0: min_timestamp = epoch
            if epoch < min_timestamp : min_timestamp = epoch
            if epoch > max_timestamp: max_timestamp = epoch

        
            #build the data point to write
            data = {'measurement': 'strava',
                    'time': timestamp,
                    'tags': { 'powerMeter': manufacturer},
                    'fields':   {'power': power, 'cadence':cad}
                    }

            dataPoints.append(data)
            
        log(f"{manufacturer} - Data Loaded - Writing to influx")
        client.write_points(dataPoints, database='strava')
        log(f"{manufacturer} Data written")

    GRAFANA_URL = os.getenv('GRAFANA_URL'+DEV)
    GRAFANA_URL=GRAFANA_URL.replace("{min}", str(min_timestamp))
    GRAFANA_URL=GRAFANA_URL.replace("{max}", str(max_timestamp))
    log(GRAFANA_URL)

while True:
    loadFitFiles()
    time.sleep(60)