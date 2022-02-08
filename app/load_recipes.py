import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import nltk
from nltk import tokenize
nltk.download('punkt')
import ast 



def load_salad_recipes(ENV="Debug"):
    '''
    Loads preprocessed recipe database from postgresql table to pandas dataframe

    Arguments
    ENV -- Flag signalling whether to use developement or production database

    Returns
    df -- pandas dataframe containing recipe database
    '''

    # --Connect to PostgreSQL server local or remote
    if ENV == "Debug":
        engine = create_engine('postgresql://postgres:newPassword@localhost:5432/RecipeRecommendations')
        #engine = create_engine('postgresql://postgres:MySQLPW@localhost:5432/WhatToCook')
        dbConnection = engine.connect()
        df = pd.read_sql('recipes', dbConnection)
    else:
        heroku_postgresql_url = "..."
        engine = create_engine(heroku_postgresql_url)
        dbConnection = engine.connect()
        df = pd.read_sql('recipes', dbConnection)
    
    return df



def select_recommendations(cos_scores, nr_ingredients):
    '''
    Loads recipe data from sql database and extracts top recommendations based on score.

    Arguments:
    top_score -- list of top scores (ids) produced by recommendation model

    Returns:
    rec_ids -- list of ids of top recommendations
    rec_names -- list of recipe names of top recommendations
    rec_ingredients -- list of lists of ingredients needed for top recommendations
    '''

    # load recipe data
    df = load_salad_recipes(ENV="Debug")
    # --add scores to dataframe
    df['score'] = cos_scores
    # --sort df by scores
    df = df.sort_values('score', ascending=False)
    # --Exclude recipes with to many ingredients
    df = df[df["n_ingredients"] <= nr_ingredients*1.5]
    print("Max nr ingredients in recipes: ", df['n_ingredients'].max())

    # select top recommendations based on scores
    rec_ids = [] # list of recipe ids
    rec_names = [] # list of recipe names
    rec_ingredients = [] # list of ingredients needed for recommendations
    for i in range(3):
        rec_ids.append(int(df.iloc[i]['id']))
        rec_names.append(df.iloc[i]['recipe_name'])
        rec_ingredients.append(df.iloc[i]['parsed_ingredients'])
    
    return rec_ids, rec_names, rec_ingredients


def show_final_recipe(recipe_id):
    # load recipe data
    df = load_salad_recipes(ENV="Production")
    
    print("recipe_id: ", recipe_id)
    selected_recipe = df[df["id"] == recipe_id]
    print("selected_recipe: \n", selected_recipe)
    
    # ... get name of recipe as string
    recipe_name = selected_recipe["recipe_name"].values[0]
    print("recipe_name: ", recipe_name)
    
    # ... get cooking steps of recipe
    recipe_steps = ast.literal_eval(selected_recipe["cooking_method"].values[0])
    counter = 1 # add numbers to steps
    for i in range(0, len(recipe_steps)):
        recipe_steps[i] = str(counter) + ". " + recipe_steps[i]
        counter+=1
    print("Final version of steps: \n", recipe_steps)

    # ... get recipe ingredients of recipe as string
    recipe_ingredients = ast.literal_eval(selected_recipe['ingredients'].values[0])
    print("recipe_ingredients: ", recipe_ingredients)
    
    # ... get url of recipe image
    recipe_image = selected_recipe["image"].values[0]
    print("URL of image: ", recipe_image)
    print("type image: ", type(recipe_image))
    if type(recipe_image) == float:
        recipe_image = "/static/Blue_plate.png"
    # to many links not available, so return blue plate
    recipe_image = "/static/Blue_plate.png"

    
    
    return recipe_name, recipe_ingredients, recipe_steps, recipe_image