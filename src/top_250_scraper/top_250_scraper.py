# Python 3.6.0

"""
This code retrives data from all the movies from the IMDb Top 250 page and stores them into files
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import csv

top_url = "https://www.imdb.com/chart/top/"
top_page = requests.get(top_url)
top_soup = BeautifulSoup(top_page.content, 'html.parser')
movies_charts = top_soup.find('tbody', class_='lister-list')
movies_elms = movies_charts.find_all('td', class_='titleColumn')
movie_ids = []
for elm in movies_elms:
    movie_id = re.search("title/(.*)/", elm.find('a')['href']).group(1)
    movie_ids.append(movie_id)

for movie_id in movie_ids:
    url = "https://www.imdb.com/title/" + movie_id + "/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    json_elm = soup.find('script', type='application/ld+json')
    data = json.loads(json_elm.string)

    mid = soup.find('meta', property="pageId")['content']
    title = data['name']
    release_date = data['datePublished']

    summary_elem = soup.find('div', class_='summary_text')
    summary = summary_elem.text.strip().replace('\n', '')   # Clean up text
    summary = re.sub(' +', ' ', summary)                    # Substitute multiple whitespace with single whitespace

    runtime_iso = soup.find('time')['datetime']
    runtime = int(runtime_iso[2:-1])  # Runtime in minutes

    rating = float(data['aggregateRating']['ratingValue'])
    num_votes = data['aggregateRating']['ratingCount']
    genres = data['genre']

    # CREDITS

    credits_url = "https://www.imdb.com/title/" + mid + "/fullcredits"
    credits_page = requests.get(credits_url)
    credits_soup = BeautifulSoup(credits_page.content, 'html.parser')
    directors = []
    writers = []
    actors = []

    crew_elms = credits_soup.find_all('table', class_="simpleTable simpleCreditsTable")
    directors_table = crew_elms[0]
    writers_table = crew_elms[1]
    cast_table = credits_soup.find('table', class_="cast_list")

    directors_names_elms = directors_table.find_all('td', class_='name')
    for elm in directors_names_elms:
        nmurl = elm.find('a')['href']
        pid = re.search("name/(.*)/", nmurl).group(1)
        name = elm.find('a').text.strip()
        director = {'pid': pid, 'name': name}
        directors.append(director)

    writers_elms = writers_table.find_all('tr')
    for elm in writers_elms:
        name_elm = elm.find('td', class_='name')
        if name_elm is not None:
            nmurl = name_elm.find('a')['href']
            pid = re.search("name/(.*)/", nmurl).group(1)
            name = name_elm.find('a').text.strip()
            credit_elm = elm.find('td', class_='credit')
            credit = None
            if credit_elm is not None:
                credit = credit_elm.text.strip()[1:credit_elm.text.strip().find(')')]
            writer = {'pid': pid, 'name': name, 'credit': credit}
            writers.append(writer)

    actors_elms = cast_table.find_all('tr')
    for i in range(1, len(actors_elms)):  # Start at 1 to skip first label element
        td_elms = actors_elms[i].find_all('td')
        try:
            name_elm = td_elms[1]
            nmurl = name_elm.find('a')['href']
            pid = re.search("name/(.*)/", nmurl).group(1)
            name = name_elm.find('a').text.strip()
            character = td_elms[3].text.strip().replace('\n', '')   # Clean up text
            character = re.sub(' +', ' ', character)                # Substitute multiple whitespace with single whitespace
            actor = {'pid': pid, 'name': name, 'character': character}
            actors.append(actor)
        except IndexError:  # Terminate loop when encounter label
            break

    # Rows of csv files
    movies_rows = []
    movie_genres_rows = []
    people_rows = []
    movie_credits_rows = []

    movies_rows.append([mid, title, release_date, summary, runtime, rating, num_votes])
    genres_dict = {'Action': 1, 'Adventure': 2, 'Animation': 3, 'Biography': 4, 'Comedy': 5, 'Crime': 6, 'Documentary': 7,
                   'Drama': 8, 'Family': 9, 'Fantasy': 10, 'Film-Noir': 11, 'Game-Show': 12, 'History': 13, 'Horror': 14,
                   'Music': 15, 'Musical': 16, 'Mystery': 17, 'News': 18, 'Reality-TV': 19, 'Romance': 20, 'Sci-Fi': 21,
                   'Sport': 22, 'Talk-Show': 23, 'Thriller': 24, 'War': 25, 'Western': 26}
    if isinstance(genres, str):
        movie_genres_rows.append([mid, genres_dict.get(genres)])
    else:
        for genre in genres:
            movie_genres_rows.append([mid, genres_dict.get(genre)])

    for director in directors:
        people_rows.append([director['pid'], director['name']])
    for writer in writers:
        people_rows.append([writer['pid'], writer['name']])
    for actor in actors:
        people_rows.append([actor['pid'], actor['name']])

    for director in directors:
        movie_credits_rows.append([mid, director['pid'], 1, None, None])
    for writer in writers:
        movie_credits_rows.append([mid, writer['pid'], 2, writer['credit'], None])
    for actor in actors:
        movie_credits_rows.append([mid, actor['pid'], 3, None, actor['character']])

    # Writing csv files
    with open('movies.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerows(movies_rows)
    with open('movie_genres.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerows(movie_genres_rows)
    with open('people.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerows(people_rows)
    with open('movie_credits.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerows(movie_credits_rows)
    """
    movie_data = {'mid': mid, 'title': title, 'release_date': release_date, 'summary': summary, 'directors': directors, 'writers': writers,
             'actors': actors, 'genres': genres, 'runtime': runtime, 'rating': rating, 'num_votes': num_votes}
    json_object = json.dumps(movie_data, indent=4)
    # Writing json into a file
    with open(mid + ".json", "w") as f:
        f.write(json_object)
    """
print('Done !')
