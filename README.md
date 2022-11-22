# visa_rescheduler
US VISA (ais.usvisa-info.com) appointment re-scheduler - Canada multithread adaptation

## Prerequisites
- Google Chrome installed (to be controlled by the script)
- Python v3 installed (for running the script)
- API token from Pushover (for notifications)

## Accounts Setup
- Create several fake accounts, for each account register until 
you reach the payment part
- For each account create separate config 'config1.ini', 'config2.ini', ...
- Depending on the amount of accounts, change *amount_of_accounts* in run.py
- You should change *sleep_time* in run.py and *RETRY_TIME* in visa.py as well

*sleep_time* - the time difference between bots  
*RETRY_TIME* - the time difference between attempts for each bot  

So if you have 10 accounts and want to check the site every minute, set *amount_of_accounts* to 10, *sleep_time* to 60 
and *RETRY_TIME* to 600

## Executing the script
- Simply run `python3 run.py`
- That's it!

## Tips
- Do not use your personal account, it might get temporally blocked
- This script won't automatically reschedule your appointment, it'll only send you the notification about the available 
timeslot
- You can change line 145 in visa.py to follow your conditions  
```if 'October, 2022' in dates or 'November, 2022' in dates:```
