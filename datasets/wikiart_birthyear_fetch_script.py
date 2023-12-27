import pandas as pd
import requests
import time

# Function to get the birth year of the artist from Wikidata
def get_birth_year(artist_name, artist_birth_years, endpoint_url="https://query.wikidata.org/sparql", retries=3, delay=1):
    # Check if we already have the birth year
    if artist_name in artist_birth_years:
        return artist_birth_years[artist_name]

    # SPARQL query to fetch the birth year
    query = '''
    SELECT ?artist ?artistLabel ?dateOfBirth WHERE {
      ?artist ?label "%s"@en.
      ?artist wdt:P569 ?dateOfBirth.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 1
    ''' % artist_name.replace('"', '\"')

    # Attempt the request up to 'retries' times
    for attempt in range(retries):
        response = requests.get(endpoint_url, params={'query': query, 'format': 'json'})
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {}).get('bindings', [])
            if results:
                date_of_birth = results[0].get('dateOfBirth', {}).get('value', None)
                artist_birth_years[artist_name] = date_of_birth  # Store the birth year
                return date_of_birth
            break  # Break out of the loop if successful
        else:
            print(f"Error fetching data for {artist_name}, status code: {response.status_code}. Attempt {attempt + 1} of {retries}.")
            if response.status_code in [429, 500, 502, 503, 504]:
                time.sleep(delay * (attempt + 1))  # Exponential back-off
            else:
                break  # Break on non-retryable error

    # Store None if we failed to get the birth year
    artist_birth_years[artist_name] = None
    return None