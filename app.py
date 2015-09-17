""" Get Facebook notifications on your mobile via SMS for free
"""

import time
import configparser
import urllib.request
import urllib.parse
import csv
import xml.etree.ElementTree as ET
from urllib.error import URLError, HTTPError
from twilio.rest import TwilioRestClient


def read_configfile():
    """Read the config file

    :returns: The ConfigParser object
    """
    c = configparser.ConfigParser()
    c.read("config.conf")

    return c


def check_config_values():
    """Checks the configuration file for settings

    :returns: The ConfigParser object
    """
    config = read_configfile()
    if config.get('DEFAULT', 'user_id') == "your user id here":
        print("Please setup facebook user_id in config file")
        exit()
    elif config.get('DEFAULT', 'key') == 'your key here':
        print("Please setup facebook key in config file")
        exit()

    return config


def get_feed(url):
    """Get feed data from feed url

    :param str url: full feed url of Facebook notification
    :returns: The feed data as XML string
    """
    try:
        print("Please wait...")
        response = urllib.request.urlopen(feed_url)
        return response.read()
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)


def parse_feed(xml_string):
    """Parse XML string

    :param str xml_string: the XML string
    :returns: The notifications list
    """
    # read configuration from the config file
    config = read_configfile()
    config_last_build_date = config.get('DEFAULT', 'last_build_date')
    config_max_notification = config.get('DEFAULT', 'max_notification')

    # notifications list
    notifications = []

    root = ET.fromstring(xml_string)
    fb_last_build_date = root[0][7].text
    post_items = root[0].findall('item')

    count = 1
    for item in post_items:
        if count > int(config_max_notification):
            break

        notification = {
            "guid": item.find('guid').text,
            "title": item.find('title').text,
            "description": item.find('description').text,
            "pub_date": item.find('pubDate').text,
            "sent": False
        }

        notifications.append(notification)
        count = count + 1

    if fb_last_build_date > config_last_build_date:
        write_notifications_to_file(notifications)
        config.set('DEFAULT', 'last_build_date', fb_last_build_date)
        with open('config.conf', 'w') as configfile:
            config.write(configfile)

    return notifications


def sendsms(message):
    """Send SMS via Twilio SMS API

    :param str message: SMS body to send
    """

    # read configuration from the config file
    config = check_config_values()
    account_sid = config.get('DEFAULT', 'twilio_account_sid')
    auth_token = config.get('DEFAULT', 'twilio_auth_token')
    to_phone = config.get('DEFAULT', 'twilio_to_phone')
    from_phone = config.get('DEFAULT', 'twilio_from_phone')

    client = TwilioRestClient(account_sid, auth_token)
    print("Sending this notification as SMS")
    message = client.messages.create(
        body=message, to=to_phone, from_=from_phone)
    print("SMS sent")
    # print(message.sid)


def write_notifications_to_file(notifs):
    """Write notifications list to a file

    :param list notifs: The notification list
    """
    with open('notifications.csv', mode='w', encoding='utf-8') as notif_file:
        notif_csv_writer = csv.writer(notif_file)

        for notif in notifs:
            notif_csv_writer.writerow(
                [notif['guid'], notif['title'], notif['pub_date'], notif['sent']])


def read_notifications_from_file():
    """Read notifications from file

    :returns list notifications: The notifications list
    """
    notifications = []
    f = open("notifications.csv", encoding='utf-8')
    for row in csv.reader(f):
        notifications.append(row)
    return notifications


def show_notifications(notifs):
    """Show notifications on the terminal and send sms

    :param list notifs: The notifications list
    """
    total_notif = len(notifs)
    file_notifs = read_notifications_from_file()

    has_new_notif = False
    if total_notif > 0:
        count = 1
        sn = 1
        for notif in notifs:
            sent = file_notifs[count - 1][3]
            if sent == 'False':
                has_new_notif = True
                print("%d) %s" % (sn, notif['title']))
                print("%s %s" % (" " * 5, notif['pub_date']))
                sendsms(notif['title'])
                time.sleep(8)
                notifs[count - 1]['sent'] = True
                write_notifications_to_file(notifs)
                sn = sn + 1
            count = count + 1
            total_notif = sn - 1

        if has_new_notif:
            print("Total notifications (%d)" % total_notif)
        else:
            print("No new notifications")

    print("Last updated at: %s\n" % time.ctime())

# read configuration from the config file
config = check_config_values()
user_id = config.get('DEFAULT', 'user_id')
key = config.get('DEFAULT', 'key')
last_updated = config.get('DEFAULT', 'last_build_date')
config_sleep_time = float(config.get('DEFAULT', 'update_interval'))

params = urllib.parse.urlencode(
    {'id': user_id, 'viewer': user_id, 'key': key, 'format': 'rss20'})
feed_url = "https://www.facebook.com/feeds/notifications.php?%s" % params

first_run = True

# run forever :P
while(True):
    # retrieve xml feed string from feed url
    xml_string = get_feed(feed_url)

    # parse xml string to get notifications list
    notifs = parse_feed(xml_string)

    # if this is the first run, write notifications to file
    if first_run:
        write_notifications_to_file(notifs)
        first_run = False

    # show notifications in terminal and also send SMS
    show_notifications(notifs)

    # sleep for some time before sending next request
    time.sleep(config_sleep_time)
