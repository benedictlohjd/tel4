
#%%

import logging
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
from twilio.rest import Client, api
from sys import exit

#%%

dt_of_log = datetime.now().strftime('%d%m%Y_%H%M%S')
log_file_name = f"send_intro_{dt_of_log}.log"

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(levelname)s:%(message)s',
    filename=log_file_name,
    filemode='w', 
    encoding='utf-8', 
    level=logging.DEBUG
    )

#%%

@sleep_and_retry
@limits(calls=200, period=timedelta(seconds=60).total_seconds())
def send_intro_msg(content_sid: str, from_: str, date_contacted: str, to: str) -> Any: # TODO: how to properly annotate this?
    
    # Format phone number and format date that participant was recruited to the study
    number = 'whatsapp:+65' + to
    date_contacted_formatted = datetime.strptime(date_contacted, '%d%m%y').strftime("%d/%m/%Y")

    # Send the message
    message = client.messages.create(
        content_sid=content_sid, # HXXXXXXXXXXXXXXXXXXXXXXXXXX; WhatsApp content template ID
        from_= from_,            # MGXXXXXXXXXXXXXXXXXXXXXXXXXXX; messaging service ID
        content_variables=json.dumps({
            '1': date_contacted_formatted
        }),
        to=number
        )
    return message

#%%

parent_path = Path(__file__).parent
env_path = parent_path / ".env"
data_path = parent_path / "data" / "subjects.csv"

logger.info(f"Parent path: {parent_path}")
logger.info(f"Environment variables at {env_path}")

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

if account_sid and auth_token:
    logger.info(f"Twilio auth tokens successfully retrieved")
else:
    exit("twilio authentication tokens not loaded")

#%%

try:
    df_intro = pd.read_csv(data_path, dtype=str, na_values='NA')
    logger.info(f"Data of study subjects read in from {data_path}")
except FileNotFoundError:
    logger.exception("Data of study subjects not found")
    exit("FileNotFoundError for data of study subjects")
    

#%%

msg_id = list()
status = list()
error_code = list()
date_updated = list()

# Send introduction messages
for i in tqdm(range(len(df_intro))):
    contact_number, date_contacted = df_intro.loc[i, 'Mobile'], df_intro.loc[i, 'Date']
    msg = send_intro_msg(
        content_sid, messaging_service, date_contacted, contact_number
    )
    
    if msg.error_code:
        logger.info(f"Message {msg.sid} sent to {contact_number} with error code {msg.error_code}")
    else:
        logger.info(f"Message {msg.sid} sent to {contact_number}")

    msg_id.append(msg.sid)
    status.append(msg.status)
    error_code.append(msg.error_code)
    date_updated.append(
        msg.date_updated.strftime("%d/%m/%Y %H:%M:%S %Z")
    )

#%%

# Create output dataframe 
out = pd.DataFrame({
    'message_ID': msg_id,
    'status': status,
    'error': error_code,
    'date_updated': date_updated 
})

out_filename = "send_intro" + "_" + datetime.now().strftime("%d-%m-%Y %H:%M:%S")

out.to_csv(out_filename)

logging.shutdown()