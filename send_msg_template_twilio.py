
#%%
import json
import requests

from twilio.rest import Client


# Your Account SID and Auth Token from twilio.com/console
account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

# message = client.messages.create(
#                               content_sid='HX581aabc550bc27369a4b3d0798cea7d6',
#                               from_='MG84961d0ca1b0f24210bf1193c68bdb81',
#                               content_variables=json.dumps({}),
#                               to='whatsapp:+6594746442'
#                           )


# # Message with quick-reply button in Mandarin
# message = client.messages.create(
#                               content_sid='HX402bd0ba00d12a92d66ba30a4078cd19',
#                               from_='MG84961d0ca1b0f24210bf1193c68bdb81',
#                               content_variables=json.dumps({}),
#                               to='whatsapp:+6594746442'
#                           )

# # Message with Mandarin text and quick-reply button in Mandarin
# message = client.messages.create(
#                               content_sid='HXdc79b2e6918ad0ba4db4e3446f0ca30c',
#                               from_='MG84961d0ca1b0f24210bf1193c68bdb81',
#                               content_variables=json.dumps({
#                                   '1': '31 May 2024'
#                               }),
#                               to='whatsapp:+6594746442'
#                           )

# # Message with Mandarin button and no Mandarin text in message body
# # Note: this shows that we can use the same messaging service to send different templates
# message = client.messages.create(
#                               content_sid='HX402bd0ba00d12a92d66ba30a4078cd19', # content_sid: string variable of ID of content template 
#                               from_='MG84961d0ca1b0f24210bf1193c68bdb81',       # from_: string variable of messaging service ID
#                               to='whatsapp:+6596309938'
#                           )


# # Test if it's possible to 'direct' incoming message to webhook if no whatsapp sender associated with the messaging service
from_whatsapp_number = 'whatsapp:+6585529684'
to_whatsapp_number = 'whatsapp:+6596309938'
messaging_service_sid = 'MG004e7e3544c7a92a6687e98eeaae8a11' # test-messaging-service-2
content_sid = 'HXdc79b2e6918ad0ba4db4e3446f0ca30c'
content_variables = json.dumps({
    '1': '31 May 2024'
    }) 

message = client.messages.create(
    from_=from_whatsapp_number,
    to=to_whatsapp_number,
    messaging_service_sid=messaging_service_sid,
    content_sid=content_sid,
    content_variables=content_variables
)

# # Failed code
# message = client.messages.create(
#     from_='whatsapp:+6585529684',
#     body="Hello world, this is a test message from NUS Department of Economics. If you receive this message, press on the 'Yes_or_No' button.",
#     to='whatsapp:+6596309938'
# )

# # Failed code from GPT
# # Template name and language
# template_name = 'test_1'
# template_language = 'en'
# message = client.messages.create(
#     from_='whatsapp:+6585529684',  # Your Twilio WhatsApp-enabled number
#     to='whatsapp:+6596309938',  # Recipient's number
#     body=' ',  # Provide a body with a space to avoid the error
#     media_url=[],  # Provide an empty list if no media URL is used
#     status_callback=None,  # Provide None if no status callback is needed
#     persistent_action=[
#         {
#             'type': 'whatsapp_template',
#             'parameters': {
#                 'name': template_name,
#                 'language': {
#                     'code': template_language
#                 }
#             }
#         }
#     ]
# )

print(message.sid)

#%%

# Retrieve messages sent to Twilio phone number
messages = client.messages.list(to = 'whatsapp:+6585529684')

# Check number of messages received
len(messages)

# Check the meta data of the first message
messages[0].__dict__

# Get message body of the first message 
messages[0].__dict__['body']

#%%

# Retrieve media from an inbound message sent by participant
BASE_URL = "https://%s:%s@api.twilio.com" % (account_sid, auth_token)

messages = client.messages.list(to = 'whatsapp:+6585529684')
message = messages[0]
m_sid = message.sid

msg = client.messages(m_sid).fetch()
medias = msg.media.list()
for media in medias:
    media_inst = client.messages(m_sid).media(media.sid).fetch()
    uri = requests.get(BASE_URL + media_inst.uri).json()
    uri2 = requests.get(BASE_URL + uri['uri'].replace('.json', ''))
    phone_number = msg.__dict__['from_'].lstrip('whatsapp:')
    with open(phone_number + "_" + media_inst.uri.split("/")[-1].replace(".json", ".png"), "wb") as f:
        f.write(uri2.content)
        f.close()

#%%