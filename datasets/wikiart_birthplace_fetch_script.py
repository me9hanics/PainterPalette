import pandas as pd
import requests
import time


def get_birthplace(artist_name, artist_birthplaces, endpoint_url="https://query.wikidata.org/sparql", retries=3, delay=1,):
    # Check if we already have the birth place
    if artist_name in artist_birthplaces:
        return artist_birthplaces[artist_name]
    
    # SPARQL query to fetch the birth place. See: https://www.mediawiki.org/wiki/API:Main_page#Endpoint
    query = '''
    SELECT ?artist ?artistLabel ?placeOfBirthLabel WHERE {
      ?artist ?label "%s"@en.
      ?artist wdt:P19 ?placeOfBirth.
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
                birth_place = results[0].get('placeOfBirthLabel', {}).get('value', None)
                artist_birthplaces[artist_name] = birth_place  # Store the birth place
                return birth_place
            break  # Break out of the loop if successful
        else:
            print(f"Error fetching data for {artist_name}, status code: {response.status_code}. Attempt {attempt + 1} of {retries}.")
            if response.status_code in [429, 500, 502, 503, 504]:
                time.sleep(delay * (attempt + 1))  # Exponential back-off
            else:
                break  # Break on non-retryable error

    # Store None if we failed to get the birth place
    artist_birthplaces[artist_name] = None
    return None

if __name__ == '__main__':
    art_data = pd.read_csv("originals/wikiart_art_pieces.csv")
    non_artists = ['Byzantine Mosaics', 'Orthodox Icons', 'Romanesque Architecture']
    art_data = art_data[~art_data['artist'].isin(non_artists)]
    
    # Add a new column for birthplaces
    art_data['birth_place'] = None
    
    #Dictionary to storing birthplaces (no repeated API calls this way)
    artist_birthplaces = {}
    
    # Iterate over the artists in the dataframe
    for index, row in art_data.iterrows():
        artist_name = row['artist']
        birth_place = get_birthplace(artist_name, artist_birthplaces)
        
        # Update the birth_place in the dataframe
        art_data.at[index, 'birth_place'] = birth_place
    
        # Print progress
        print(f"Fetched birthplace for {artist_name}: {birth_place}")
    
    #Save the updated df to csv
    art_data.to_csv("wikiart_paintings_with_artist_birthplaces.csv", index=False)
    
    #Reload the data for safe keeping
    art_data_with_birth_places = pd.read_csv("wikiart_paintings_with_artist_birthplaces.csv")
    #Manually add some missing birthplaces
    manual = pd.read_csv('artist_birth_work_places_manually_created.csv')
    for i, row in art_data_with_birth_places.iterrows():
        for j, row2 in manual.iterrows():
            if row['artist'] == row2['artist']:
                row['birth_place'] = row2['birth_place']
    #Clean
    art_data_cleaned = art_data_with_birth_places[(art_data_with_birth_places['birth_place'].notna())]
    art_data_cleaned.to_csv("wikiart_paintings_with_artist_birthplaces_cleaned.csv", index=False)