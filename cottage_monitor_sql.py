## cottage_monitor_sql.py
## based on mms_monitor_sql.py
## eric.loeliger@gmail.com

## Change Log
## 11/27/16 - Added logging config for local log (temporary) and environment column
## 11/28/16 - Fixed multiple query issues with cursor.close() and added closeDBConnection() function

## 2/12/17 - cottage_monitor_sql started
## 3/16/17 - Moved ending statement for select to after return
## 5/7/17 - Moved logging into main cottage_monitoring log
# 1/3/17 - Added properties file, module importing improvements (for future code simplification)

from __main__ import *
import pymysql

# load properties from file
config = configparser.ConfigParser()
# THIS HAS TO BE CHANGED ON LINUX !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#config.read('cottage_monitor_properties.ini')
config.read('//home/pi/Python_Scripts/cottage_monitor/cottage_monitor_properties.ini')

# DEBUG switch  0 = Production, 1 = debug
debugMode = int(config['general']['DebugMode'])

# Logger configuration
log_name = config['logger.config']['LogName']
log_path_linux = config['logger.config']['LogPathLinux']

logger = logging.getLogger('cottage_monitor_sql.py')
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

# Database properties
db_host_win = config['database.windows']['host']
db_user_win = config['database.windows']['user']
db_pwd_win = config['database.windows']['password']
db_name_win = config['database.windows']['db']

db_host_linux = config['database.linux']['host']
db_user_linux = config['database.linux']['user']
db_pwd_linux = config['database.linux']['password']
db_name_linux = config['database.linux']['db']

if debugMode == 1:
    logger.info("############################# DEBUG Mode #############################")

## opens the DB connection
def openDBConnection():
    logger.info("***Begin openDBConnection function***")
    global connection
    
    # Connect to the database
    if debugMode == 0:
        ## Linux
        
        connection = pymysql.connect(host='%s' % db_host_linux, port=3306,
                                 user='%s' % db_user_linux,
                                 passwd='%s' % db_pwd_linux,
                                 db='%s' % db_name_linux,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    else:
        ## Windows
        #global connection
        connection = pymysql.connect(host='%s' % db_host_win,
                                 user='%s' % db_user_win,
                                 passwd='%s' % db_pwd_win,
                                 db='%s' % db_name_win,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    logger.info("***End openDBConnection function***") 


## select latest tide event from the tide_events table
def selectTideEvent():
    logger.info("***Begin selectTideEvent function***")
    with connection.cursor() as cursor:
        # Create a new record
        sql = "SELECT * from tide_events order by id desc limit 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        logger.debug("Query: %s" % cursor._last_executed)
        logger.debug("Result: %s" % result)

## example result
## {'id': 6, 'type': 'HIGH', 'occurrence_count': 1, 'start_timestamp': datetime.datetime(2017, 2, 12, 17, 6, 52), 'end_timestamp': None}

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    ##connection.commit()
    logger.info("***End selectTideEvent function***")
    return(result)



## Inserts new tide event into the tide_events table
def insertTideEvent(type,occurrence_count):
    logger.info("***Begin insertTideEvent function***")
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO tide_events (type,occurrence_count,start_timestamp)  VALUES(%s,%s,NOW())"
        result = cursor.execute(sql, (type,occurrence_count))
        cursor.close()
        logger.debug("Query: %s" % cursor._last_executed)
        logger.debug("Result: %s" % result)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End insertTideEvent function***")

	
## update an already existing tide event (increases the occurence count)
def updateTideEvent(id,occurrence_count):
    logger.info("***Begin updateTideEvent function***")
    with connection.cursor() as cursor:
        # Update an existing tide record
        sql = "UPDATE tide_events SET occurrence_count = %s where id = %s"
        result = cursor.execute(sql, (occurrence_count,id))
        cursor.close()
        logger.debug("Query: %s" % cursor._last_executed)
        logger.debug("Result: %s" % result)
		
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End updateTideEvent function***")

	
## end an already existing tide event
def endTideEvent(id,occurrence_count):
    logger.info("***Begin endTideEvent function***")
    with connection.cursor() as cursor:
        # Update an existing tide record
        sql = "UPDATE tide_events SET occurrence_count = %s, end_timestamp = NOW() where id = %s"
        result = cursor.execute(sql, (occurrence_count,id))
        cursor.close()
        logger.debug("Query: %s" % cursor._last_executed)
        logger.debug("Result: %s" % result)
		
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End endTideEvent function***")
	
	
## Closes the DB connection once all activities are done
def closeDBConnection():
    logger.info("***Begin closeDBConnection function***")
    connection.close()
    logger.info("***End closeDBConnection function***")

