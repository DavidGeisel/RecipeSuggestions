def load_heroku_postgresql_url():
    # store url in .txt file
    with open('heroku_postgresql_url.txt', 'r') as file:
        heroku_postgresql_url = file.read().rstrip()
    return heroku_postgresql_url