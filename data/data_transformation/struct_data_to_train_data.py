import json
from itertools import combinations
from tqdm import tqdm
import random

# Load the original JSON data
with open('./data/data_acquisition/recipes.json', 'r', encoding='utf-8') as file:
    recipes = json.load(file)


def generate_combinations(ingredients):
    all_combinations = []
    # Generate combinations of all lengths from 1 to the length of ingredients list
    for r in range(1, len(ingredients) + 1):
        # Use combinations to generate all possible combinations of length r
        combinations_r = combinations(ingredients, r)
        # Extend the all_combinations list with the combinations generated
        all_combinations.extend(combinations_r)

    return all_combinations


def filter_available_ingredients(ingredients, available_ingredients):
    # Filter out ingredients that are not in available_ingredients
    non_available_ingredients = []
    for ingredient in ingredients:
        if ingredient not in available_ingredients:
            non_available_ingredients.append(ingredient)
    return non_available_ingredients


def comma_separate_list(list, key='name'):
    # Separate list with comma
    comma_separated_list = ''

    if len(list) == 1:
        comma_separated_list = list[0][key]
    elif len(list) == 2:
        comma_separated_list = f"{list[0][key]} und {list[1][key]}"
    else:
        for item in list:
            if item == list[-2]:
                comma_separated_list += f"{item[key]}" + " und "
            elif item == list[-1]:
                comma_separated_list += f"{item[key]}"
            else:
                comma_separated_list += f"{item[key]}" + ", "
    return comma_separated_list


def generate_ingredient_list(ingredients):
    ingredient_list = []
    for ingredient in ingredients:
        ingredient_list.append(ingredient['name'])
    return ingredient_list


def generate_full_ingredient_string(ingredients):
    # Generate a string of all ingredients
    full_ingredient_string = ''
    for ingredient in ingredients:
        if ingredient['amount'] is not None:
            full_ingredient_string += f"{ingredient['amount']} "
        if ingredient['unit'] is not None:
            full_ingredient_string += f"{ingredient['unit']} "
        if ingredient['name'] is not None:
            full_ingredient_string += f"{ingredient['name']}, "
    # Remove last comma
    full_ingredient_string = full_ingredient_string[:-2]
    return full_ingredient_string


# Function to generate prompts and answers for each recipe
def generate_training_data(recipe):
    training_data = []
    ingredients = recipe['ingredients']
    prep_time = recipe['prepTime']
    portions = recipe['numberOfPortions']

    # generate a list of all different ingredient combinations
    ingredient_combinations = generate_combinations(ingredients)

    # Limit the number of ingredient combinations per recipe to 100
    if len(ingredient_combinations) > 100:
        # print(
        #    f"Number of ingredient combinations for recipe {recipe['name']} is greater than 100. Randomly selecting 100 ingredient combinations.")
        # Randomly select 100 ingredient combinations
        ingredient_combinations = random.sample(
            ingredient_combinations, 100)

    for ingredient_combination in ingredient_combinations:
        available_ingredients = generate_ingredient_list(
            ingredient_combination)

        # Finding missing ingredients not in ingredient_combination
        non_available_ingredients_string = comma_separate_list(filter_available_ingredients(
            ingredients, ingredient_combination))

        if len(non_available_ingredients_string) == 0:
            answer = f'Du hast alle Zutaten für das folgende Rezept: {recipe["name"]}. '
        else:
            answer = f'Wenn du noch {non_available_ingredients_string} besorgst, kannst du das folgende Rezept nachkochen: {recipe["name"]}. '
        answer += 'Dazu brauchst diese Zutaten: ' + \
            generate_full_ingredient_string(ingredients) + '. '

        answer += f"Und so wird's gemacht: {recipe['instructions']} "

        answer += f"Dieses Rezept dauert circa {prep_time} Minuten und ergibt {portions} Portionen."

        training_data.append(
            {'available_ingredients': available_ingredients, 'answer': answer})

    return training_data


# Create a new JSON structure with prompts and answers for each recipe
prompt_answer_pair = []
skipped_recipes = []
recipe_number = 0
for recipe in tqdm(recipes):
    # add an ID and increment it for every recipe
    recipe_number += 1
    # Only consider recipes with less than 15 ingredients
    if len(recipe['ingredients']) > 15:
        skipped_recipes.append(recipe['name'])
        continue
    recipe_data = {
        "recipeNumber": recipe_number,
        "chefkochId": recipe['chefkochID'],
        "training_data": generate_training_data(recipe)
    }
    prompt_answer_pair.append(recipe_data)

print(f"Number of prompt-answer-pairs generated: {len(prompt_answer_pair)}")
print(f"Number of skipped recipes: {len(skipped_recipes)}")

# Save the new JSON data to a file
with open('./data/data_transformation/training_data.json', 'w', encoding="utf-8") as new_file:
    json.dump(prompt_answer_pair, new_file,
              ensure_ascii=False, indent=2)

# Save the skipped recipes to a file
with open('./data/data_transformation/skipped_recipes.json', 'w', encoding="utf-8") as new_file:
    json.dump(skipped_recipes, new_file,
              ensure_ascii=False, indent=2)
