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


def load_recipe_data():
    '''
    load recipe database

    Returns:
    raw_recipes -- dataframe of recipes
    '''

    #data_path = "../data/food-com/"
    #raw_recipes = pd.read_csv(data_path + "RAW_recipes.csv", converters={'ingredients': ast.literal_eval})
    data_path = "../data/salad-recipe-data/"
    raw_recipes = pd.read_csv(data_path + "recipes_82k.csv")
    
    return raw_recipes


def concat_ingredients(df):
    '''
    concatenates list of ingredients strings to one string
    '''
    
    df['ingredients'] = [' '.join(x) for x in df['ingredients']]
    
    return df


def add_dummy_recipe(df, ingredients):
    '''
    - adds a dummy recipe to the dataframe of recipes consisting of the input ingredients
    - concatenates list of ingredient strings to one string
    
    Arguments:
    df -- dataframe of recipes
    ingredients -- ingredients to be used for dummy recipe
    
    Returns:
    df -- df with included dummy recipe
    idx_dummy -- value of the id column of the dummy recipe
    '''
    
    ## assign an id for dummy recipe
    id_dummy = df["id"].max()+1

    # create data dict
    dummy = {"id":id_dummy,
             "name":"dummy", 
             "minutes":30, 
             "ingredients":ingredients}
    
    # append data to dataframe
    dummy_data = pd.Series(dummy)
    df = df.append(dummy_data, ignore_index=True)
    
    # we also want to return the index of the dummy recipe in the new dataframe
    idx_dummy = len(df) - 1
    
    # concatenate strings of ingredients lists
    df = concat_ingredients(df)
    
    return df, idx_dummy


def produce_foot_com_recommendations(my_ingredients):
    '''
    function produces recommendations for recipes based on ingredients

    Arguments:
    my_ingredients -- List of ingredients on which recommendations are based

    Returns:
    recommendations_df -- Dataframe with recommendations
    '''

    # Load recipe data
    raw_recipes = load_recipe_data()

    ## Exclude recipes with to many ingredients
    #df = raw_recipes[raw_recipes["n_ingredients"] < len(my_ingredients)]
    #print("Max nr ingredients in recipes: ", df['n_ingredients'].max())
    df = raw_recipes

    # only use important columns of data
    selection = ["name", "id", "minutes", "steps", "ingredients"]
    df = df[selection]

    # get random subset of data (complete dataset cannot be processed)
    if len(df) > 30000:
        df = df.sample(30000)
    
    # add dummy recipe built from input ingredients list to dataframe
    df, idx_dummy = add_dummy_recipe(df=df, ingredients=my_ingredients)

    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    '''
    # calculate cosine similarities
    tfidf = TfidfVectorizer()
    
    #Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(df['ingredients'])
    
    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    '''
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    '''
    count_vec = MultiLabelBinarizer()
    matrix = count_vec.fit_transform(df['ingredients'])
    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(matrix, matrix)
    #print("Shape of cosine sim matrix: ", cosine_sim.shape)
    '''
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    # convert lists of strings to strings
    count_vec = CountVectorizer()
    matrix = count_vec.fit_transform(df['ingredients'])
    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(matrix, matrix)
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------




    # get reverse mapping of indices
    indices = pd.Series(df.index, index=df['ingredients']).drop_duplicates()

    # get pairwise similarity scores and sort recipes based on them
    sim_scores = list(enumerate(cosine_sim[idx_dummy]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # select top 10 recommendations 
    sim_scores = sim_scores[1:11] # first one is dummy recipe itself

    print("sim_scores: ", sim_scores)
    
    # get the recipe indices
    recipe_indices = [i[0] for i in sim_scores]

    print("recipe_indices: ", recipe_indices)
    
    # return the top 10 most similar recipes
    recommendations_df = df.loc[recipe_indices]

    # remove dummy recipe from list of suggestions
    if 'dummy' in recommendations_df['name'].values:
        recommendations_df = recommendations_df.drop(recommendations_df[recommendations_df['name']=='dummy'].index)
        
    
    return recommendations_df


def load_salad_recipes():
    '''
    Loads preprocessed recipe database.

    Returns:
    df -- pandas dataframe containing recipe database
    '''
    
    df = pd.read_pickle("../data/Salad_Recipes.pkl")

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
    df = df[df["n_ingredients"] < len(my_ingredients)]
    print("Max nr ingredients in recipes: ", df['n_ingredients'].max())


    # calculate similarities
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf.fit(df['parsed_ingredients'])
    tfidf_recipe = tfidf.transform(df['parsed_ingredients'])
    
    # concatenate my_ingredients input into one string and convert to lower case
    my_ingredients = ' '.join(my_ingredients).lower()

    # use our pretrained tfidf model to encode our input ingredients
    input_ingredients_tfidf = tfidf.transform([my_ingredients])
    
    # calculate cosine similarity between actual recipe ingreds and input ingreds
    cos_sim = map(lambda x: cosine_similarity(input_ingredients_tfidf, x), tfidf_recipe)
    scores = list(cos_sim)

    # getting top 5 recomendations
    top_score = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
    recommendation_df = pd.DataFrame(columns = ['recipe_name', 
    'ingredients',
    'cooking_method',
    'cuisine',
    'image', 
    'score' ])
    count = 0

    for i in top_score:
        #print("top_score = ", i)
        #print("recipe name: ", df.iloc[i]['recipe_name'])

        recommendation_df.at[count, 'recipe_name'] = df.iloc[i]['recipe_name']
        recommendation_df.at[count, 'ingredients'] = df.iloc[i]['parsed_ingredients']
        recommendation_df.at[count, 'cooking_method'] = df.iloc[i]['cooking_method']
        recommendation_df.at[count, 'cuisine'] = df.iloc[i]['cuisine']
        recommendation_df.at[count, 'cuisine'] = df.iloc[i]['image']
        recommendation_df.at[count, 'score'] = "{:.3f}".format(float(scores[i]))
        count += 1

    print(recommendation_df)
    
    return recommendation_df


