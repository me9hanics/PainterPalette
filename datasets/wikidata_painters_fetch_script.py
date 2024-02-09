from urllib.parse import urlparse
import pandas as pd
import requests
import time

def sparql_query(query, offset, retries=5, backoff_factor=0.1, timeout=60): #A similar function is in the SparQL Wikidata data collection submodule. https://github.com/me9hanics/sparql-wikidata-data-collection
    url = 'https://query.wikidata.org/sparql'
    headers = {"Accept": "application/sparql-results+json"}
    response = None
    for i in range(retries):
        try:
            full_query = query.format(offset=offset)
            response = requests.get(url, headers=headers, params={'query': full_query}, timeout=timeout)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            data = response.json()
            for result in data['results']['bindings']:
                painter_uri = result['painter']['value']
                if not bool(urlparse(painter_uri).netloc):
                    raise ValueError(f"Invalid URI: {painter_uri}")
            return data
        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
            if i < retries - 1:  # No delay on the last attempt
                sleep_time = backoff_factor * (2 ** i)  # Exponential back-off
                time.sleep(sleep_time)
            else:
                print("Failed to parse JSON. Response text:")
                if response is not None:
                    print(response.text)
                print(f"Error: {e}")
                return None

def get_painters_list():
    #First, the query, which gets the painters (instance of human + occupation painter)
    query = '''
    SELECT ?painter ?painterLabel WHERE {{
      ?painter wdt:P31 wd:Q5;
              wdt:P106 wd:Q1028181.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 15000
    OFFSET {offset}
    '''
    #There are around 200k painters in the Wikidata database, 200086 at the time of writing, can't get all of them at one go, so we need to fetch them in chunks.
    offset = 0
    total_runs = 0
    data = {} #We use a dictionary, so "not data" doesn't break the loop in the case of an error

    while total_runs <= 20: #we should get all painters in 14 runs, but we'll do 20 just to be safe
        try:
            data = sparql_query(query, offset)
        except:
            time.sleep(180)
            total_runs += 1
            continue #Basically, we try again after 3 minutes
        if not data:
            break
        names.extend([item['painterLabel']['value'] for item in data['results']['bindings']])
        offset += 15000
        time.sleep(30)
        total_runs += 1
    return names

names = get_painters_list() #Important to say, that this wasn't the final result, some results were "Q1......" type results 
    #even for labels, these were dropped, and some new names were added, but this was the main part of the data collection.

with open('PainterPalette/painter_names_200k.txt', 'w', encoding="utf-8") as f:
    for name in names:
        f.write(name + '\n')