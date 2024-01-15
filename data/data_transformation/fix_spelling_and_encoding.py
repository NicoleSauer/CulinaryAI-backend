import json

# Load the JSON data from the file
with open('./data/data_acquisition/structured_recipes.json', 'r') as file:
    recipes = json.load(file)


# Function to correct the typo in the JSON data
def correct_typo(recipes_list):
    for recipe in recipes_list:
        # Check if 'carbonhydrates' is in the nutritionalValues dictionary
        if 'carbonhydrates' in recipe.get('nutritionalValues', {}):
            # Replace 'carbonhydrates' with 'carbohydrates'
            recipe['nutritionalValues']['carbohydrates'] = recipe['nutritionalValues'].pop(
                'carbonhydrates')
    return recipes_list


# Correct the typo in the loaded data
recipes = correct_typo(recipes)

# Write the corrected data back to the file
with open('recipes_corrected.json', 'w', encoding='utf-8') as file:
    # Save the corrected data to a new file
    json.dump(recipes, file, ensure_ascii=False, indent=2)
