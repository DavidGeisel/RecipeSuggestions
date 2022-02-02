import numpy as np
import pandas as pd
import ast
# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
#Import TfIdfVectorizer (scikit-learn)
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer



def load_salad_recipes():
    '''
    Loads preprocessed recipe database.

    Returns:
    df -- pandas dataframe containing recipe database
    '''
    
    df = pd.read_pickle("../data/Salad_Recipes.pkl")
    # TODO: insert data from SQL database

    return df


def produce_salad_recommendations(my_ingredients):
    '''
    function produces recommendations for recipes based on ingredients

    Arguments:
    my_ingredients -- List of ingredients on which recommendations are based

    Returns:
    recommendations_df -- Dataframe with recommendations
    '''

    # Load recipe data
    df = load_salad_recipes()

    ## Exclude recipes with to many ingredients
    df = df[df["n_ingredients"] <= len(my_ingredients)*1.5]
    #print("Max nr ingredients in recipes: ", df['n_ingredients'].max())


    # calculate similarities of recipe ingredients with inserted ingredients
    # --use tfidf vectorizer to count word frequencies in strings of ingredients
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf.fit(df['parsed_ingredients'])
    tfidf_recipe = tfidf.transform(df['parsed_ingredients'])
    # --concatenate my_ingredients input into one string and convert to lower case
    my_ingredients = ' '.join(my_ingredients).lower()
    # --use our pretrained tfidf model to encode our input ingredients
    input_ingredients_tfidf = tfidf.transform([my_ingredients])
    # --calculate cosine similarity between actual recipe ingreds and input ingreds
    cos_sim = map(lambda x: cosine_similarity(input_ingredients_tfidf, x), tfidf_recipe)
    scores = list(cos_sim)

    # Collect best recommendations in dataframe
    # --getting top 5 recomendations
    top_score = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
    # --initialize dataframe
    recommendation_df = pd.DataFrame(columns = ['id', 'recipe_name', 
    'ingredients',
    'cooking_method',
    'cuisine',
    'image', 
    'score' ])
    # --insert recommendations into dataframe
    count = 0
    for i in top_score:
        #print("top_score = ", i)
        #print("recipe name: ", df.iloc[i]['recipe_name'])
        recommendation_df.at[count, 'id'] = int(df.iloc[i]['id'])
        recommendation_df.at[count, 'recipe_name'] = df.iloc[i]['recipe_name']
        recommendation_df.at[count, 'ingredients'] = df.iloc[i]['parsed_ingredients']
        recommendation_df.at[count, 'cooking_method'] = df.iloc[i]['cooking_method']
        recommendation_df.at[count, 'cuisine'] = df.iloc[i]['cuisine']
        recommendation_df.at[count, 'cuisine'] = df.iloc[i]['image']
        recommendation_df.at[count, 'score'] = "{:.3f}".format(float(scores[i]))
        count += 1

    print("recommendation_df: ", recommendation_df)
    
    return recommendation_df


