############################################################################################################################
# Title: Rule Check
# Date:  2020-05-18
# Author:  Ethan Mooney
# Description:  This is a simple function that sends an email with attachment containing a timestamp.  An outlook rule 
# called "Rule Check" saves the attachment to a specified file.  The file is then read by this function to verify the rule 
# is running.  If execution of the rule takes greater than N seconds, an email alert is sent.  This process is repeated
#  every N minutes.   
############################################################################################################################

import pandas as pd
import os
from functools import reduce
import string
import numpy as np
import collections
import re
from datetime import datetime
from pathlib import Path
from my_functions import max_pd_display, check_answer, make_string_cost_center, add_columns_for_reporting, double_check
from my_classes import FileDateVars
from my_variables import master_alias, mmm_dict
import win32com.client
import time 

max_pd_display()

#define the file paths and file names
rule_check_path = Path('//uh-nas/Groupshare3/ClinicalAdvisoryTeam/data_folders/rule_check_folder')
rule_ck_out_file_name = 'rule_check_timestamp.csv'
rule_ck_in_file_name = 'timestamp_from_message.csv'

while True:
    try:
        #generate a timestamp string
        timestr = time.strftime("%Y%m%d-%H%M")
        #open the file to write the timestamp to
        timestamp = open(rule_check_path / rule_ck_out_file_name, 'r+')
        #write the timestamp
        timestamp.write(timestr)
        #close the timestamp file
        timestamp.close()
        #initialize the outlook mail item using the local account
        olMailItem = 0x0
        #create an object to interface with Outlook
        obj = win32com.client.Dispatch("Outlook.Application")
        #create the new mail object
        newMail = obj.CreateItem(olMailItem)
        #generate the components
        newMail.Subject = '#rule_check_message'
        newMail.To = 'ejmooney@salud.unm.edu'
        newMail.body = '''This is your automated rule-checking message.  This message is only intended to ensure Outlook is running and rule-checking is operational in general.  The 
successful completion of this rule_check does not necessarily mean that ALL rules are operational. '''
        #add the attachment to the message
        newMail.Attachments.Add('//uh-nas/Groupshare3/ClinicalAdvisoryTeam/data_folders/rule_check_folder/rule_check_timestamp.csv')
        #send the message
        newMail.Send()
        #sleep for 5 minutes to allow the message to be received and the rule to excecute (delay of up to one minute has been observed)
        time.sleep(300)
        #read the file that has been saved by outlook rule "Rule Check"
        from_msg = pd.read_csv(rule_check_path / rule_ck_in_file_name )
        #recover the timestamp from the file saved by the rule
        timestamp = from_msg.columns.values[0]
        #convert the string timestamp to a datetime value
        timestamp = datetime.strptime(timestamp, '%Y%m%d-%H%M')
        #generate a timestamp for now
        nowstamp = time.strftime('%Y%m%d-%H%M')
        #convert the now timestamp to a datatime value
        nowstamp = datetime.strptime(nowstamp, '%Y%m%d-%H%M')
        #calculate the difference in the timestamp sent through the rule process and the now timestamp
        diff = ((nowstamp - timestamp).total_seconds())
        # if the difference between the timestamps is greater than 900 seconds 15 min, there is likely a problem with the rules; so send an email
        if diff > 1200:
            alertMail = obj.CreateItem(olMailItem)
            alertMail.Subject = 'Problem with Outlook Rules'
            alertMail.To = 'ejmooney@salud.unm.edu'
            alertMail.body = '''Your rule check process has detected a problem with an outlook rule.  Please check your "server machine" to ensure Outlook is running correctly.'''
            alertMail.Send()
            print(str(nowstamp) + ' try statment executed and detected a problem; message sent and sleeping for 1 hour')
            time.sleep(3600)
        else:
            #if the difference between the timestamps is < 120 seconds, the rule appears to be in place so no action/alert needs to be made
            print(str(nowstamp) + ' try statement executed without any issue, sleeping for 1 hour')
            time.sleep(3600)
    except:
        #if for some reason an exception is encountered, handle it with an email alert and retry the process in an hour
        alertMail2 = obj.CreateItem(olMailItem)
        alertMail2.Subject = 'Problem with Outlook Rules'
        alertMail2.To = 'ejmooney@salud.unm.edu'
        alertMail2.body = '''Your rule check process has triggered an except statement.  Please check your "server machine" to ensure your mail_rules are working correctly.'''
        alertMail2.Send()
        print(str(nowstamp) + ' exception triggered; sleeping for 1 hour')
        time.sleep(3600)
