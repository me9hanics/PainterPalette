import pandas as pd
import numpy as np #Can do an workaround to avoid this to save time
import sys
import re
import ast
import spacy
from collections import Counter

def create_painter_palette(wikiart_artists, art500k_artists, wikiart_art500k_mapping, art500k_further_selected_df):
    mapping_keys = list(wikiart_art500k_mapping.keys())
    #WikiArt + Art500k combination
    artists_c = create_painter_dataset_from_mapping(wikiart_art500k_mapping, wikiart_artists, art500k_artists)
    #Further WikiArt artists
    additional_artists_wikiart = wikiart_artists[~(wikiart_artists['artist'].isin(mapping_keys))].copy()
    additional_artists_wikiart.rename(columns={'pictures_count':'wikiart_pictures_count'}, inplace=True)
    artists = pd.concat([artists_c, additional_artists_wikiart], ignore_index=True)
    #Further Art500k artists
    additional_artists_art500k = (art500k_further_selected_df.copy()).rename(columns={'birth_date':'birth_year', 'death_date':'death_year'})
    artists = pd.concat([artists, additional_artists_art500k], ignore_index=True)
    return artists

############################# General functions #############################

def normalize_name(name):
    import unicodedata
    #Lowercase + replace non-ASCII characters
    name = name.lower()
    name = ''.join(c for c in unicodedata.normalize('NFKD', name) if c.isascii())
    return name

def row_contains_values_switch(row, columns, texts, exceptions=None, switch_function=None):
#The idea: if in certain columns (e.g. "Places", now "PaintingsExhibitedAt") there is a certain value contained (e.g. "Main") but not an exception (e.g. "Maine"), then a switch function is called
    if exceptions is None or not isinstance(exceptions, list): #To iterate over it
        exceptions = []
    
    value = row[columns[0]]
    if (type(value)==float) and (np.isnan(value)): #If it is NaN, then we don't want to do anything
        return row

    row2 = row.copy()
    for i in range(len(columns)):
        for exception in exceptions: #First, go through all exceptions
            if exception in value:
                break #Inner loop break, but it is "global" (also breaks the outer loop), see below
        else:#The else for the for loop: this is only ran, if the for loop was never broke. This includes if it is None
        #See here for explanation: 
        # https://stackoverflow.com/questions/189645/how-can-i-break-out-of-multiple-loops
            for text in texts:
                if text in value:
                    if switch_function is None:
                        print("Artist:", row['artist'], "Column:", columns[i], "contains text:", text) 
                    else:
                        if switch_function.__code__.co_argcount == 3: #Generated code
                            row2 = switch_function(row2, columns[i], text)
                        else:
                            row2 = switch_function(row2, columns[i])

            continue #Allows us to go to next column, withput breaking the outer loop
        #We would only get here if we already had a break (at the inner loop break)
        row2 = row #If the inner loop was broken, then the row is not changed
        break 
    return row2

def switch_function_exclude_word(row_as_series, column_name, excluded_word):
    row = row_as_series.copy()

    if column_name not in ["PaintingsExhibitedAt", "PaintingsExhibitedAtCount"]: #Used to be ["Places", "PlacesYears", "PlacesCount"]
        raise ValueError("Error: not yet implemented column")
    if not isinstance(row_as_series[column_name], str): #For example, if it is NaN (float)
        return row

    if column_name == "PaintingsExhibitedAt": 
        row[column_name] = row_as_series[column_name].replace(f", {excluded_word}", "").replace(f" {excluded_word},","")
        if row[column_name] == excluded_word:
            row[column_name] = ""
    #if column_name == "PlacesYears":
    #    expressions = re.findall(fr"{excluded_word}:\d+-\d+|$", row_as_series[column_name])
    #    expression = expressions[0] if expressions != [] else ""
    #    if expression != "":
    #        row[column_name] = row_as_series[column_name].replace(","+expression, "").replace(expression+",","")
    #        if row[column_name] == expression:
    #            row[column_name] = ""

    if column_name == "PaintingsExhibitedAtCount":
        expressions = re.findall(fr"\{{{excluded_word}:\d+\}}", row_as_series[column_name])
        expression = expressions[0] if expressions != [] else ""
        if expression != "":
            row[column_name] = row_as_series[column_name].replace(","+expression, "").replace(expression+",","")
            if row[column_name] == expression:
                row[column_name] = ""
    return row

def check_if_nan(entity):
    if type(entity) == float:
        if np.isnan(entity):
            return True
    return False

def combine_list_like_str_columns(df1, df2, columns, indices=[0,0]):
    for column in columns:
        column1_val = df1[column][indices[0]]
        column2_val = df2[column][indices[1]]
        
        if pd.isnull(df1[column][indices[0]]):
            df1.loc[indices[0], column] = column2_val
        elif not pd.isnull(df2[column][indices[1]]):
            values1 =  ast.literal_eval(column1_val) #A possibility to use re.findall(r"'(.*?)'", column1_val), however with inputs like 's-Hertogenbosch it'd fail
            values2 = ast.literal_eval(column2_val)
            values = list(set(values1 + values2))
            df1.loc[indices[0], column] = "["+",".join([f"'{x}'" for x in values])+"]"
    return df1

def combine_string_extend_columns(df1, df2, columns, indices=[0,0]):
    for column in columns:
        column1_val = df1[column][indices[0]]
        column2_val = df2[column][indices[1]]
        if pd.isnull(column1_val):
            df1.loc[indices[0], column] = column2_val
        elif not pd.isnull(column2_val):
            values1 = [x for x in column1_val.split(",") if x != ""]
            values2 = [x for x in column2_val.split(",") if x != ""]
            values = list(set(values1 + values2))
            df1.loc[indices[0], column] = ",".join(values)
    return df1

def combine_dict_like_columns(df1, df2, columns, indices=[0,0]):
    for column in columns:
        column1_val = df1[column][indices[0]]
        column2_val = df2[column][indices[1]]        
        if pd.isnull(df1[column][indices[0]]):
            df1.loc[indices[0], column] = column2_val
        elif not pd.isnull(df2[column][indices[1]]):
            values1 = re.findall(r"{(.*?)}", column1_val)
            values2 = re.findall(r"{(.*?)}", column2_val)
            tuples1 = [tuple(x.split(":")) for x in values1]
            tuples2 = [tuple(x.split(":")) for x in values2]
            for instance, count in tuples1:
                index1 = tuples1.index((instance, count))
                if instance in [x[0] for x in tuples2]:
                    index2 = [x[0] for x in tuples2].index(instance)
                    tuples1[index1] = (instance, int(count) + int(tuples2[index2][1]))
            for instance, count in tuples2:
                if instance not in [x[0] for x in tuples1]:
                    tuples1.append((instance, count))
            df1.loc[indices[0], column] = ",".join(["{" + ":".join(map(str, x)) + "}" for x in tuples1])
    return df1

def split_str_dict_keys_values(string_dict_list, year_vals = False):
    keys = [x.split(":")[0] for x in string_dict_list]
    values = [x.split(":")[1] for x in string_dict_list]
    if year_vals:
        firstyears = []
        lastyears = []
        firstyears_min =[]
        lastyears_max = []
        year_pairs = []
        for value in values:
            val_firstyears = [int(x.split("-")[0]) for x in value.split(",") if "-" in value]
            val_lastyears = [int(x.split("-")[1]) for x in value.split(",") if "-" in value]
            firstyears.append(val_firstyears)
            lastyears.append(val_lastyears)
            firstyears_min.append(min(val_firstyears))
            lastyears_max.append(max(val_lastyears))
        for i in range(len(firstyears)):
            year_pairs.append(list(zip(firstyears[i], lastyears[i])))
        return keys, values, firstyears, lastyears, firstyears_min, lastyears_max, year_pairs
    return keys, values

def combine_years_columns(df1, df2, columns, indices=[0,0], strdictlike=False, minmax=False):
    for column in columns:
        column1_val = df1[column][indices[0]]
        column2_val = df2[column][indices[1]]  
        if pd.isnull(df1[column][indices[0]]):
            df1.loc[indices[0], column] = column2_val
            continue
        elif not pd.isnull(df2[column][indices[1]]):
            if column == 'FirstYear':
                df1.loc[indices[0], column] = min(column1_val, column2_val)
                continue
            if column == 'LastYear':
                df1.loc[indices[0], column] = max(column1_val, column2_val)
                continue
            
            if not strdictlike: #locations_with_years
                #Assuming list inside the string (strlistlike)
                values1 = ast.literal_eval(column1_val)
                values2 = ast.literal_eval(column2_val)
            if strdictlike: #StylesYears
                values1 = [x for x in column1_val.split(",") if x != ""]
                values2 = [x for x in column2_val.split(",") if x != ""]

            keys1, _, _, _, minyears1, maxyears1, locations_yearpairs1 = split_str_dict_keys_values(values1, year_vals=True)
            keys2, _, _, _, minyears2, maxyears2, locations_yearpairs2 = split_str_dict_keys_values(values2, year_vals=True)

            if not minmax:
                tuples1 = list(zip(keys1, locations_yearpairs1))
                tuples2 = list(zip(keys2, locations_yearpairs2))
                for instance1, location_yearspair1 in tuples1:
                    index1 = tuples1.index((instance1, location_yearspair1))
                    if instance1 in [x[0] for x in tuples2]:
                        index2 = [x[0] for x in tuples2].index(instance1)
                        instance2, location_yearspair2 = tuples2[index2]
                        location_yearspairs = list(set(location_yearspair1 + location_yearspair2))
                        tuples1[index1] = (instance1, location_yearspairs)
                tuples1_copy = tuples1.copy()
                for instance2, location_yearspair2 in tuples2:
                    if instance2 not in [x[0] for x in tuples1_copy]:
                        tuples1.append((instance2, location_yearspair2))

                tuples = []
                for instance, location_yearspair in tuples1:
                    years_str = ",".join([str(location_yearspair[n][0]) + "-" + str(location_yearspair[n][0]) for n in range(len(location_yearspair))])
                    tuples.append((f"'{instance}'", years_str))
                df1.loc[indices[0], column] = "[" + ",".join([f"{x[0]}:{x[1]}" for x in tuples]) + "]"
                
            if minmax:
                tuples1 = list(zip(keys1, minyears1, maxyears1))
                tuples2 = list(zip(keys2, minyears2, maxyears2))
                for instance1, minyear1, maxyear1 in tuples1:
                    index1 = tuples1.index((instance1, minyear1, maxyear1))
                    if instance1 in [x[0] for x in tuples2]:
                        index2 = [x[0] for x in tuples2].index(instance1)
                        instance2, minyear2, maxyear2 = tuples2[index2]
                        minyear = min(minyear1, minyear2)
                        maxyear = max(maxyear1, maxyear2)
                        tuples1[index1] = (instance1, minyear, maxyear)
                tuples1_copy = tuples1.copy()
                for instance2, minyear2, maxyear2 in tuples2:
                    if instance2 not in [x[0] for x in tuples1_copy]:
                        tuples1.append((instance2, minyear2, maxyear2))    
                df1.loc[indices[0], column] = ",".join([f"{x[0]}:{x[1]}-{x[2]}" for x in tuples1])
    return df1

def combine_columns_first_value(df1, df2, columns, indices=[0,0]):
    for column in columns:
        if pd.isnull(df1[column][indices[0]]):
            df1.loc[indices[0], column] = df2[column][indices[1]]
    return df1
############################# PainterPalette manipulation functions #############################

def painter_palette_combine_instances_by_index(df, primary_artist_index, secondary_artist_index, return_index=False):
    df = df.copy()
    if primary_artist_index not in df.index or secondary_artist_index not in df.index:
        if primary_artist_index not in df.index:
            raise ValueError(f"Primary artist index {primary_artist_index} not found.")
        if secondary_artist_index not in df.index:
            raise ValueError(f"Secondary artist index {secondary_artist_index} not found.")
        return df
    df1 = df.loc[[primary_artist_index]].reset_index(drop=True) #Should be only one row
    df2 = df.loc[[secondary_artist_index]].reset_index(drop=True)
    string_extend_columns = ['styles', 'occupations', 'PaintingsExhibitedAt', 'PaintingSchool','Influencedby','Influencedon','Pupils', 'Teachers','FriendsandCoworkers',]
    dict_like_columns = ['Art500k_Movements', 'styles_extended', 'StylesCount','PaintingsExhibitedAtCount', 'ArtMovement']
    list_like_columns = ['locations'] 
    years_columns = ['FirstYear','LastYear', 'locations_with_years'] #StylesYears is added separately
    first_value_columns = ['Nationality', 'citizenship', 'gender', 'movement', 'birth_place', 'death_place', 'birth_year', 'death_year', 'Contemporary', 'Type']
    #wikiart_pictures_count is handled separately

    #Columns where first value is chosen if it is not NaN
    if pd.isnull(df1['wikiart_pictures_count'][0]):
        df1.loc[0,'wikiart_pictures_count'] = df2['wikiart_pictures_count'][0]
    else:
        df1.loc[0,'wikiart_pictures_count'] = max(df1['wikiart_pictures_count'][0], df2['wikiart_pictures_count'][0]) #Could consider to add them
    df1 = combine_columns_first_value(df1, df2, first_value_columns)
    df1 = combine_string_extend_columns(df1, df2, string_extend_columns)
    df1 = combine_dict_like_columns(df1, df2, dict_like_columns)
    df1 = combine_list_like_str_columns(df1, df2, list_like_columns)
    df1 = combine_years_columns(df1, df2, years_columns)
    df1 = combine_years_columns(df1, df2, ['StylesYears'], strdictlike=True)

    df = df.drop([secondary_artist_index, primary_artist_index])

    max_index = max(df.index)
    df1.index = [max_index+1] #To avoid index conflicts
    df = pd.concat([df, df1], ignore_index=False) #This is important for cases when we don't want to reset the index of other rows 
    if return_index:
        return df, df[-1:].index[0]
    return df

def create_painter_dataset_from_mapping(mapping, wikiart_df = None, art500k_df = None):
    if wikiart_df is None:
        wikiart_df = pd.read_csv('https://raw.githubusercontent.com/me9hanics/PainterPalette/main/datasets/wikiart_artists.csv') 
    if art500k_df is None:
        art500k_df = pd.read_csv('https://raw.githubusercontent.com/me9hanics/PainterPalette/main/datasets/art500k_artists.csv')
    artists_c = pd.DataFrame()
    for key, value in mapping.items():
        wikiart_artist_df = wikiart_df[wikiart_df['artist'] == key]; art500k_artist_df = art500k_df[art500k_df['artist'] == value]
        columns_list_Wiki = wikiart_df.columns.tolist(); columns_list_Art500k = art500k_df.columns.tolist()[1:]
        combined_df = pd.concat([wikiart_artist_df[columns_list_Wiki].reset_index(), art500k_artist_df[columns_list_Art500k].reset_index()],  axis=1).drop(columns=['index'])
        artists_c = pd.concat([artists_c, combined_df], axis=0).reset_index(drop=True)
    #cols = artists_c.columns.tolist();
    #cols = cols[0:1]+cols[7:8]+cols[5:7]+cols[1:2]+cols[3:4]+cols[19:]+cols[2:3]+cols[9:10]+cols[4:5]+cols[15:19]+cols[8:9]+cols[10:15]
    cols = ["artist", "Nationality", "citizenship", 'gender', 'styles', 'movement', 'ArtMovement', 'birth_place','death_place',
            'birth_year', 'death_year', 'FirstYear', 'LastYear', 'pictures_count', 'locations','locations_with_years',
            'styles_extended', 'StylesCount', 'StylesYears', 'occupations',  'PaintingsExhibitedAt', 'PaintingsExhibitedAtCount',
             'PaintingSchool', 'Influencedby', 'Influencedon', 'Pupils', 'Teachers','FriendsandCoworkers','Contemporary'
            ] #Skipped:  'Type',
    artists_c = artists_c[cols]
    artists_c = artists_c.rename(columns={"pictures_count": "wikiart_pictures_count", 'ArtMovement': "Art500k_Movements"})
    return artists_c

############################# Art500k/WikiArt functions #############################

def wikiart_combine_instances(df, primary_artist_name, secondary_artist_name):
    df = df.copy()
    if primary_artist_name not in df['artist'].values or secondary_artist_name not in df['artist'].values:
        if primary_artist_name not in df['artist'].values:
            raise ValueError(f"Primary artist {primary_artist_name} not found.")
        if secondary_artist_name not in df['artist'].values:
            raise ValueError(f"Secondary artist {secondary_artist_name} not found.")
        return df
    df1 = df[df['artist'] == primary_artist_name].reset_index(drop=True) #Set to 0 (might be changed)
    df2 = df[df['artist'] == secondary_artist_name].reset_index(drop=True)
    string_extend_columns = ['styles', 'occupations',]
    dict_like_columns = ['styles_extended', ]
    list_like_columns = ['locations']
    years_columns = ['locations_with_years'] #StylesYears is added separately
    first_value_columns = ['movement', 'birth_place', 'death_place', 'birth_year', 'death_year', 'gender', 'citizenship']

    #sum_like_column columns: pictures_count (might have np.nan values)
    df1.loc[0,'pictures_count'] = np.nansum([df1['pictures_count'][0], df2['pictures_count'][0]])

    df1 = combine_columns_first_value(df1, df2, first_value_columns)
    df1 = combine_string_extend_columns(df1, df2, string_extend_columns)
    df1 = combine_dict_like_columns(df1, df2, dict_like_columns)
    df1 = combine_list_like_str_columns(df1, df2, list_like_columns)
    df1 = combine_years_columns(df1, df2, years_columns)

    df = df[(df['artist'] != secondary_artist_name) & (df['artist'] != primary_artist_name)]
    df = pd.concat([df, df1], ignore_index=True)
    return df

def art500k_combine_instances(df, primary_artist_name, secondary_artist_name):
    df = df.copy()
    if primary_artist_name not in df['artist'].values or secondary_artist_name not in df['artist'].values:
        if primary_artist_name not in df['artist'].values:
            raise ValueError(f"Primary artist {primary_artist_name} not found.")
        if secondary_artist_name not in df['artist'].values:
            raise ValueError(f"Secondary artist {secondary_artist_name} not found.")
        return df
    df1 = df[df['artist'] == primary_artist_name].reset_index(drop=True) #Set to 0 (might be changed)
    df2 = df[df['artist'] == secondary_artist_name].reset_index(drop=True)
    string_extend_columns = ['PaintingSchool','Influencedby','Influencedon','Pupils', 'Teachers','FriendsandCoworkers','PaintingsExhibitedAt']
    dict_like_columns = ['ArtMovement', 'StylesCount','PaintingsExhibitedAtCount']
    years_columns = ['FirstYear','LastYear'] #StylesYears is added separately
    first_value_columns = ['Nationality', 'Contemporary', 'Type']

    df1 = combine_columns_first_value(df1, df2, first_value_columns)
    df1 = combine_string_extend_columns(df1, df2, string_extend_columns)
    df1 = combine_dict_like_columns(df1, df2, dict_like_columns)
    df1 = combine_years_columns(df1, df2, years_columns)
    df1 = combine_years_columns(df1, df2, ['StylesYears'], strdictlike=True, minmax=True)

    df = df[(df['artist'] != secondary_artist_name) & (df['artist'] != primary_artist_name)]
    df = pd.concat([df, df1], ignore_index=True)
    return df

def art500k_combine_instances_by_index(df, primary_artist_index, secondary_artist_index):
    df = df.copy()
    df1 = df.loc[[primary_artist_index]].reset_index(drop=True)
    df2 = df.loc[[secondary_artist_index]].reset_index(drop=True)
    string_extend_columns = ['PaintingSchool','Influencedby','Influencedon','Pupils', 'Teachers','FriendsandCoworkers','PaintingsExhibitedAt']
    dict_like_columns = ['ArtMovement', 'StylesCount','PaintingsExhibitedAtCount']
    years_columns = ['FirstYear','LastYear'] #StylesYears is added separately

    if pd.isnull(df1['Nationality'][0]):
        df1.loc[0,'Nationality'] = df2['Nationality'][0]
    if pd.isnull(df1['Contemporary'][0]):
        df1.loc[0,'Contemporary'] = df2['Contemporary'][0]
    if pd.isnull(df1['Type'][0]):
        df1.loc[0,'Type'] = df2['Type'][0]

    df1 = combine_string_extend_columns(df1, df2, string_extend_columns)
    df1 = combine_dict_like_columns(df1, df2, dict_like_columns)
    df1 = combine_years_columns(df1, df2, years_columns)
    df1 = combine_years_columns(df1, df2, ['StylesYears'], strdictlike=True)

    df = df.drop([secondary_artist_index, primary_artist_index])
    df = pd.concat([df, df1], ignore_index=True)
    return df

def art500k_combine_duplicate_name(df, name):
    df2 = df.copy()
    duplicates = df[df.duplicated(['artist'], keep=False)]
    duplicates.sort_values(by=['artist'])
    duplicates = duplicates[duplicates['artist'].str.contains(name)]
    if len(duplicates) == 2:
        primary_artist_index = duplicates.index[0]
        secondary_artist_index = duplicates.index[1]
        df2 = art500k_combine_instances_by_index(df2, primary_artist_index, secondary_artist_index)
        df2 = df2.reset_index(drop=True)
    if(len(duplicates) > 2):
        print("More than 2 duplicates found, not implemented yet.")

    return df2


def art500k_combine_duplicates(df):
    df2 = df.copy()
    duplicated_names = df2[df2.duplicated(['artist'], keep=False)]['artist'].unique()
    for name in duplicated_names:
        df2 = art500k_combine_duplicate_name(df2, name)
    return df2

############################# Initial functions #############################

#Extract years from strings containing dates with RegEx
def initial_art500k_years_extract(date_string):
    years = re.findall(r'\b\d{4}\b', str(date_string))  #finds 4-digit numbers
    years_list = list(map(int, years))  #List of years, as ints
    return years_list

#Get the earliest and latest year for each artist (thus the interval)
def initial_art500k_get_years_interval(years_list):
    if len(years_list)>0:
        return min(years_list), max(years_list)
    return None, None #Just if the list is empty

def initial_art500k_get_artist_geolocations(artist_rows):
    nlp = spacy.load("en_core_web_sm") #Just English model. This may be a mistake, some locations may be from different languages
    
    geolocations = []
    for location_string in artist_rows['Location']:
        if location_string is np.nan:
            continue
        doc = nlp(location_string)
        for ent in doc.ents:
            if ent.label_ == 'GPE': #Geopolitical entity (locations)
                geolocations.append(ent.text)
    if geolocations == []:
        return None

    geolocations = list(set(geolocations)) #Duplicates are excluded with set()
    return initial_art500k_get_geolocations_string(geolocations) #Could switch to dictstring version

def initial_art500k_get_multiple_artists_geolocations(artist_rows):
    nlp = spacy.load("en_core_web_sm")  # ust English. May be a mistake, some locations could be from different languages

    geolocations = []
    for location_string in artist_rows['Location']:
        if location_string is np.nan:
            continue
        doc = nlp(location_string)
        for ent in doc.ents:
            if ent.label_ == 'GPE':  #Geopolitical entity (locations)
                geolocations.append(ent.text)
    if geolocations == []:
        return None
    location_counter = Counter(geolocations)
    result_string = ",".join([f"{{{location}:{count}}}" for location, count in location_counter.items()])
    return result_string

def initial_art500k_get_geolocations_string(location_list): # Version A
    return ', '.join(location_list)

def initial_art500k_get_geolocations_dictstring(location_list):
    location_counter = Counter(location_list)
    return ', '.join([f'{{{key}:{value}}}' for key, value in location_counter.items()])

############################# Similarity functions #############################

def similarity(s1, s2):
    import difflib #Import here, because it is only used here
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def similarity_difference(s1, s2):
    return (1 - similarity(s1, s2))*len(s1)

def character_difference_naive(a, b, similarity_score):
    #Usually, similarity_score comes from similarity
    return similarity_score*len(a)

def similarity_character_difference_operations(s1,s2):
    import difflib #Import here, because it is only used here
    sequence_match = difflib.SequenceMatcher(None, s1, s2)
    similarity = sequence_match.ratio()
    character_difference = 0
    steps = 0
    for opcode in sequence_match.get_opcodes():
        if opcode[0] in ['replace', 'delete']:
            character_difference += opcode[2] - opcode[1]
            steps += 1
        if opcode[0]=='insert':
            character_difference += opcode[4] - opcode[3]
            steps += 1

    return similarity, character_difference, steps

def sort_artists_by_similarity(df, original_string, similarity_func=similarity):
    """
    Sorts DataFrame 'artist' column similarity, based on the given similarity function.

    Parameters:
    df (pd.DataFrame): DataFrame containing the artist names.
    original_string (str): String to compare to
    similarity_func (function): The similarity function to use.

    Returns:
    pd.DataFrame: The original DataFrame sorted.
    """

    df['similarity'] = df['artist'].apply(lambda x: similarity_func(original_string, x))
    sorted_df = df.sort_values(by='similarity', ascending=False)
    return sorted_df

def calculate_similarities_df(artists_X, artists_Y):
    sims_df = pd.DataFrame(columns=['artist (original)','"Best" pair','Similarity', 'Character difference', 'Operations to transform'])
    artists_X_copy = artists_X.copy()
    artists_Y_copy = artists_Y.copy()
    if type(artists_X) == pd.core.frame.DataFrame:
        artists_X_copy = artists_X_copy['artist']
    if type(artists_Y) == pd.core.frame.DataFrame:
            artists_Y_copy = artists_Y_copy['artist']

    for painter in artists_X:
        all_sims = []
        max_sim = 0
        for comparison_artist in artists_Y:
            (similarity_score,char_diff, operation_count) = similarity_character_difference_operations(painter, comparison_artist)
            if similarity_score >= max_sim: #Runtime reasons
                max_sim = similarity_score
                all_sims.append((similarity_score,char_diff, operation_count ,comparison_artist))
        final_maximum = max(sims[0] for sims in all_sims) 
        for sims in all_sims:
            if sims[0] == final_maximum: #Just take the highest ones
                sims_df = pd.concat([sims_df, pd.DataFrame([[painter, sims[3], sims[0], sims[1], sims[2]]], columns=['artist (original)','"Best" pair','Similarity', 'Character difference', 'Operations to transform'])])

    sims_df = (sims_df.sort_values(by=['Similarity'], ascending=False)).reset_index(drop=True)
    return sims_df

############################# Year checking functions #############################

def years_completer(yearslist): #Birth, first active year, last active year, death
    """
    Expecting 4 values, in this order: birthyear, first active year, last active year, death year.
    
    Returns either a nan (if it is insufficient data), or a filled list of years.
    This is not used for the dataset creation typically, but for analysis (fill blanks).
    """
    if np.isnan(yearslist[0]) and np.isnan(yearslist[1]):
        return np.nan
    if np.isnan(yearslist[2]) and np.isnan(yearslist[3]):
        return np.nan
    
    if np.isnan(yearslist[0]):
        yearslist[0] = yearslist[1]
    if np.isnan(yearslist[1]):
        yearslist[1] = yearslist[0]
    if np.isnan(yearslist[2]):
        yearslist[2] = yearslist[3]
    if np.isnan(yearslist[3]):
        yearslist[3] = yearslist[2]

    #return sorted(yearslist) #Sort just in case
    return yearslist

def order_check(years_ordered, years_original_order):
    if years_ordered != years_original_order:
        return True
    return False

def difference_check(yearslist):
    if min(yearslist) +110 < max(yearslist):
        return True
    return False

def artist_years_order_check(artist_years):
    """Expecting 4 years, in this order: birthyear, first active year, last active year, death year."""
    artist_years_modified = years_completer(artist_years)
    if type(artist_years_modified)==float: #np.nan
        return False
    artist_years_ordered = sorted(artist_years_modified)
    if order_check(artist_years_ordered, artist_years_modified):
        return True
    return False

def suspicious_artist_years_check(artist_years):
    #Birthyear, first year of activity, last year of activity, death year
    artist_years_modified = years_completer(artist_years)
    if type(artist_years_modified)==float: #np.nan
        return False
    artist_years_ordered = sorted(artist_years_modified)
    if order_check(artist_years_ordered, artist_years_modified) or difference_check(artist_years_modified):
        return True
    return False

def first_year_setting(birth_year, difference=20):
    return birth_year, birth_year+difference #

def last_year_setting(death_year, difference=0):
    return death_year-difference, death_year

def years_setting(df, fix_first_year_artists, fix_last_year_artists, first_year_difference=20, last_year_difference=0):
    for artist in fix_first_year_artists:
        index = df[df['artist']==artist].index[0]
        df.at[index, 'FirstYear'] = first_year_setting(df.at[index, 'birth_date'], first_year_difference)[0]
    for artist in fix_last_year_artists:
        index = df[df['artist']==artist].index[0]
        df.at[index, 'LastYear'] = last_year_setting(df.at[index, 'death_date'], last_year_difference)[1]
    return df