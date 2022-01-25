import os
from flask import Flask, flash, render_template, request
from matplotlib.style import context
import pandas as pd

from model import produce_recommendations
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
        recommendations_df = produce_recommendations(my_ingredients=ingredients_list)
        recipe_name = recommendations_df.iloc[0]["name"]
        recipe_ingredients = recommendations_df.iloc[0]["ingredients"]
        recipe_steps = recommendations_df.iloc[0]["steps"]
        print(recipe_steps)

        return render_template('success.html', message=f"Successfull db response",
        ingredients_list=ingredients_list,
        recipe_name=recipe_name,
        recipe_ingredients=recipe_ingredients,
        recipe_steps=recipe_steps)
        



if __name__ == '__main__':
    app.run()