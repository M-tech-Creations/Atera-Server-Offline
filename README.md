# Atera-Server-Offline
 Simple python script to create a ticket when a monitored computer (Servers by default) go offline or disconnect from Atera 

Must enter your Atera API key in api_key and enter the User ID of the account the tickets will be created under.

Right now this script will only create tickets under a set account and not automatically based on the account
of the computer belongs too. This might be added in the future.

Code is a bit messy but I am using it in prodction and works well.

Uses the following libarys:
json, 
requests, 
datetime, 
time, 
tqdm
