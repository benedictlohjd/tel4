
#%%

import time
import requests
import json
import os
import numpy as np
import pandas as pd

from datetime import timedelta, datetime
from dotenv import load_dotenv                # For loading environment variables
from pathlib import Path
from ratelimit import limits, sleep_and_retry # To limit number of API calls per unit of time 
from typing import Tuple, Any                      
from tqdm import tqdm                         # To provide progress bars
from twilio.rest import Client

#%%

@sleep_and_retry
@limits(calls=200, period=timedelta(seconds=60).total_seconds())
def send_intro_msg(content_sid: str, from_: str, date_contacted: str, to: str) -> Any: # TODO: how to properly annotate this?
    number = 'whatsapp:+65' + to
    message = client.messages.create(
        content_sid=content_sid, # HXXXXXXXXXXXXXXXXXXXXXXXXXX; WhatsApp content template ID
        from_= from_, # MGXXXXXXXXXXXXXXXXXXXXXXXXXXX; messaging service ID
        content_variables=json.dumps({
            '1': date_contacted
        }),
        to=number
        )
    return message

#%%

parent_path = Path(__file__).parent
env_path = parent_path / ".env"
data_path = parent_path / "data" / "subjects.csv"

#%%
# Set Twilio whatsapp content template ID and Twilio messaging service ID
content_sid = ''
messaging_service = ''
#%%
# Load twilio tokens


load_dotenv(env_path)

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

#%%

df_intro = pd.read_csv(data_path)

#%%

msg_id = list()
status = list()
error_code = list()
date_updated = list()

# Send introduction messages
for i in tqdm(range(len(df_intro))):
    contact_number, date_contacted = df_intro.loc[i, 'Mobile'], df_intro.loc[i, 'date_contacted']
    msg = send_intro_msg(
        content_sid, messaging_service, date_contacted, contact_number
    )
    msg_id.append(msg.sid)
    status.append(msg.__dict__['status'])
    error_code.append(msg.__dict__['error_code'])
    date_updated.append(
        msg.__dict__['date_updated'].strftime("%d/%m/%Y %H:%M:%S")
    )

#%%

# Create output dataframe 
out = pd.DataFrame({
    'message_ID': msg_id,
    'status': status,
    'error': error_code,
    'date_updated': date_updated 
})

out_filename = "out" + "_" + datetime.datetime.now().strftime("%d-%m-%Y")

out.to_csv(out_filename)