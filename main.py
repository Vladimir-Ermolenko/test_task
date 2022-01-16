# Curiosity landing date: 2012-08-06 (photos start from the same day) still working
# Opportunity landing date: 2004-01-25 (photos start from 2004-01-25) up to 2018-06-11
# Spirit landing date: 2004-01-04 (photos start from 2004-01-05) up to 2010-03-21

# To run the program from IDE you can add the date in YYYY-MM-DD format as the last arg of "request" function
# To run program from terminal you need to type the the date in YYYY-MM-DD format as the argument after "main.py"
import sys
from defs import request, update

link = "https://api.nasa.gov/mars-photos/api/v1/rovers/{}/photos"
api_key = "e3lIHQIvwHpVomPAEiFKVVWRB9CLOl7kd7S1ncCA"
if len(sys.argv) == 2:
    date = sys.argv[1]
    request(link, api_key, date)
else:
    print("If you want to get the data from the exact day, please, pass the date as the argument")
    print("The date is set to today" + "\n")
    request(link, api_key)
