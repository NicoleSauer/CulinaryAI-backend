import json

DATA = './data/data_acquisition/structured_recipes.json'

# Load the JSON file
with open(DATA, 'r', encoding="utf-8") as file:
    recipes_data = json.load(file)

# Extract ingredients list and generate prompts for each recipe
output_data = []

for recipe in recipes_data:
    ingredients = [ingredient['name'] for ingredient in recipe['Ingredients']]
    prompts = {
        "Id": recipe["Id"],
        "Name": recipe["Name"],
        "Ingredients": ingredients,
    }

    # No list
    # Generate prompts based on available ingredients
    # prompts.update({
    #    f"Prompt_{i+1}": f"Ich habe folgende Zutaten gefunden: {', '.join(ingredients[:len(ingredients)-i])}. Welches Rezept kann ich damit nachkochen?"
    #    for i in range(len(ingredients))
    # })
    # output_data.append(prompts)

    # List
    # Generate prompts based on available ingredients and organize as a list
    # TODO: maybe set a limit for the number of prompts
    prompts_list = [
        f"Ich habe folgende Zutaten gefunden: {', '.join(ingredients[:len(ingredients)-i])}. Welches Rezept kann ich damit nachkochen?"
        for i in range(len(ingredients))
    ]
    prompts["Prompts"] = prompts_list  # Add prompts list to the output

    # Generating Answers_to_prompts based on the last prompt and available ingredients
    last_prompt = prompts_list[-1]
    available_ingredients = ingredients[-1::-1]  # Reverse the ingredients list
    answers_to_prompts = [
        f"Wenn du noch die Zutat(en) {', '.join(available_ingredients[:i+1])} hättest, könntest du dieses Rezept probieren: {recipe['Name']}"
        for i in range(len(available_ingredients))
    ]
    prompts["Answers_to_prompts"] = answers_to_prompts
    output_data.append(prompts)

# Convert to JSON and print the result for each recipe
for recipe_output in output_data:
    output_json = json.dumps(recipe_output, indent=4, ensure_ascii=False)
    print(output_json)

# Save the prompts to a new JSON file
output_file = './data/data_transformation/prompts.json'

with open(output_file, 'w', encoding='utf-8') as output:
    json.dump(output_data, output, ensure_ascii=False, indent=4)
