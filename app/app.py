from cmath import nan
import os
from flask import Flask, flash, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from matplotlib.style import context
import pandas as pd
import ast 
import nltk
from nltk import tokenize
nltk.download('punkt')
from datetime import datetime

from model import produce_salad_recommendations

'''
Configure app and session
'''
app = Flask(__name__)
#app.secret_key = "super secret key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


'''
Enable development and production mode.

dev: local developement
production: online version of the app
'''
ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newPassword@localhost/RecipeRecommendations'
else:
    app.debug = False 
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


'''
Configure database with SQLAlchemy
'''
db = SQLAlchemy(app)



class SearchCalls(db.Model):
    '''
    searchcalls table in database will store all requests made to the app.

    The columns record the access time, name of the customer, inserted ingredients and 
    recommended recipes (by id)
    '''
    __tablename__ = 'searchcalls'
    call_id = db.Column(db.Integer, primary_key=True)
    access_time = db.Column(db.String(200))
    customer = db.Column(db.String(200))
    ingredients = db.Column(db.Text())
    rec_1_recipe_id = db.Column(db.Integer)
    rec_2_recipe_id = db.Column(db.Integer)
    rec_3_recipe_id = db.Column(db.Integer)

    def __init__(self, customer, ingredients, 
    rec_1_recipe_id, rec_2_recipe_id, rec_3_recipe_id):
        
        self.customer = customer
        self.ingredients = ingredients
        self.rec_1_recipe_id = rec_1_recipe_id
        self.rec_2_recipe_id = rec_2_recipe_id
        self.rec_3_recipe_id = rec_3_recipe_id
        self.access_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        


class Assessment(db.Model):
    '''
    assessment table in database will store customer feedback.

    The columns will record the name of the customer, the recipe suggested to the customer,
    the comments by the customer as well as the rating for the app.
    '''
    __tablename__ = 'assessment'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200))
    recipe_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, recipe_id, rating, comments):
        self.customer = customer
        self.recipe_id = recipe_id
        self.rating = rating
        self.comments = comments


def db_add_search_call(customer, ingredients, rec_ids):
    '''
    Add search call to database.

    Arguments:
    customer -- name of the customer requesting a recommendation
    ingredients -- ingredients inserted to search by customer
    rec_id_1 -- recipe id of first recommended recipe
    rec_id_2 -- recipe id of second recommended recipe
    rec_id_3 -- recipe id of third recommended recipe

    Output:
    Adds changes to database
    '''
    
    data = SearchCalls(customer=customer, 
                       ingredients=ingredients,
                       rec_1_recipe_id=rec_ids[0], 
                       rec_2_recipe_id=rec_ids[1], 
                       rec_3_recipe_id=rec_ids[2])
    db.session.add(data)
    db.session.commit()



'''
Start page of the app.

User is asked to insert name and ingredients at hand.
'''
@app.route('/')
def index():
    return render_template('index.html')




'''
User is presented with the top recommendations of recipe names based on 
the ingredients inserted.

User can select one of the recommendations to get full recipe.
'''
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        ingredients = request.form['comments']
        print('customer: ', customer)
        print('ingredients: ', ingredients)
        # store input in session
        session["customer"] = customer
        session["ingredients"] = ingredients
        
        ingredients_list = ingredients.split(",")
        print("Processed ingredients_list: ", ingredients_list)

        # Error handling if no valid input
        if customer == '':
            return render_template('index.html', message="Please enter required fields")
        if ingredients == '':
            return render_template('no_food.html', message="..")
        

        # Produce recommendations
        # --get recommendations dataframe
        recommendations_df = produce_salad_recommendations(my_ingredients=ingredients_list)
        # --write dataframe to pickle to use it later on
        recommendations_df.to_pickle("../data/recommendations_df.pkl")
        # --extract names of the first three recommended recipes
        rec_names = recommendations_df.iloc[0:3]["recipe_name"]
        # --extract ingredients of the first three recommended recipes
        rec_ingredients = recommendations_df.iloc[0:3]["ingredients"]
        # --extract ids from recommended recipes
        rec_ids = recommendations_df.iloc[0:3]['id']
        
        ## --extract cooking mehtods of the first three recommended recipes
        #cooking_methods = recommendations_df.iloc[0:3]["cooking_method"]
        ## --extract tags associated with the recommended recipes
        #tags = recommendations_df.iloc[0:3]["tags"]
        
        #print("Top recommended recipes: ")
        #for i in range(3):
        #    print(rec_names[i])
        #    print("Ingredients needed: ", rec_ingredients[i])
        
        # add data to database
        db_add_search_call(customer=customer, 
        ingredients=ingredients, 
        rec_ids=rec_ids)

        # Render recommendations
        return render_template('recommendations.html', message=f"Successfull db response",
        ingredients_list=ingredients_list,
        rec_names=rec_names,
        rec_ingredients=rec_ingredients)
        

'''
Result page for the selected recommendation.

User can insert feedback on the app at the bottom.
'''
@app.route('/submit/SelectedRecommendation', methods=['GET', 'POST'])
def follow_up():
    if request.method == 'POST':
        
        # Load dataframe with recommendations
        print('**************')
        print('SelectedRecommendation:')
        recommendations_df = pd.read_pickle("../data/recommendations_df.pkl")
        print(recommendations_df)
        # TODO: get this data from SQL databse?
        

        print("session.get(customer): ", session.get("customer"))

        # Identify selected recommendation
        selected_recommendation = int(request.form['selected_recommendation'])
        #print("Selected recipe recommendation index: ", selected_recommendation)
        #print("Recipe_name: ", recommendations_df.iloc[selected_recommendation]["recipe_name"])
        #print("Cooking_method: ", recommendations_df.iloc[selected_recommendation]["cooking_method"])
        # ... get name of recipe as string
        recipe_name = recommendations_df.iloc[selected_recommendation]["recipe_name"]
        # --store recipe name in session
        session["recipe_name"] = recipe_name
        # --store recipe id in session
        session["recipe_id"] = 9999
        # ... get needed ingredients as list of strings
        recipe_ingredients = recommendations_df.iloc[selected_recommendation]["ingredients"].split()
        # ... get steps of cooking as list of strings (each step one item)
        recipe_steps = ast.literal_eval(recommendations_df.iloc[selected_recommendation]["cooking_method"])
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
        img = recommendations_df.iloc[selected_recommendation]["image"]
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



#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/submit/SelectedRecommendation/ThankYou', methods=['GET', 'POST'])
def thank_you():
    if request.method == 'POST':
        
        # get assessment data
        # --get comments on app
        comments = request.form['comments']
        print('comments: ', comments)
        # --get rating value
        app_rating = request.form['app_rating']
        print('app_rating: ', app_rating)
        # --get customer from flask session
        customer = session.get("customer")
        print("session.get(customer): ", customer)
        # --get recipe_id from flask session
        recipe_id = session.get("recipe_id")
        print("session.get(recipe_name): ", session.get("recipe_name"))


        # add assessment to database
        data = Assessment(customer=session.get("customer"), 
                          recipe_id=session.get("recipe_id"), 
                          rating=app_rating, 
                          comments=comments)
        db.session.add(data)
        db.session.commit()
        
        

        # render success page
        return render_template('thank_you.html')
        
        

if __name__ == '__main__':
    app.run()