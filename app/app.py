from cmath import nan
import os
from flask import Flask, flash, render_template, request
from matplotlib.style import context
import pandas as pd
import ast 
import nltk
from nltk import tokenize
nltk.download('punkt')

from model import produce_salad_recommendations

app = Flask(__name__)
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
else:
    app.debug = False 

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        ingredients = request.form['comments']
    
        print('customer: ', customer)
        print('ingredients: ', ingredients)
        
        ingredients_list = ingredients.split(",")
        print("Processed ingredients_list: ", ingredients_list)

        # Error handling if no valid input
        if customer == '':
            return render_template('index.html', message="Please enter required fields")
        if ingredients == '':
            return render_template('no_food.html', message="..")
        
        # Produce recommendations
        recommendations_df = produce_salad_recommendations(my_ingredients=ingredients_list)
        # write dataframe to pickle to use it later on
        recommendations_df.to_pickle("../data/recommendations_df.pkl")

        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------
        rec_names = recommendations_df.iloc[0:3]["recipe_name"]
        rec_ingredients = recommendations_df.iloc[0:3]["ingredients"]
        print("Top recommended recipes: ")
        for i in range(3):
            print(rec_names[i])
            print("Ingredients needed: ", rec_ingredients[i])
        
        
        # Render recommendations
        return render_template('recommendations.html', message=f"Successfull db response",
        ingredients_list=ingredients_list,
        rec_names=rec_names,
        rec_ingredients=rec_ingredients)
        


@app.route('/submit/follow_up', methods=['POST'])
def follow_up():
    if request.method == 'POST':
        
        # Load dataframe with recommendations
        recommendations_df = pd.read_pickle("../data/recommendations_df.pkl")

        print(recommendations_df)
        print('----------')

        # Identify selected recommendation
        selected_idx = int(request.form['rating'])

        print("Selected recipe recommendation index: ", selected_idx)
        print(recommendations_df.iloc[selected_idx]["recipe_name"])
        
        print(recommendations_df.iloc[selected_idx]["cooking_method"])

        
        # ... get name of recipe as string
        recipe_name = recommendations_df.iloc[selected_idx]["recipe_name"]
        # ... get needed ingredients as list of strings
        recipe_ingredients = recommendations_df.iloc[selected_idx]["ingredients"].split()
        # ... get steps of cooking as list of strings (each step one item)
        recipe_steps = ast.literal_eval(recommendations_df.iloc[selected_idx]["cooking_method"])
        print("recipe_steps: ", recipe_steps)
        print("type(recipe_steps): ", type(recipe_steps))
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # convert sting into sentences
        #steps = tokenize.sent_tokenize(recipe_steps[0])
        #print("steps: ", steps)
        steps = recipe_steps

        counter = 1 # add numbers to steps
        for i in range(0, len(steps)):
            steps[i] = str(counter) + ". " + steps[i]
            counter+=1
        # ... get url of image for cooked meal
        img = recommendations_df.iloc[selected_idx]["image"]
        print("URL of image: ", img)
        print("type image: ", type(img))
        if type(img) == float:
            img = "/static/Blue_plate.png"
        
        print("Final image used: ", img)

        # render success page
        return render_template('recommended_recipe.html', message=f"Successfull db response",
        recipe_name=recipe_name,
        recipe_ingredients=recipe_ingredients,
        recipe_steps=steps,
        recipe_image=img)
        
        

if __name__ == '__main__':
    app.run()