import google_play_scraper as gs
import pandas as pd
import numpy as np 
import time
from datetime import datetime


def get_app_ids(genre: str = '', n_games: int = 10) -> list:
    """
    Gets Games Application ID's 
    Parameters: 
        genre (str): The game's genre 
        n_games (int): The number of games to be extracted (default is 10)
    Returns: 
        list: Lists of App Id's
    """
    letters = 'abcdefghijklmnopqrstuvwxyz'
    games = [] 
    search_data = gs.search(query = f"{genre} Games", lang = 'en', n_hits=50)
    for x in search_data:
        if x['genre'] == genre and x['appId'] not in games:
            games.append(x['appId'])

    while len(games) < n_games: 
        # Handling Timeout
        time.sleep(1.5)
        idx = np.random.randint(low = 0, high = 26, size = 1, dtype = int)
        search_data = gs.search(query = f"{genre} Games starting with the letter '{letters[idx[0]]}'", lang = 'en', n_hits=50)
        for x in search_data:
            if x['genre'] == genre and x['appId'] not in games:
                games.append(x['appId'])

    return games

def get_games_and_reviews(genre_of_games: list[str], n_games: int, num_reviews: int) -> list[pd.DataFrame, pd.DataFrame]:
    """
    Gets Game's Reviews and Info
    Parameters: 
        genre_of_games (list[str]): List of genre of games
        n_games (int): Number of games 
        num_reviews (int): Number of reviews to be fetch
    Returns:
        list[pd.DataFrame, pd.DataFrame]: List of Dataframes for reviews & Game info
    """
    dataframes = []
    game_info_list = []
    for genre in genre_of_games:
        app_ids = get_app_ids(genre = genre, n_games = n_games)
        for app in app_ids:
            # Reviews
            result, continuation_token = gs.reviews(
                app_id=app,
                lang = 'en',
                country='us', 
                sort= gs.Sort.NEWEST, 
                count = num_reviews
            )
            data = pd.json_normalize(result)
            data['appId'] = app
            dataframes.append(data)  
            # Game info
            game_info = gs.app(
                app_id = app,
                lang='en', 
                country='us' 
            )
            game_info_list.append(game_info)
    return pd.concat(dataframes, axis = 0), pd.json_normalize(game_info_list)

if __name__ == '__main__':
    print("Fetching data..")
    reviews_df, game_df = get_games_and_reviews(genre_of_games=['Educational', 'Adventure', 'Action'], n_games = 30, num_reviews= 1500)
    reviews_df.to_parquet("./data/raw/reviews_{}.parquet".format(datetime.now().strftime('%Y-%m-%d_%H-%M_PH')), index=False, engine='pyarrow')
    game_df.to_parquet("./data/raw/games_{}.parquet".format(datetime.now().strftime('%Y-%m-%d_%H-%M_PH')), index=False, engine='pyarrow')
    print("Done.")