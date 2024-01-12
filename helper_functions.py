def combine_instances(df, primary_artist_name, secondary_artist_name):
    import sys
    import pandas as pd
    import re

    df = df.copy()
    df1 = df[df['artist'] == primary_artist_name].reset_index(drop=True)
    df2 = df[df['artist'] == secondary_artist_name].reset_index(drop=True)
    string_extend_columns = ['PaintingSchool','Influencedby','Influencedon','Pupils', 'Teachers','FriendsandCoworkers','Places']
    dict_like_columns = ['ArtMovement', 'StylesCount','PlacesCount']
    years_columns = ['FirstYear','LastYear','PlacesYears','StylesYears']

    if pd.isnull(df1['Nationality'][0]):
        df1['Nationality'][0] = df2['Nationality'][0]

    for column in string_extend_columns:
        column1_val = df1[column][0]
        column2_val = df2[column][0]
        if pd.isnull(column1_val):
            df1[column][0] = column2_val
        else:
            values1 = [x for x in column1_val.split(",") if x != ""]
            values2 = [x for x in column2_val.split(",") if x != ""]
            values = list(set(values1 + values2))
            df1[column][0] = ",".join(values)
    
    for column in dict_like_columns:
        column1_val = df1[column][0]
        column2_val = df2[column][0]        
        if pd.isnull(df1[column][0]):
            df1[column][0] = column2_val
        else:
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
            df1[column][0] = ",".join(["{" + ":".join(map(str, x)) + "}" for x in tuples1])

    for column in years_columns:
        column1_val = df1[column][0]
        column2_val = df2[column][0]  
        if pd.isnull(df1[column][0]):
            df1[column][0] = column2_val
            continue
        elif column == 'FirstYear':
            df1[column][0] = min(column1_val, column2_val)
            continue
        elif column == 'LastYear':
            df1[column][0] = max(column1_val, column2_val)
            continue
        else:
            values1 = [x for x in column1_val.split(",") if x != ""]
            values2 = [x for x in column2_val.split(",") if x != ""]
            things1 = [x.split(":")[0] if ":" in x else x for x in values1]
            minyears1 = [int(x.split(":")[1].split("-")[0]) for x in values1 if ":" in x]
            maxyears1 = [int(x.split(":")[1].split("-")[1]) for x in values1 if ":" in x]
            things2 = [x.split(":")[0] for x in values2]
            minyears2 = [int(x.split(":")[1].split("-")[0]) for x in values2]
            maxyears2 = [int(x.split(":")[1].split("-")[1]) for x in values2]
            tuples1 = list(zip(things1, minyears1, maxyears1))
            tuples2 = list(zip(things2, minyears2, maxyears2))
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
            df1[column][0] = ",".join([f"{x[0]}:{x[1]}-{x[2]}" for x in tuples1])

    df = df[(df['artist'] != secondary_artist_name) & (df['artist'] != primary_artist_name)]
    df = pd.concat([df, df1], ignore_index=True)
    return df