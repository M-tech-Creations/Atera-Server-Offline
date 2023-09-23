# Please set api_key
# Adjust expire in days for ticket creation threshold
# Adjust sleep_time in seconds for api rate limit threshold

# Use at own risk
# Created for Python 3.6
# pip install tqdm
# pip install requets

# Created by Mario Avenoso

import json
import requests
from datetime import datetime
import time
from tqdm import tqdm



### BEGIN VARIABLES ###

sleep_time = 30  # Time in seconds to Sleep between checking alterts

userID = 11 # User ID to use to create the ticket

api_key = '[API KEY]'
api_url_base = 'https://app.atera.com/api/v3/'

### END VARIABLES ###

headers = {'Accept': 'application/json', 'X-API-KEY': '%s' % api_key}

oldAlerts = []


def storeOldAlerts(TID, title):
    oldAlerts.append([TID, title])


def checkOldAlerts(title): # Check to see if Alert ID is stored or not.
    #print("Checking " + str(AID))
    if oldAlerts:
        for item in oldAlerts:
            #print("item in check old alerts " + str(item[0]) + "and the AID " + str(AID))
            if item[1] == title:
                return True

    return False


def get_ticket_status(TID):
    try:
        url = api_url_base + 'tickets/' + str(TID)
        #payload = {'EndUserID': str(client), 'TicketTitle': title, 'Description': description}
        r = requests.get(url=url, headers=headers)
        data = json.loads(r.text)
        if data['TicketStatus'] != "Open":
            return True
        else:
            return False

    except Exception as e:
        print(e)
        return False


def removeOldAlerts():
    """
    Checks over each stored alert ticket and see if it is still open, removing tickets that are not active
    """
    if oldAlerts:
        t = tqdm(oldAlerts, desc='Clearing old alerts', leave=False)
        for item in t:
            if get_ticket_status(item[0]):
                oldAlerts.remove(item)
            time.sleep(1)  # Small delay to not overload API


def createTicket(client, title, description):
    try:
        url = api_url_base + 'tickets/'
        payload = {'EndUserID': str(client), 'TicketTitle': title, 'Description': description}
        r = requests.post(url, data=payload, headers=headers)
        data = json.loads(r.text)
        return True, data['ActionID']  # Returns the generated ticket number
    except Exception:
        return False, -1


def clear_alert(AID):
    """
    Used to clear alerts from Atera's system. Without clearing the alert, every time the alerts are checked the same
    alert will be read trying to create another new ticket. Must be done as you can't mark alert as read with the API
    :param AID: ID number of alert to be deleted
    """
    try:
        #print("Deleting " + str(AID))
        url = api_url_base + 'alerts/' + str(AID)
        r = requests.delete(url=url, headers=headers)
    except Exception as e:
        print(e)


def checkAlerts():
    try:
        url = api_url_base + 'alerts/'
        resp = requests.get(url=url, headers=headers)
        data = json.loads(resp.text)
        #print(data)
        for item in data['items']:
            if item['Severity'] == "Critical":
                if item['Title'] == "Machine status unknown":
                    #print("Output from check alerts: " + str(checkOldAlerts(item['AlertID'])))
                    title = item['DeviceName'] + " For " + item['CustomerName'] + " IS OFFLINE!"  # Title used for Ticket Creation
                    if not checkOldAlerts(title):
                        # print(item)
                        # print(type(item['AlertID']))
                        # print(item['AlertID'])


                        description = "As of " + datetime.now().strftime("%m-%d-%Y %I:%M %p") + ", the system " + item['DeviceName'] + " belonging to " + item['CustomerName'] + \
                                      " has been marked as being OFFLINE. Please check on the status of the system and or client site for an outage."
                        result, ticket_id = createTicket(userID, title, description)
                        if result:
                            print("Alert Logged! for " + item['DeviceName'] + " of " + item['CustomerName'])
                            storeOldAlerts(ticket_id, title)
                            clear_alert(item['AlertID'])  # Clears alert, otherwise it will keep trying to
                                                          # create a ticket
                        else:
                            print("Unable to Log Alert for " + item['DeviceName'] + " of " + item['CustomerName'] + "!")
                    else:
                        print("Alert already logged! For " + item['DeviceName'] + " of " + item['CustomerName'])
                        clear_alert(item['AlertID'])
                # print(item)
        return True
    except Exception as e:
        print(e)
        return False


def main():
    print("Starting System offline Alert Monitor!")


    while True:
        # print(oldAlerts)
        if not checkAlerts():
            print("There was an error checking alerts!")
        removeOldAlerts()
        t = tqdm(range(sleep_time), desc='Time Till Next Update', leave=False)
        for number in t:
            time.sleep(1)



if __name__ == "__main__":
    main()
