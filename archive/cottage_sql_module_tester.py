## dedicated tester for mms_monitor_sql
import cottage_monitor_sql as sql

print("#####SQL debugger started#####")
system = 'Test System'

## tide_events
##id,type,occurence_count,start_timestamp,end_timestamp
## type to be HIGH or LOW

result = sql.selectTideEvent()
print("Select result: %s" % result)

type = "HIGH"
occurence_count = 1

print("SQL data: type=%s, occurence_count=%s" % (type,occurence_count))
sql.insertTideEvent(type,occurence_count)


occurence_count = 3
id = 2

print("SQL data: occurence_count=%s" % (occurence_count))
sql.updateTideEvent(id,occurence_count)


occurence_count = 4
id = 1

print("SQL data: occurence_count=%s" % (occurence_count))
sql.endTideEvent(id,occurence_count)

print("Closing DB connection")
sql.closeDBConnection()

print("#####SQL debugger ended#####")
