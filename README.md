# Twilio Facebook Notification
A python script to receive your Facebook notifications on your mobile via SMS for free.

## How it works
A python script is used to parse the Facebook notification xml feed.

Twilio SMS API is used to send SMS.

The script checks the notifications every 30 seconds.


## Configuration
1. First login your Facebook account
2. Visit [www.facebook.com/notifications](http://www.facebook.com/notifications) and click the **RSS** link
3. From the address bar, note down the values of **id=XXXXXXXXXXXXXXX** and **key=XXXXXXXXXXXXX**
4. Go to the folder where you downloaded the script
5. Open *config.conf* file
6. Substitute the values of **user_id** with your **id** and **key** with your **key**
7. Create a trial account at [www.twilio.com](http://www.twilio.com)
8. Go to [www.twilio.com/user/account](http://www.twilio.com/user/account) and Click on **Show API Credentials** link
9. Note down your **account sid** and **auth token**
10. Substitute the values of **account_sid** with your **account sid** and **auth_token** with your **auth token** in the config file
11. Verify the phone number to which you want to receive SMS
12. Substitute the values of **to_phone** and **from_phone** with your verified phone number

## Installation
Remember, you must have **python3** and **pip3** installed.
```
$ git clone https://github.com/sandipbgt/twilio-fb-notification
$ cd twilio-fb-notification
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python app.py
```


## How to run
From your terminal type `python3 app.py` or `python app.py` depending upon how your install python on your system