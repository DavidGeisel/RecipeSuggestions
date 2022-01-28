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
from model import produce_foot_com_recommendations
#from flask_sqlalchemy import SQLAlchemy
#from send_mail import send_mail

app = Flask(__name__)
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
else:
    app.debug = False 

@app.route('/')
def index():
    return render_template('index.html')



'''
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        ingredients = request.form['comments']
    
        print(customer, ingredients)
        ingredients_list = ingredients.split(",")
        print(ingredients_list)

        # Error handling if no valid input
        if customer == '':
            return render_template('index.html', message="Please enter required fields")
        if ingredients == '':
            return render_template('no_food.html', message="It seems that you have to do some fasting today.")
        
        # Produce recommendations
        recommendations_df = produce_salad_recommendations(my_ingredients=ingredients_list)
        recipe_name = recommendations_df.iloc[0]["name"]
        recipe_ingredients = recommendations_df.iloc[0]["ingredients"]
        recipe_steps = recommendations_df.iloc[0]["steps"]
        print(recipe_steps)

        return render_template('success.html', message=f"Successfull db response",
        ingredients_list=ingredients_list,
        recipe_name=recipe_name,
        recipe_ingredients=recipe_ingredients,
        recipe_steps=recipe_steps)

'''
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        ingredients = request.form['comments']
    
        print(customer, ingredients)
        ingredients_list = ingredients.split(",")
        print(ingredients_list)

        # Error handling if no valid input
        if customer == '':
            return render_template('index.html', message="Please enter required fields")
        if ingredients == '':
            return render_template('no_food.html', message="It seems that you have to do some fasting today.")
        
        # Produce recommendations
        recommendations_df = produce_salad_recommendations(my_ingredients=ingredients_list)
        # ... get name of recipe as string
        recipe_name = recommendations_df.iloc[0]["recipe_name"]
        # ... get needed ingredients as list of strings
        recipe_ingredients = recommendations_df.iloc[0]["ingredients"].split()
        # ... get steps of cooking as list of strings (each step one item)
        recipe_steps = ast.literal_eval(recommendations_df.iloc[0]["cooking_method"])
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # convert sting into sentences
        steps = tokenize.sent_tokenize(recipe_steps[0])
        counter = 1 # add numbers to steps
        for i in range(0, len(steps)):
            steps[i] = str(counter) + ". " + steps[i]
            counter+=1
        # ... get url of image for cooked meal
        img = recommendations_df.iloc[0]["image"]
        print("URL of image: ", img)
        print("type image: ", type(img))
        if type(img) == float:
            img = "static/Blue_plate.png"
        
        print("Final image used: ", img)

        # render success page
        return render_template('success.html', message=f"Successfull db response",
        ingredients_list=ingredients_list,
        recipe_name=recipe_name,
        recipe_ingredients=recipe_ingredients,
        recipe_steps=steps,
        recipe_image=img)
        



if __name__ == '__main__':
    app.run()