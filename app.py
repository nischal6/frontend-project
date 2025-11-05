from flask import Flask, render_template, request, redirect, url_for
import json
import requests
import os
import time


app = Flask(__name__)

USER_RECIPES_FILE = 'user_recipes.json'  
USER_RECIEPES_FILE = 'user_recipes.json'


def load_user_recipes():
    if os.path.exists(USER_RECIPES_FILE):
        with open(USER_RECIPES_FILE,'r') as f:
            return json.load(f)
    return []

def save_user_recipes(recipes):
    with open(USER_RECIPES_FILE,'w') as f:
        json.dump(recipes, f, indent=4)


@app.route('/')
def home():
    search_query = request.args.get('search','').lower()

    response = requests.get('https://www.themealdb.com/api/json/v1/1/search.php?s=')
    meals_json = response.json()
    meals = meals_json['meals']
    user_added_meals = load_user_recipes()
    all_meals = meals + user_added_meals

    if search_query:
        all_meals = [i for i in all_meals if search_query in i['strMeal'].lower()]
    return render_template('recipes.html',meals=all_meals)

@app.route('/add',methods=['GET','POST'])
def add_recipe():   # fixed function name typo
    if request.method == 'POST':
        new_recipe = {
            'idMeal':str(int(time.time())),
            'strMeal':request.form['name'],
            'strCategory':request.form['category'],
            'strMealThumb':request.form['image'],
            'strInstructions':request.form['instructions'],
            'ingredients':request.form['ingredients'].split(',')
        }
        recipes = load_user_recipes()
        recipes.append(new_recipe)
        save_user_recipes(recipes)
        return redirect(url_for('home'))
    return render_template('add_recipe.html')

@app.route('/recipe/<meal_id>')
def recipe_details(meal_id):
    meal_detail_url = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}'
    response = requests.get(meal_detail_url)
    meal_data_json = response.json() 

    if not meal_data_json.get('meals'):
        recipes = load_user_recipes()
        for j in recipes:
            if j['idMeal'] == meal_id:   # fixed wrong variable reference
                return render_template('recipes_details.html', meal=j)
    
    meal = meal_data_json['meals'][0]
    return render_template('recipes_details.html', meal=meal)   # fixed .json to .html



if __name__ == "__main__":
    app.run(debug=True, port=5000)
