#!/usr/bin/python3
## Monitoring application for NOAA tide and weather data
## CO-OPS API For Data Retrieval - http://tidesandcurrents.noaa.gov/api/

## Eric Loeliger
## Started: 1/11/2016

## Variables: underscore
## Loggers: double quotes

##Change Log
## 6/4/16 - Removed while loop (switched to cron running) and added logging
## 6/26/16 - Updated API response to show numeric status code instead of full response, removed terminal print lines, added RasPi directory for logs
## 11/22/16 - Updated email properties & sendEmail to support recipients array, taken from mms_monitor.py
## 2/12/17 - Added SQL & DB to prevent sending mails during an tide event
## 3/15/17 - Added inserting, updating, & ending tide events in the DB
## 3/16/17 - Added debug mode, only sending tide emails every 3 times, API stub
## 5/7/17 - Fixed bug which says NONE in subject & email on end of tide event
## 10/24/17 - Added site URLs for reference in emails
# 1/3/18 - Added properties file, exception logging improvements, openDBConnection function

## TO DO
## Add to emails: difference increasing or decreasing, reference tide points, next high/low tide

import configparser
import logging
import requests
import json
import smtplib
from email.mime.text import MIMEText
import time
import datetime

# load properties from file
config = configparser.ConfigParser()
# THIS HAS TO BE CHANGED ON LINUX !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
config.read('cottage_monitor_properties.ini')
#config.read('//home/pi/Python_Scripts/cottage_monitor/cottage_monitor_properties.ini')

# DEBUG switch  0 = Production, 1 = debug
debugMode = int(config['general']['DebugMode'])

# Logger configuration
log_name = config['logger.config']['LogName']
log_path_linux = config['logger.config']['LogPathLinux']

logger = logging.getLogger('cottage_monitoring.py')
if debugMode == 0:
    ## Linux
    handler = logging.FileHandler('%s%s' % (log_path_linux,  log_name))
else:
    ## Windows
    handler = logging.FileHandler('%s'% log_name)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

## email properties
gmail_user = config['email']['outbound_user']
gmail_password = config['email']['outbound_password']
smtpserver = smtplib.SMTP(config['email']['outbound_smtp_server'])
recipients = [config['email']['recipients']]

## API Properties
base_url = config['noaa.api.config']['BaseURL']
station_id = config['noaa.api.config']['StationID']
datum = config['noaa.api.config']['Datum']
units = config['noaa.api.config']['Units']
time_zone = config['noaa.api.config']['TimeZone']
format1 = config['noaa.api.config']['Format']
application = config['noaa.api.config']['Application']
homepage_url = config['noaa.api.config']['HomePageURL']

# import custom modules
import cottage_monitor_sql as sql

if debugMode == 1:
    logger.info("############################# DEBUG Mode #############################")


######### to be removed once property file confirmed to be working ###########

## DEBUG switch  0 = Production, 1 = debug
#debugMode = 0

#### Logger configuration
##logger = logging.getLogger('cottage_monitoring.py')
#### Log name and directory.  Needs to be changed if running on Windows box
##handler = logging.FileHandler('//home/pi/logs/cottage_monitor/cottage_monitoring.log')
##formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
##handler.setFormatter(formatter)
##logger.addHandler(handler)
##logger.setLevel(logging.DEBUG)

## API Properties
##station_id = "8573927"
##datum= "MLLW"
##units = "english"
##time_zone = "gmt"
##format1 = "json"
##application = "loeliger_pi"
##base_url = "http://tidesandcurrents.noaa.gov/api/datagetter?"
##homepage_url = "https://tidesandcurrents.noaa.gov/stationhome.html?id="

#### Email properties
##eric = 'jon.loeliger@gmail.com'
##rick = 'rick.loeliger@gmail.com'
##if debugMode == 0:
##    recipients = [eric,rick]
##else:
##    recipients = [eric]
##gmail_user = 'loeliger.raspi@gmail.com'
##gmail_password = 'C0ttage#19'
##smtpserver = smtplib.SMTP('smtp.gmail.com:587')

## Initialize counter to keep track of how many loops the application does on a single run
loops = int(0)

## This is a generic function to send emails
def sendEmail(msg):
    logger.debug('Entered sendEmail function')
    msg['From'] = gmail_user
    msg['To'] = ", ".join(recipients)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_password)
    smtpserver.sendmail(gmail_user, recipients, msg.as_string())
    logger.debug("Mail Sent to %s" % recipients)
    


## Function calls NOAA API based on input Product and Date and returns response as dictionary
def getNoaaData(product, date):
    logger.debug("Entering getNoaaData function")
    url = ("%sstation=%s&product=%s&datum=%s&date=%s&units=%s&time_zone=%s&format=%s&application=%s" % (base_url, station_id, product, datum, date, units, time_zone, format1, application))
    logger.debug("Request URL: %s" % url)
    r = requests.get(url)
    response_text = r.text
    response_code = r.status_code

    #Cast JSON response into dict
    parsed_response = json.loads(response_text)

    #Print API response code, JSON
    logger.debug("Response Code: %s", response_code)
    logger.debug("Response: %s", json.dumps(parsed_response, indent=4, sort_keys=True))

    #Get main JSON element and print
    x = parsed_response.keys()
    logger.debug(x)
    
    logger.debug("Exiting getNoaaData function")
    return(parsed_response)


## Function returns stubbed NOAA API data
def getNoaaDataStub(product, date):
    logger.debug("Entering getNoaaDataStub function")
    url = ("%sstation=%s&product=%s&datum=%s&date=%s&units=%s&time_zone=%s&format=%s&application=%s" % (base_url, station_id, product, datum, date, units, time_zone, format1, application))
    logger.debug("Request URL: %s" % url)

    if product == 'water_level':
        ## no event
        response_text = '{"data":[{"f":"0,0,0,0","q":"p","s":"0.013","t":"2017-03-1606:42","v":"2"}],"metadata":{"id":"8573927","lat":"39.5267","lon":"-75.8100","name":"ChesapeakeCity"}}'
        ## high tide event
        #response_text = '{"data":[{"f":"0,0,0,0","q":"p","s":"0.013","t":"2017-03-1606:42","v":"5"}],"metadata":{"id":"8573927","lat":"39.5267","lon":"-75.8100","name":"ChesapeakeCity"}}'
        ## low tide event
        #response_text = '{"data":[{"f":"0,0,0,0","q":"p","s":"0.013","t":"2017-03-1606:42","v":"0"}],"metadata":{"id":"8573927","lat":"39.5267","lon":"-75.8100","name":"ChesapeakeCity"}}'
        
    elif product == 'predictions':
        response_text = '{"predictions":[{"t":"2017-03-1606:18","v":"2.833"},{"t":"2017-03-1606:24","v":"2.808"},{"t":"2017-03-1606:30","v":"2.779"},{"t":"2017-03-1606:36","v":"2.746"},{"t":"2017-03-1606:42","v":"3"},{"t":"2017-03-1606:48","v":"2.670"}]}'
    else:
        logger.error("Invalid product")

    response_code = 200

    #Cast JSON response into dict
    parsed_response = json.loads(response_text)

    #Print API response code, JSON
    logger.debug("Response Code: %s", response_code)
    logger.debug("Response: %s", json.dumps(parsed_response, indent=4, sort_keys=True))

    #Get main JSON element and print
    x = parsed_response.keys()
    logger.debug(x)
    
    logger.debug("Exiting getNoaaDataStub function")
    return(parsed_response)


## Example URLs
## http://tidesandcurrents.noaa.gov/api/datagetter?station=8573927&product=water_level&datum=MLLW&date=latest&units=english&time_zone=gmt&format=json&application=loeliger_pi
## http://tidesandcurrents.noaa.gov/api/datagetter?station=8573927&product=predictions&datum=MLLW&date=latest&units=english&time_zone=gmt&format=json&application=loeliger_pi

## Tide Reference Information
##+2ft - Over bulkhead
##+3ft - Start to worry about boats on lifts
##+4ft - Close to  deck / entering front of cottage
##+4-5ft - Enters house somewhere in here
##+6+ - We're underwater

try:
    logger.info("*****************Begin Cottage Monitoring script*********************")
    # open connection to the database
    sql.openDBConnection()

    
    ## Call API to get actual water level
    product = "water_level"
    logger.debug("Product: %s" % product)
    date = "latest"
    logger.debug("Date: %s" % date)
    
    if debugMode == 0:
        logger.debug("Calling real NOAA API")
        resp = getNoaaData(product, date)
    else:
        logger.debug("Calling stub NOAA API")
        resp = getNoaaDataStub(product, date)
    
    logger.debug("Returned to main loop")
    for x in resp['data']:
        level = float(x['v'])
        logger.info("Level: %s" % level)
        actual_time = x['t']
        logger.info("Actual Time: %s" % actual_time)



            
    ## Call API to get predicted water level
    product = "predictions"
    logger.debug("Product: %s" % product)
    date = "latest"
    logger.debug("Date: %s" % date)

    if debugMode == 0:
        logger.debug("Calling real NOAA API")
        resp = getNoaaData(product, date)
    else:
        logger.debug("Calling stub NOAA API")
        resp = getNoaaDataStub(product, date)
    
    logger.debug("Returned to main loop")
    for x in resp['predictions']:
        prediction_time = x['t']
        if prediction_time == actual_time:
            predicted_level = float(x['v'])
            logger.info("Predicted Level: %s" % predicted_level)

    ## Calculate difference in actual and predicted water level
    diff = level - predicted_level
    logger.info("Level Difference: %s" % diff)

    ## determine if currently in tide event
    if diff >= 2:
        logger.debug("Currently in a high tide event")
        tide_event = 'HIGH'
        email_word_1 = 'greater'
        email_word_2 = 'above'

    elif diff <= -2:
        logger.debug("Currently in a low tide event")
        tide_event = 'LOW'
        email_word_1 = 'less'
        email_word_2 = 'below'

    else:
        logger.info("Tide is within alert threshold - no current tide event")
        tide_event = 'NONE'



    ## retrieve latest tide event information from DB
    logger.debug("Getting latest tide_event info from DB")
    result = sql.selectTideEvent()
    logger.debug("DB Result: %s" % result)
    
    tide_event_id = result['id']
    logger.debug("tide_event_id: %s" % tide_event_id)

    ##Added for 5/7/17 for ending events
    tide_event_type = result['type']
    logger.debug("tide_event_type: %s" % tide_event_type)
    
    tide_event_count = result['occurrence_count']
    logger.debug("tide_event_count: %s" % tide_event_count)
    
    tide_event_start = result['start_timestamp']
    logger.debug("tide_event_start: %s" % tide_event_start)
    
    tide_event_end = result['end_timestamp']
    logger.debug("tide_event_end: %s" % tide_event_end)
    
    

## example result
## {'id': 6, 'type': 'HIGH', 'occurence_count': 1, 'start_timestamp': datetime.datetime(2017, 2, 12, 17, 6, 52), 'end_timestamp': None}

    ## determine if already in a tide_event
    #if result['end_timestamp'] is None:
    if tide_event_end is None:
        already_in_tide_event = 1
        logger.debug("Already in tide event")
   
    else:
        already_in_tide_event = 0
        logger.debug("No pre-existing tide event in DB")


######################################################################################################################################################
## Main tide event logic

    ## instantiate email_required variable
    email_required = 0
    emailSent = False
    
    if tide_event != 'NONE':
        if already_in_tide_event == 0:
            logger.debug("Inserting new tide event into DB")
            sql.insertTideEvent(tide_event,1)
            email_required = 1

        elif already_in_tide_event == 1:
            tide_event_count = tide_event_count + 1
            logger.debug("Updating existing tide event %s in DB" % tide_event_id)
            sql.updateTideEvent(tide_event_id,tide_event_count)

            ## check occurences, possibly send email
            if tide_event_count % 3 == 1:
                logger.info("Tide event count is divisible by 3 - email will be sent")
                email_required = 1
            else:
                logger.info("Tide event count is not divisible by 3 - no email will be sent")

    else:
        ## check to see if prior tide event needs to be closed
        if already_in_tide_event == 1:
            logger.debug("Ending %s tide event %s in DB" % (tide_event_type,tide_event_id))
            sql.endTideEvent(tide_event_id,tide_event_count)
            
            logger.info("Sending end of tide event %s email" % tide_event_id)
            today = datetime.date.today()
            #keeping old code for reference
            #msg = MIMEText("The %s tide event has ended" % tide_event_type)
            text = ("The %s tide event has ended" % tide_event_type)
            siteURL = homepage_url + station_id
            msgBody = ("%s\n\nStation Home Page: %s" % (text, siteURL))
            msg = MIMEText(msgBody)
            msg['Subject'] = 'Loeliger Cottage %s Tide Warning on %s' % (tide_event_type,today.strftime('%b %d %Y'))
            sendEmail(msg)
            emailSent = True
        else:
            logger.debug("Tide is within alert threshold - no email will be sent")




    ## generic email sending for within tide events
    if email_required == 1:
        logger.debug("Tide is %s than 2 feet %s normal - email will be sent" % (email_word_1,email_word_2))
        today = datetime.date.today()
        #keeping old code for reference
        #msg = MIMEText("The current water level is %sft which is %sft %s normal" % (level, diff, email_word_2))
        text = ("The current water level is %sft which is %sft %s normal" % (level, diff, email_word_2))
        siteURL = homepage_url + station_id
        msgBody = ("%s\n\nStation Home Page: %s" % (text, siteURL))
        msg = MIMEText(msgBody)
        msg['Subject'] = 'Loeliger Cottage %s Tide Warning on %s' % (tide_event,today.strftime('%b %d %Y'))
        sendEmail(msg)
        emailSent = True
        
    # moved to finally block
    #smtpserver.quit()    
    
        

except Exception as e:
    logger.exception("Exception occured: %s" % e)

finally:
    ## Needed to end the SMTP server here otherwise it would not work in the loop
    if emailSent == True:
        smtpserver.quit()
        logger.info("SMTP server stopped")
    sql.closeDBConnection()
    logger.info("Database connection closed")
    logger.info("*****************End Cottage Monitoring script***********************")

