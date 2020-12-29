## eric.loeliger@gmail.com

## Change Log
## 11/27/16 - Added logging config for local log (temporary) and environment column
## 11/28/16 - Fixed multiple query issues with c.close() and added closeDBConnection() function

## 2/12/17 - cottage_monitor_sql started
## 3/16/17 - Moved ending statement for select to after return
## 5/7/17 - Moved logging into main cottage_monitoring log
# 1/3/17 - Added properties file, module importing improvements (for future code simplification)

## 12/28/20 - refactored to use SQLite3, changed name to tide_monitor*, removed all windows configs, removed debug mode
##              note: because SQLite does not reccomend autoincrement's, the unique ID was moved to the start_timestamp

from __main__ import *
import sqlite3

script_path = "//home/pi/Python_Scripts/tide_monitor/"
script_name = "tide_monitor"

# load properties from file
config = configparser.ConfigParser()
config.read('%s%s_properties.ini' % (script_path, script_name))

# Logger configuration
log_name = config['logger.config']['LogName']
log_path_linux = config['logger.config']['LogPathLinux']

logger = logging.getLogger('%s_sql.py' % script_name)
## Linux
handler = logging.FileHandler('%s%s' % (log_path_linux,  log_name))
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

## opens the DB connection
def openDBConnection():
    logger.info("***Begin openDBConnection function***")
    connection = sqlite3.connect('%sdata.db' % script_path)
    connection.set_trace_callback(logger.debug)
    connection.row_factory=sqlite3.Row
    c = connection.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS "tide_events" ("id" INTETER NOT NULL,"type" VARCHAR(50) NOT NULL,"occurrence_count" INTEGER NOT NULL,"start_timestamp" INTEGER NOT NULL PRIMARY KEY,"end_timestamp" INTEGER NULL)')
    connection.commit()
    logger.info("***End openDBConnection function***") 
    return connection


## select latest tide event from the tide_events table
def selectTideEvent(connection):
    logger.info("***Begin selectTideEvent function***")
    c = connection.cursor()
    # Create a new record
    sql = "SELECT * from tide_events order by start_timestamp desc limit 1"
    c.execute(sql)
    result = c.fetchone()
    logger.debug("Result: %s" % result)
    
    # check if no results are returned.  if not, insert one (only used on first run)
    if result == None:
        now_sql = 'SELECT strftime("%s","now")'
        sql = 'INSERT INTO tide_events (id, "type", occurrence_count, start_timestamp, end_timestamp) VALUES((SELECT strftime("%s","now")), "LOW", 1, (SELECT strftime("%s","now")), (SELECT strftime("%s","now")))'
        c.execute(sql)
        connection.commit()

        sql = "SELECT * from tide_events order by start_timestamp desc limit 1"
        c.execute(sql)
        result = c.fetchone()
        logger.debug("Result: %s" % result)

    c.close()


## example result
## {'id': 6, 'type': 'HIGH', 'occurrence_count': 1, 'start_timestamp': datetime.datetime(2017, 2, 12, 17, 6, 52), 'end_timestamp': None}

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    ##connection.commit()
    logger.info("***End selectTideEvent function***")
    return(result)



## Inserts new tide event into the tide_events table
def insertTideEvent(connection, type,occurrence_count):
    logger.info("***Begin insertTideEvent function***")
    c = connection.cursor()
    # Create a new record
    sql = "INSERT INTO tide_events (id,type,occurrence_count,start_timestamp)  VALUES((SELECT strftime('%s','now')),%s,%s,(SELECT strftime('%s','now')))"
    result = c.execute(sql, (type,occurrence_count))
    c.close()
    logger.debug("Result: %s" % result)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End insertTideEvent function***")

	
## update an already existing tide event (increases the occurence count)
def updateTideEvent(connection, id,occurrence_count):
    logger.info("***Begin updateTideEvent function***")
    c = connection.cursor()
    # Update an existing tide record
    sql = "UPDATE tide_events SET occurrence_count = %s where start_timestamp = %s"
    result = c.execute(sql, (occurrence_count,id))
    c.close()
    logger.debug("Result: %s" % result)
		
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End updateTideEvent function***")

	
## end an already existing tide event
def endTideEvent(connection, id,occurrence_count):
    logger.info("***Begin endTideEvent function***")
    c = connection.cursor()
    # Update an existing tide record
    sql = "UPDATE tide_events SET occurrence_count = %s, end_timestamp = (SELECT strftime('%s','now')) where start_timestamp = %s"
    result = c.execute(sql, (occurrence_count,id))
    c.close()
    logger.debug("Result: %s" % result)
		
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End endTideEvent function***")
	
	
## Closes the DB connection once all activities are done
def closeDBConnection(connection):
    logger.info("***Begin closeDBConnection function***")
    connection.close()
    logger.info("***End closeDBConnection function***")

