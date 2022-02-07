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

from load_recipes import load_salad_recipes


def produce_salad_recommendations(my_ingredients):
    '''
    function produces recommendations for recipes based on ingredients

    Arguments:
    my_ingredients -- List of ingredients on which recommendations are based

    Returns:
    recommendations_df -- Dataframe with recommendations
    '''

    # Load recipe data
    df = load_salad_recipes(ENV="Debug")

    # calculate similarities of recipe ingredients with inserted ingredients
    # --use tfidf vectorizer to count word frequencies in strings of ingredients
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf.fit(df['parsed_ingredients'])
    tfidf_recipe = tfidf.transform(df['parsed_ingredients'])
    print("tfidf_recipe.shape: ", tfidf_recipe.shape)
    # --concatenate my_ingredients input into one string and convert to lower case
    my_ingredients = ' '.join(my_ingredients).lower()
    # --use our pretrained tfidf model to encode our input ingredients
    input_ingredients_tfidf = tfidf.transform([my_ingredients])
    print("input_ingredients_tfidf.shape: ", input_ingredients_tfidf.shape)
    # --calculate cosine similarities
    cosine_sim = linear_kernel(input_ingredients_tfidf, tfidf_recipe)
    


    return cosine_sim[0]


