import requests
import sqlite3
import json
import os
from openai import OpenAI
import re


# Function input_ingredients asks for the user to input the ingredients that
# are available, stores them in a list and then returns the list as a comma
# separated string
def input_ingredients():
    num = int(input("Input the number of items left in your fridge: "))
    count, arr = 1, []
    while count <= num:
        ing = input(f"Input item {count}: ")
        count += 1
        arr.append(ing)
    ingredients = ','.join(arr)
    return ingredients


# Function fetch_recipes calls input ingredients for the required format of
# ingredients for the query. Get Request made to spoonacular api for recipes
# which require those ingredients and the response data is printed
def fetch_recipes():
    ingredients = input_ingredients()
    api_key = os.getenv('API_KEY_FOOD')
    url = 'https://api.spoonacular.com/recipes/findByIngredients'
    params = {
        'ingredients': ingredients,
        'number': 3,        # number of recipes I want from the API database
        'apiKey': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    recipe_list = []
    for recipe in data:
        recipe_input = ""
        recipe_input += f"Title: {recipe['title']}\n"
        recipe_input += f"Image: {recipe['image']}\n"

        recipe_input += "Used Ingredients:\n"
        for ingredient in recipe['usedIngredients']:
            recipe_input += f"""  - {ingredient['name']}:
            {ingredient['amount']} {ingredient['unit']}\n"""

        recipe_input += f"""Missed Ingredients
        ({recipe['missedIngredientCount']}):\n"""
        for ingredient in recipe['missedIngredients']:
            recipe_input += f"""  - {ingredient['name']}:
            {ingredient['amount']} {ingredient['unit']}\n"""
        recipe_list.append(recipe_input)

    return recipe_list


# Function has parameter - recipe_list. recipe_list contains ingredients and
# other information. The function uses openai api on the recipe_list and
# generates proper recipes and returns the 3 recipes.
def gpt_output(recipe_list: list):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a chef making 3 recipes
             based on 3 sets of ingredients given to you."""},
            {"role": "user", "content": f"""Construct 3 separate recipes with
            the corresponding ingredients from the list provided:{recipe_list}
            """}
        ]
    )
    output = (completion.choices[0].message.content)
    return output


# Function has parameter - markdown_content. Function opens a file, writes the
# parameter's content and prints a success message.
def redirect_output(markdown_content: list):
    with open("Recipe2.md", "w") as file:
        file.write(markdown_content)
    print("Markdown file created successfully.")


# Function has 2 params - recipe_list and gpt_out_recipe. It parses through
# the 2 inputs using regex's, creates a database and inserts the contents
# of the parsing into the database. It prints a success message.
def store_in_db(recipe_list: list, gpt_out_recipe: str):
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS My_Recipes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Ingredients TEXT,
            Recipes TEXT
        )
    ''')

    # Regex to deconstruct recipes in recipe list
    pattern = re.compile(r"""
    Title:\s+(?P<title>.*)\n
    Image:\s+(.*)\n
    Used\ Ingredients:\s*(?P<used_ingredients>(?:\n\s*-\s*.*)+)\n
    Missed\ Ingredients\ \(\d+\):\s*(?P<missed_ingredients>(?:\n\s*-\s*.*)+)
    """, re.VERBOSE)

    # Pattern for ingredients groups
    pat_for_ing = re.compile(r"\s*-\s*(.*)")

    # Array for gpt_output recipes
    generated_recipes_array = re.split(r"### \d+. ", gpt_out_recipe)
    count = 1

    # Matching groups of regex's and inserting title, ingredients, and the
    # recipe given by GPT into user's personal database
    for recipe in recipe_list:
        match = pattern.search(recipe)
        if match:
            title = match.group('title')
            used_ing = match.group('used_ingredients')
            miss_ing = match.group('missed_ingredients')
            ui_list = [m.group(1) for m in pat_for_ing.finditer(used_ing)]
            mi_list = [m.group(1) for m in pat_for_ing.finditer(miss_ing)]
            all_ingredients = ui_list + mi_list
            my_recipe = generated_recipes_array[count]
            c.execute('''INSERT INTO My_Recipes (Title, Ingredients, Recipes)
                        VALUES (?, ?, ?)''',
                      (title, json.dumps(all_ingredients), my_recipe))
            count += 1
        else:
            print("Something went wrong, please re-run and enter valid inputs")

    conn.commit()
    conn.close()
    print("Recipes stored in the database successfully!!")


if __name__ == '__main__':
    recipe_list = fetch_recipes()
    gpt_recipes = gpt_output(recipe_list)
    redirect_output(gpt_recipes)
    store_in_db(recipe_list, gpt_recipes)
