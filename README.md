# PainterPalette dataset: The (not so) soon-to-be richest public dataset of painters

<div align="center">
  <a href="https://github.com/me9hanics/PainterPalette?tab=MIT-1-ov-file">
    <img alt="MIT License" src="https://img.shields.io/badge/Code_License-MIT-f5de53?&color=f5de53">
  </a>
</div>

<div align="center">
  <img src="https://github.com/me9hanics/ArtProject/assets/82604073/7690b7fc-b46e-4e27-ae98-7aa8bc046dc5" width=70% alt="Painter Network">
</div>
<hr>

## Introduction

The aim of this project is to create a dataset of painters from sources such as WikiArt and Art500k, combining features, substituting missing data of painters via the Wikipedia API and make corrections/additions both automated and manually.

This includes:
- Bio data of a painter
- Artistic style data
- Locations of activity (sometimes with years)
- Influences (painters on other painters)
- Quantities of paintings, styles, etc.

The dataset is intended to be used for various purposes, including data analysis, machine learning, and visualization projects.<br>
One long-term goal would be to create a JSON file that contains all combined hierarchically. A level in the structure could be art movement, inside it, are artists with some base bio data, an even lower layer could be the paintings of the painter (even better could be eras of painters in their substructure, and inside them the paintings).

We have created multiple networks of painters (based on being at the same places at the same time + nationality, additionally style similarity, or who influenced whom networks) in another project (see: [ArtProject](https://github.com/me9hanics/ArtProject/)). A network of styles and movements were also created.

### Resulting file
The final dataset is stored in the *artists.csv* file (raw file here: [raw](https://raw.githubusercontent.com/me9hanics/PainterPalette/main/datasets/artists.csv), often this is better import / look at as it doesn't have the commit ID in the URL so this gives back always the freshest version).

### Next Steps
- Find the aliases of painters in Art500k dataset (one painter, multiple instances with different names e.g., Rembrandt and Rembrandt van Rijn); currently the methods are being developed and discussed (the two highest candidate methods are finding aliases through Wikipedia and Wikidata, and using a word embedding to find the very similar names).
- Broader combination of datasets (handle aliases, add more painters to the final dataset)


## Some visualizations using the dataset

<div align="center">
  <img src="https://github.com/me9hanics/ArtProject/assets/82604073/7690b7fc-b46e-4e27-ae98-7aa8bc046dc5" width=90% alt="Time-and-place network" >
  <br> <b>Figure 1:</b> Painters connected based on time and place (roughly if they painted at the same places at the same time), arranged in birth year order. The color of the nodes represents the movement most common in the painter's styles.
</div>

<div align="center">
  <img src="https://github.com/me9hanics/ArtProject/assets/82604073/039688be-16f0-4432-bae2-acba9688914b" width=75% alt="Movements network" >
  <br> <b>Figure 2:</b> Network of movements: two movements are connected if it's common enough that painters painted in both styles.
</div>

<div align="center">
  <img src="https://github.com/me9hanics/ArtProject/assets/82604073/fe2c11b3-0386-4655-857e-37e0632aa6d9" width=55% alt="Painter influence network" >
  <br> <b>Figure 3:</b> Network of painters based on who influenced whom.
</div> 



## Quick Start

You can use the dataset by importing it in your Python environment:

```python
import pandas as pd

url = "https://raw.githubusercontent.com/me9hanics/PainterPalette/main/datasets/artists.csv"
artists = pd.read_csv(url)
artists
```

The artists.csv file contains all information about painters, each row representing a painter, columns representing an attribute. An example of a few painters from the dataset:

<div class="output execute_result">

| ID | artist | Nationality | citizenship | gender | styles | movement | Art500k_Movements | birth_place | death_place | birth_year | death_year | FirstYear | LastYear | wikiart_pictures_count | locations | locations_with_years | styles_extended | StylesCount | StylesYears | occupations | PaintingsExhibitedAt | PaintingsExhibitedAtCount | PaintingSchool | Influencedby | Influencedon | Pupils | Teachers | FriendsandCoworkers | Contemporary | pictures_count |
|----|--------|-------------|-------------|--------|--------|----------|-------------------|-------------|-------------|------------|------------|-----------|----------|------------------------|-----------|----------------------|-----------------|-------------|-------------|-------------|---------------------|---------------------------|----------------|--------------|--------------|--------|----------|---------------------|---------------|----------------|
| 50 | Richard Pousette-Dart | American | United States of America | male | Abstract Art, Abstract Expressionism, Academicism | Abstract Art | {Abstract Expressionism:54} | Saint Paul | Rockland County | 1916.0 | 1992.0 | 1930.0 | 1992.0 | 54.0 | [] | [] | {Abstract Art:10},{Abstract Expressionism:43},{Academicism:1} | {Abstract Expressionism:43}, {Abstract Art:11}, {Academicism:1} | Abstract Expressionism:1940-1992,Abstract Art:1930-1992,Academicism:1944-1944 | photographer, painter, drawer | NY, New York City, US | {New York City:2},{NY:2},{US:2} | New York School,Irascibles | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 51 | Ethel Léontine Gabain | French,British | United Kingdom | female | Neo-Romanticism | Neo-Romanticism | NaN | Le Havre | London | 1883.0 | 1950.0 | 1930.0 | 1944.0 | 45.0 | [] | [] | {Neo-Romanticism:45} | NaN | NaN | lithographer, painter | London, Manchester, UK | {London:2},{UK:3},{Manchester:1} | NaN | NaN | NaN | NaN | NaN | NaN | No | NaN |
| 52 | Charles-Amable Lenoir | NaN | France | male | Academicism, Unknown | Academic Art | {Academic Art:9} | Châtelaillon-Plage | Paris | 1860.0 | 1926.0 | NaN | NaN | 9.0 | [] | [] | {Academicism:1},{Unknown:8} | {Academicism:1} | NaN | painter | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 53 | Francisco de Zurbaran | Spanish | Spain | male | Baroque, Unknown | Baroque | {Baroque:96} | Fuente de Cantos | Madrid | 1598.0 | 1664.0 | 1625.0 | 1664.0 | 154.0 | ['Seville', 'Madrid'] | ['Seville:1614-1658', 'Madrid:1658-1664'] | {Baroque:150},{Unknown:4} | {Baroque:94} | Baroque:1625-1664 | painter | Hungary, Museo del Prado, Paris, Barcelona, Budapest,Seville, Moscow, Pasadena, London, Sweden, France, Hartford, Grenoble, Munich, CA, Germany, Nationalmuseum, Stockholm, UK, Madrid, OH, St. Louis, Cleveland, Italy, MO, San Diego, Spain, Edinburgh, Besançon, Lyon, Montpellier, Bordeaux, Florence, US, Argentina, Russia, Saint Petersburg | {Grenoble:7},{France:19},{Seville:31},{Spain:36},{Bordeaux:1},{Besançon:1},{Barcelona:1},{Paris:4},{Budapest:3},{Hungary:3},{Saint Petersburg:1},{Russia:2},{Museo del Prado:14},{Madrid:19},{Munich:1},{Germany:1},{Moscow:1},{Lyon:1},{San Diego:2},{CA:4},{US:7},{Edinburgh:1},{UK:4},{Cleveland:1},{OH:1},{London:3},{Florence:1},{Italy:1},{St. Louis:1},{MO:1},{Pasadena:2},{Montpellier:1},{Argentina:1},{Nationalmuseum:1},{Stockholm:1},{Sweden:1},{Hartford:1} | NaN | Caravaggio, Gustave Courbet | NaN | Francisco Pacheco | NaN | No | NaN |
| 54 | Pieter van Hanselaere | Belgian | Belgium | male | Neoclassicism | Neoclassicism | {Neoclassicism:8} | Ghent | Ghent | 1786.0 | 1862.0 | 1817.0 | 1827.0 | 8.0 | ['Paris', 'Ghent', 'Italy'] | ['Paris:1809-1815,1812-1812', 'Italy:1815-1815'] | {Neoclassicism:8} | {Neoclassicism:8} | Neoclassicism:1817-1827 | painter | Netherlands, Amsterdam | {Amsterdam:2},{Netherlands:2} | NaN | NaN | NaN | Jacques-Louis David | NaN | No | NaN |
| 55 | Jean-Honore Fragonard | French | France | male | Rococo, Unknown | Rococo | {Rococo:72},{Renaissance:1} | Grasse | Paris | 1732.0 | 1806.0 | 1750.0 | 1790.0 | 69.0 | ['Vienna', 'Tivoli', 'Rome', 'Paris', 'Naples', 'Strasburg', 'Grasse', 'Prague', 'Dresden', 'Frankfurt'] | [] | {Rococo:64},{Unknown:5} | {Rococo:70} | Rococo:1750-1790 | illustrator, painter, printmaker, architectural draftsperson, drawer | Netherlands, Paris,London, Pasadena, Moscow, NY, Washington DC, France, Marseille, Munich, CA, Germany, New York City, MA, UK, Toledo, Madrid, OH, Rotterdam, St. Louis, Williamstown, MO, Spain, Amiens, Russia, US,France, Saint Petersburg | {France:21},{Paris:8},{Moscow:1},{Russia:3},{Saint Petersburg:2},{Washington DC:2},{US:9},{New York City:2},{NY:2},{Rotterdam:1},{Netherlands:1},{Toledo:1},{OH:1},{Munich:1},{Germany:1},{Williamstown:1},{MA:1},{London:1},{UK:1},{Amiens:1},{Pasadena:1},{CA:1},{St. Louis:1},{MO:1},{Marseille:1},{Madrid:1},{Spain:1} | NaN | NaN | NaN | NaN | NaN | No | NaN |
| 56 | Ion Theodorescu-Sion | Romanian | Romania | male | Art Nouveau (Modern), Impressionism, Post-Impressionism, Symbolism | Post-Impressionism | {Post-Impressionism:43} | Ianca | Bucharest | 1882.0 | 1939.0 | 1909.0 | 1938.0 | 43.0 | [] | [] | {Art Nouveau (Modern):1},{Impressionism:8},{Post-Impressionism:33},{Symbolism:1} | {Post-Impressionism:33}, {Impressionism:8}, {Cubism:2}, {Art Nouveau (Modern):1}, {Symbolism:1} | Post-Impressionism:1912-1938,Impressionism:1913-1934,Cubism:1925-1936,Art Nouveau (Modern):1925-1925,Symbolism:1909-1909 | trade unionist, caricaturist, painter | NaN | NaN | Balchik School | NaN | NaN | NaN | NaN | No | NaN |
| 57 | Janos Mattis-Teutsch | Hungarian,Romanian | Romania | male | Abstract Art, Constructivism, Cubism, Expressionism, Fauvism, Socialist Realism | Constructivism | {Art Nouveau:1},{Socialist realism:1},{Abstract art:1},{Modern art:1},{Constructivism:109} | Brașov | Brașov | 1884.0 | 1960.0 | 1909.0 | 1947.0 | 108.0 | [] | [] | {Abstract Art:59},{Constructivism:7},{Cubism:4},{Expressionism:2},{Fauvism:31},{Socialist Realism:5} | {Constructivism:11}, {Abstract Art:61}, {Expressionism:2}, {Cubism:4}, {Fauvism:31}, {Socialist Realism:5} | Constructivism:1925-1930,Abstract Art:1918-1925,Expressionism:1947-1947,Cubism:1926-1928,Fauvism:1909-1947,Socialist Realism:1928-1945 | writer, poet, painter, sculptor, journalist | NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |
| 58 | Apollinary Goravsky | Belarusian,Russian | Russian Empire | male | Romanticism | Romanticism | {Romanticism:12} | Novyja Nabarki | Mariinskaya Hospital | 1833.0 | 1900.0 | 1853.0 | 1897.0 | 12.0 | [] | [] | {Romanticism:12} | {Romanticism:12} | Romanticism:1853-1897 | painter | Russia, Moscow, Saint Petersburg, Minsk, Belarus | {Minsk:7},{Belarus:7},{Saint Petersburg:2},{Russia:3},{Moscow:1} | NaN | Belarusian National Museum of Fine Arts, Minsk, Belarus | NaN | NaN | NaN | NaN | No | NaN |
| 59 | Edouard Debat-Ponsan | French | France | male | Academicism | Academic Art | {Academic art:1},{Academic Art:11} | Toulouse | Paris | 1847.0 | 1913.0 | 1876.0 | 1902.0 | 15.0 | [] | [] | {Academicism:15} | {Academicism:11} | Academicism:1876-1902 | painter | NaN | NaN | NaN | NaN | NaN | NaN | NaN | No | NaN |

</div>


Capital first letter means the attribute is collected from Art500k paintings data, non-capital means the attribute is collected from WikiArt or Wikidata.

## Examples of Using the Code
Here are some examples of using the code to work with the dataset:

- Filter Renaissance painters:
```python
display(artists[artists['styles'].str.contains('Renaissance')])
```
<div class="output execute_result">

| artist | Nationality | birth_place | birth_year | styles | styles_extended | StylesYears | StylesCount | PlacesCount | Contemporary | FirstYear | LastYear | Places | PlacesYears | PaintingSchool | Influencedby | Influencedon | Pupils | Teachers | FriendsandCoworkers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Titian | Italian | Pieve di Cadore | 1490.0 | High Renaissance, Mannerism (Late Renaissance)... | {High Renaissance:109},{Mannerism (Late Renaissance... | Mannerism (Late Renaissance):1540-1576,High Renaissance:1500-1540 | {Renaissance / Mythological painting:1}, {Renaissance / Portrait:1} | {Italy:62},{Bologna:2},{Budapest:2},{Hungary:2... | No | 1500.0 | 1576.0 | Kroměříž, London, Romania, CA, Rotterdam, Frar... | Italy:1506-1576,Bologna:1533-1533,Budapest:154... | Venetian School | Albrecht Durer,Giorgione,Raphael,Michelangelo, | Jacopo Bassano,Peter Paul Rubens,Diego Velazqu... | El Greco,Annibale Carracci, | Giovanni Bellini, | Giorgione,Lorenzo Lotto, |
| Vittore Carpaccio | Italian | Venice | 1465.0 | High Renaissance, Unknown | {High Renaissance:46},{Unknown:7} | High Renaissance:1501-1502 | {XV Century Italian Painting:1}, {Italian:1}, ... | {Venice:7},{Italy:12},{Veneto:1},{Stuttgart:4}... | No | 1487.0 | 1516.0 | Galleria, Bergamo, Spain, Lisbon, Rome, San Gi... | Venice:1495-1502,Italy:1493-1505,Veneto:1495-1... | Venetian School | Christianity,saints-and-apostles,Virgin-and-Ch... | Norton Simon Museum, Pasadena, CA, US,Uffizi G... | Legend of St. Ursula for the Scola di Sant'Ors... | NaN | Artists2/Vittore Carpaccio/The Glory Of St Vid... |
| Ambrogio Lorenzetti | Italian | Siena | 1290.0 | International Gothic, Proto Renaissance, Unknown | {International Gothic:9},{Proto Renaissance:9}... | International Gothic:1319-1345,Proto Renaissance:1342-1345 | {Gotic/ Altarpiece:2}, {International Gothic:1... | {Bologna:1},{Italy:2},{Florence:1},{Paris:1},{... | No | 1319.0 | 1345.0 | Italy, Paris, France, Florence, Bologna | Bologna:1344-1344,Italy:1342-1344,Florence:134... | Sienese School | Simone Martini,Duccio,Giotto,Byzantine Art,Flo... | Dante Gabriel Rossetti,William Holman Hunt,Joh... | NaN | NaN | NaN |
| Hans Holbein the Elder | NaN | Augsburg | 1465.0 | International Gothic, Northern Renaissance | {International Gothic:4},{Northern Renaissance... | NaN | NaN | NaN | No | 1495.0 | 1513.0 | NaN | NaN | NaN | NaN | NaN | NaN | NaN | NaN |

</div>


- List painters who lived in Paris:
```python
display(artists[(~artists['Places'].isna())&(artists['Places'].str.contains('Paris'))])
```

<div class="output execute_result">

| Artist                 | Nationality | Birth Place | Birth Year | Styles                                          | Styles Extended                                      | Styles Years                                          | Styles Count                                      | Places Count                                      | Contemporary | First Year | Last Year | Places                                          | Places Years                                      | Painting School | Influenced by | Influenced on                                      | Pupils                                          | Teachers | Friends and Coworkers |
|------------------------|-------------|-------------|------------|-------------------------------------------------|------------------------------------------------------|-------------------------------------------------------|----------------------------------------------------|----------------------------------------------------|--------------|------------|-----------|-------------------------------------------------|----------------------------------------------------|-----------------|---------------|----------------------------------------------------|--------------------------------------------------|----------|----------------------|
| Pierre-Narcisse Guerin | French      | Paris       | 1774.0     | Neoclassicism, Unknown                          | {Neoclassicism:49},{Unknown:1}                       | Neoclassicism:1793-1819                               | {Neoclassicism:50}                                  | {Saint Petersburg:2},{Russia:2},{France:12},{R... | No           | 1793.0     | 1819.0    | Russia, Saint Petersburg, Orleans, Versailles,... | Saint Petersburg:1811-1811,Russia:1811-1811,Fr...    | NaN           | NaN           | NaN                                                | Théodore Géricault,Eugene Delacroix,             | NaN      | NaN                  |
| Theo van Rysselberghe | Belgian     | Ghent       | 1862.0     | Impressionism, Neo-Impressionism, Pointillism,... | {Impressionism:19},{Neo-Impressionism:112},{Po...    | Post-Impressionism:1900-1926,Impressionism:188...    | {Post-Impressionism:65}, {Impressionism:34}, {... | {Otterlo:2},{Netherlands:6},{Amsterdam:1},{Utr... | NaN          | 1880.0     | 1926.0    | Belgium, Brussels, Netherlands, Otterlo, Hague... | Otterlo:1890-1890,Netherlands:1890-1920,Amster...    | Les XX        | NaN           | NaN                                                | NaN                                              | NaN      | NaN                  |
| ...                    | ...         | ...         | ...        | ...                                             | ...                                                  | ...                                                   | ...                                                | ...                                                | ...          | ...        | ...       | ...                                               | ...                                                | ...           | ...           | ...                                                | ...                                              | ...      | ...                  |
</div>

- Get Monet's number of paintings per style (those available on WikiArt), sorted by number of paintings:

<div class="cell code">

``` python
import pandas as pd

style_counts = pd.read_csv('https://raw.githubusercontent.com/me9hanics/PainterPalette/main/datasets/wikiart_artists_styles_grouped.csv')
display(style_counts[style_counts['artist']=="Claude Monet"].sort_values(by='count', ascending=False))
```

</div>


<div class="output execute_result">

              style        artist       movement  count
      Impressionism  Claude Monet  Impressionism   1341
            Realism  Claude Monet  Impressionism     12
            Unknown  Claude Monet  Impressionism     12
        Academicism  Claude Monet  Impressionism      1
           Japonism  Claude Monet  Impressionism      1

</div>
or alternatively, you could use the artists.csv file and group painters and styles together.


A lot more functionalities of the dataset are used in [ArtProject](https://github.com/me9hanics/ArtProject/).

## License
This project is licensed under the MIT License, corresponding author: Mihaly Hanics (CEU Vienna, Austria).<br>
Contact: hanicsm@gmail.com

## Other possible datasets/networks for researchers:

Linking painters/people/entities together:<br>
**PageRank / Wiki Connections**

Wiki Connections: partial dataset
<http://www.iesl.cs.umass.edu/data/data-wiki-links><br>
smaller dataset: <https://snap.stanford.edu/data/wikispeedia.html>


### Philosophy


**Philosopher's web**: Only available after paying 10$ for pro user
**Philosophy NLP data**: https://philosophydata.com/phil_nlp.zip



### Six Degrees of Francis Bacon

Network of the people connected to Francis Bacon, the network contains mostly born in the 16th century and are English so most
philosophers in this list are not super relevant, there is no Kant,
Nietzsche, etc. But good example of a network

<http://www.sixdegreesoffrancisbacon.com/?ids=10000473&min_confidence=60&type=network>

<details><summary><u>Code for obtaining graph</u></summary>
<p>
    
```python
import igraph as ig #To install: conda install -c conda-forge python-igraph  
people = pd.read_csv('datasets/SDFB_people_.csv')
relationships = pd.read_csv('datasets/SDFB_relationships_.csv')

#I used igraph, because it's faster than networkx, and graph-tool sucks on Windows
network = relationships.rename(columns={'id': 'relationship_id', }).drop(columns=['created_by', 'approved_by', 'citation'])
print(network.head(), '\n')
cols = network.columns.tolist()
cols = cols[1:3] + cols[0:1] + cols[3:]
network = network[cols]
network = network[network['person1_index'] != 10050190] #for some reason, there is no person with this id, I did a loop
# I used the documentation here: https://python.igraph.org/en/stable/generation.html#from-pandas-dataframe-s  this I followed
# this is important too: https://python.igraph.org/en/stable/api/igraph.Graph.html#DataFrame  
g = ig.Graph.DataFrame(network, directed=False, vertices=people[['id', 'display_name','historical_significance','birth_year','death_year']], use_vids=False)
print(g.summary().replace(',', '\n'))
```
    
</p>
</details>
<details><summary><u>Code for filtering</u></summary>
<p>
    
```python
filtered = g.vs.select(_degree = 0) #https://python.igraph.org/en/stable/tutorial.html#selecting-vertices-and-edges
g.delete_vertices(filtered)

import cairo #Needed for plotting #import cairocffi as cairo  # can do matplotlib too
#layout = g.layout(layout='auto')
#ig.plot(g, layout = layout) #ig.plot(g) #looks even worse

```
    
</p>
</details>
<details><summary><u>Code for obtaining graph</u></summary>
<p>
    
```python
layout = g.layout(layout='reingold_tilford_circular') #kamada_kawai requires too much computing, 'fruchterman_reingold' is too dense
visual_style = {}
visual_style["vertex_size"] = 5
visual_style["vertex_color"] = "blue"
visual_style['bbox'] = (900, 900)
visual_style["layout"] = layout
#ig.plot(g, **visual_style) #Commented out because it takes big memory
# Needs improvement, but it's a start
```
    
</p>
</details>

### Health:

<https://global.health/> they got nice data on diseases, probably
time-variant too, such as monkeypox, ebola.
    
Modeling of Biological + Socio-tech systems (MOBS) Lab: <https://www.mobs-lab.org/>