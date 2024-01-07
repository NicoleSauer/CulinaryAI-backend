import json
import run
import os
from enum import Enum
from datetime import datetime

class Language(Enum):
    """
    Class containing the enums for the language selection
    """
    DE = 'DE'
    EN = 'EN'

def evaluate_model_with_ingredients(
        base_model_name: str,
        model_or_checkpoint_name: str,
        output_json_name: str,
        language: Language,
        additional_instructions: str = None):

    # Output name of the json
    output_name = './evaluation/' + output_json_name

    # Input path of the json containing the ingredients
    input_path = ''

    # Array containing the objects with the outputs from the model
    output_object_array = []

    # Amount of retires, when trying to generate a recipe
    max_retries = 10

    # Selecting the input json depending on the language
    if language == Language.DE:
        input_path = './evaluation/input_de.json'
    elif language == Language.EN:
        input_path = './evaluation/input_en.json'

    # Load input data from json
    with open(input_path, 'r') as file:
        input_ingredients = json.load(file)

    # Create key value pair form the json
    for index, ingredient_list in enumerate(input_ingredients['ingredients']):
        ingredients_key = 'ingredients_' + str(index + 1)
        ingredients_list = ingredient_list[ingredients_key]

        # Try to generate a recipe and store result into an object which will be appended to an array
        retries = 0
        while retries < max_retries:
            try:
                output = generate_recipe(base_model_name, model_or_checkpoint_name, ingredients_list,
                                         additional_instructions)

                output_object = create_output_object(ingredients_key, ingredients_list, output)
                print(output_object)
                output_object_array.append(output_object)

                break
            except Exception as err:
                retries += 1
                print({
                    'Times failed': {retries},
                    'error': err,
                })
        else:
            print(f"Max retries ({max_retries}) reached for {ingredients_key}. Unable to generate recipe.")

    # Get current datetime for the name of the json containing the output of the model
    current_date = datetime.now()
    current_year = current_date.strftime("%Y")
    current_month = current_date.strftime("%m")
    current_day = current_date.strftime("%d")
    current_time = current_date.time()
    current_hour = current_time.strftime("%H")
    current_minute = current_time.strftime("%M")
    current_second = current_time.strftime("%S")
    current_milliseconds = current_time.microsecond

    with open(f'{output_name}_{current_year}_{current_month}_{current_day}_{current_hour}_{current_minute}_{current_second}_{current_milliseconds}.json', 'w', encoding='utf-8') as json_file:
        json.dump(output_object_array, json_file, ensure_ascii=False, indent=2)

    print('FINISHED')
    print(f'You can find the results in ./evaluation/{output_json_name}_{current_year}_{current_month}_{current_day}_{current_hour}_{current_minute}_{current_second}_{current_milliseconds}.json')


def generate_recipe(
        base_model_name: str, model_or_checkpoint_name: str, ingredients_list: list,
        additional_instructions: str) -> str:
    """
    Calls the method in the run.py file to generate a recipe
    :param base_model_name: The model of which the tokenizer should be used
    :param model_or_checkpoint_name: The model or checkpoint which should be used for generation
    :param ingredients_list: The list of ingredients which should be used for generation
    :param additional_instructions: Can be used to specify instructions for the model. These will be set as
    first string inside the prompt. The ingredients follow right after. This should only be specified when using models
    which aren't fine-tuned!
    :return: The output of the specified model
    """

    output = run.generate_recipe(base_model_name, model_or_checkpoint_name, ingredients_list, additional_instructions)

    return output


def create_output_object(ingredients_key: str, ingredients_list: list, output: str):
    """
    Creates an output object
    :param ingredients_key: The ingredients key from the input json
    :param ingredients_list:  The ingredients list from the input json
    :param output: The output from the model
    :return: The output object
    """

    output_object = {
        ingredients_key: [
            {"ingredients": ingredients_list},
            {"output": output},
        ]
    }

    return output_object


evaluate_model_with_ingredients(
    'microsoft/phi-1_5',
    'Phi-1_5_1_epoch',
    'microsoft-phi-1-5-1-epoch',
    Language.DE)