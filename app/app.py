import os
from flask import Flask, flash, render_template, request
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

        if customer == '':
            return render_template('index.html', message="Please enter required fields")
        if ingredients == '':
            return render_template('no_food.html', message="It seems that you have to do some fasting today.")
        return render_template('success.html', message=f"Entered ingredients: <br/> {ingredients_list}")
        



if __name__ == '__main__':
    app.run()