# NOAA Tide Level Monitoring

I created this script to monitor the tide levels at my family's cottage, based on the NOAA CO-OPS APIs, and alert when the tides are above/below a certain threshold.  

## Getting Started

This app consists of 4 main components:
   1. main python script
   2. SQL interraction python script
   3. ini properties file
   4. MySQL database

### Prerequisites

Non-standard Python Modules Required:
- requests (for making API calls)
- pymysql (for MySQL DB interraction)

MySQL database installed

.ini Properties file




## Known Issues

1. On the first run, there must be at least one row in the DB.  Workaround is just to manually add a dummy row. 