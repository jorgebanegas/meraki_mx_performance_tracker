"""
Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import schedule
import time
import meraki 
import pandas as pd
import json
import config
from datetime import datetime
import csv
import os.path 
from schedule import every, repeat, run_pending

def append_column(csv_file):
    # initialize meraki SDK object
    dashboard = meraki.DashboardAPI(api_key=config.meraki_api_key, print_console=False,output_log=False)

    # Read the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)  # Convert the reader object to a list of rows

    # Append the new column header to the first row
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    rows[0].append(dt_string)


    # Append the new data to each row
    for row in rows[1:]:
        perf_score = dashboard.appliance.getDeviceAppliancePerformance(serial=row[1])
        row.append(perf_score['perfScore'])

    # Write the updated data back to the CSV file
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def your_function():
    file_exists = os.path.exists('report.csv')
    # Your code here
    print("This function is running.")
    appliance_list = []
    # initialize meraki SDK object
    dashboard = meraki.DashboardAPI(api_key=config.meraki_api_key, print_console=False,output_log=False)

    # query top 10 appliances by most utilization within 30 days
    top_ten = dashboard.organizations.getOrganizationSummaryTopAppliancesByUtilization(organizationId=config.org_id,timespan=2.628e+6)

    if file_exists == False:
        with open('top_ten.txt', 'w') as fout:
            json.dump(top_ten, fout, indent=4)

        print(top_ten)

        for mx in top_ten:
            # datetime object containing current date and time
            now = datetime.now()
            # dd/mm/YY H:M
            dt_string = now.strftime("%d/%m/%Y %H:%M")
            perf_score = dashboard.appliance.getDeviceAppliancePerformance(serial=mx['serial'])

            temp={}
            temp['model'] = mx['model']
            temp['serial'] = mx['serial']
            temp['network'] = mx['network']['name']
            temp[dt_string] = perf_score['perfScore']

            appliance_list.append(temp)

        keys = appliance_list[0].keys()

        with open('report.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(appliance_list)
    else:
            append_column('report.csv')
            print('Column appended successfully!')

your_function()
schedule.every(config.time_interval).minutes.do(your_function)
while True:
    schedule.run_pending()
    time.sleep(1)
 