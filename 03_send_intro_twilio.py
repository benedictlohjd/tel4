
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

flow_sid = 'FWcfb4c89a60dba069e779ea82584e4f5f'
messaging_service = 'MG83cd4bb8925889ff75ad342587513137'

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
logger.info("Starting program to send intro messages")
logger.info(f"Using Flow SID: {flow_sid}")
logger.info(f"Using messaging service: {flow_sid}")
#%%


@sleep_and_retry
@limits(calls=200, period=timedelta(seconds=60).total_seconds())
def send_intro_msg(
    flow_sid: str,
    msg_service_sid: str, 
    date_contacted: str, 
    to: str) -> Any: # TODO: how to properly annotate this?
    
    # Format phone number and format date that participant was recruited to the study
    number = 'whatsapp:+65' + to
    date_contacted_formatted = datetime.strptime(date_contacted, '%d%m%y').strftime("%d/%m/%Y")

    # Trigger the flow
    execution = client.studio.v2.flows(flow_sid).executions.create(
        parameters={
            '1': date_contacted_formatted
            }, 
        to=number, 
        from_=msg_service_sid
        )
    logger.info(f"Triggered flow execution {execution.sid} for mobile number {to}")

    return execution

#%%

parent_path = Path(__file__).parent.parent
env_path = parent_path / "telproject" / ".env"
data_path = parent_path / "telproject" / "data" / "subjects_test.csv"

logger.info(f"Parent path: {parent_path}")
logger.info(f"Environment variables at {env_path}")

#%%
# Load twilio tokens


load_dotenv(env_path)

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

if account_sid and auth_token:
    logger.info(f"Twilio auth tokens successfully retrieved")
else:
    logging.shutdown()
    exit("twilio authentication tokens not loaded")

#%%

try:
    df_intro = pd.read_csv(data_path, dtype=str, na_values='NA')
    logger.info(f"Data of study subjects read in from {data_path}")
except FileNotFoundError:
    logger.exception("Data of study subjects not found")
    logging.shutdown()
    exit("FileNotFoundError for data of study subjects")
    
df_intro.fillna('', inplace=True)

#%%

execution_id = list()
status = list()
date_updated = list()
mobile = list()

# Send introduction messages
for i in tqdm(range(len(df_intro))):
    contact_number, date_contacted = df_intro.loc[i, 'Mobile'], df_intro.loc[i, 'Date']
    if contact_number and date_contacted:
        execution = send_intro_msg(
            flow_sid, messaging_service, date_contacted, contact_number
        )

        execution_id.append(execution.sid)
        status.append(execution.status)
        date_updated.append(
            execution.date_updated.strftime("%d/%m/%Y %H:%M:%S %Z")
        )
        mobile.append(contact_number)
    else:
        subject_name = df_intro.loc[i, 'Name']
        logger.info(f"Missing mobile number or date contacted for subject {subject_name}")

#%%

# Create output dataframe 
out = pd.DataFrame({
    'message_ID': execution_id,
    'mobile': mobile,
    'status': status,
    'date_updated': date_updated 
})

out_filename = "send_intro" + "_" + str(datetime.now().strftime("%d-%m-%Y_%H%M%S")) + '.csv'

out.to_csv(out_filename, sep=",", index=False)

logger.info("Finished program to send intro messages")

logging.shutdown()
# %%
