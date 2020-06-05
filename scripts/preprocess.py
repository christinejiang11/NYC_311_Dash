import pandas as pd
import json
from Socrata import sodapy

def get_data(chunk_size=100000, total_rows=int(total_count)):
    #define parameters for endpoint, dataset, and app token
    path ='../../data/'

    data_url = 'data.cityofnewyork.us'
    dataset = 'erm2-nwe9'
    with open(path+'client_secret.json') as f:
        credentials = json.load(f)
    app_token = credentials['app_token']

    #sets up the connection, need application token to override throttling limits
    #username and password only required for creating or modifying data
    client = Socrata(data_url, app_token)
    client.timeout = 6000

    #count number of records in desired dataset
    record_count = client.get(dataset, select='count(*)', where="created_date >='2020-01-01'")
    total_count = record_count[0]['count']
    print(total_count)

    start = 0
    results=[]
    #paginate through dataset in sets of 10000 to get all records since start of 2020
    while True:
        print(f'{start} rows retrieved')
        results.extend(client.get(dataset,select="unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, location_type, incident_zip, borough, address_type, city, status, latitude, longitude, location",
                                  where="created_date >= '2020-02-01'",
                                  limit=chunk_size, offset=start))
        start += chunk_size
        if start > total_rows:
            break
    return results

orig_results = get_data()
orig_df = pd.DataFrame(orig_results)
orig_df.to_csv(path+'311_data.csv', index=False)
