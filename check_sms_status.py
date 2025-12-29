#!/usr/bin/env python
"""Check the status of the SMS we just sent"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

# The message SID from our test
message_sid = 'SM08cca818490a805e6507c2031d0ea6a3'

message = client.messages(message_sid).fetch()

print(f"📱 Message Status Check")
print(f"SID: {message.sid}")
print(f"Status: {message.status}")
print(f"To: {message.to}")
print(f"From: {message.from_}")
print(f"Date Sent: {message.date_sent}")

if message.error_code:
    print(f"\n❌ Error Code: {message.error_code}")
    print(f"❌ Error Message: {message.error_message}")
else:
    print("\n✅ No errors detected")

print(f"\nStatus meanings:")
print(f"  - queued: Waiting to be sent")
print(f"  - sent: Handed off to carrier")
print(f"  - delivered: Confirmed delivered to phone")
print(f"  - failed: Could not deliver")
print(f"  - undelivered: Carrier couldn't deliver")
