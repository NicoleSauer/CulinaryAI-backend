from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
import streamlit as st

INGREDIENT_SEPARATOR = '$'
PROMPT_ANSWER_SEPARATOR = '%'
ANSWER_ENDING = '&'


@st.cache_resource
def initialize_model(model_name: str, tokenizer_model: str):
    """
    Initializes a model and tokenizer for generation
    :param model_name: The name of the model which should be used
    :param tokenizer_model: The model of which the tokenizer should be used
    :return: The model and tokenizer
    """

    # Use GPU if available
    if torch.cuda.is_available():
        torch.set_default_device("cuda")
    else:
        torch.set_default_device("cpu")

    # Use local model (if available)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, trust_remote_code=True)

    # use stock tokenizer from HuggingFace
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_model, trust_remote_code=True, padding=True, truncation=True
    )

    return model, tokenizer


def generate_recipe(
        model,
        tokenizer,
        ingredient_list: list,
        additional_instructions: str = None):
    """
    Generates a recipe based on a list of ingredients, with a specific model
    :param model: The model which should be used for generation
    :param tokenizer: The tokenizer which should be used for generation
    :param ingredient_list: The list of ingredients which should be used for generation
    :param additional_instructions: Can be used to specify instructions for the model. These will be set as
    first string inside the prompt. The ingredients follow right after. This should only be specified when using models
    which aren't fine-tuned!
    :return: The output of the specified model
    """

    # Model input text
    input_text = ""

    # Depending on the additional_instructions the input text is getting created
    if additional_instructions:
        input_text = additional_instructions

        for ingredient in ingredient_list:
            input_text += ' ' + ingredient + ','

    else:
        for ingredient in ingredient_list:
            # Only add ingredient separator if not last ingredient
            if ingredient != ingredient_list[-1]:
                input_text += ingredient + INGREDIENT_SEPARATOR
            else:
                input_text += ingredient

        # Add prompt answer separator
        input_text += PROMPT_ANSWER_SEPARATOR

    # Encode input text into tokens
    inputs = tokenizer(input_text, return_tensors="pt").input_ids

    # Move input to GPU if available
    if torch.cuda.is_available():
        inputs = inputs.to(torch.device("cuda"))
    else:
        inputs = inputs.to(torch.device("cpu"))

    # Set start time
    start_time = time.time()

    # Generate text using model
    outputs = model.generate(
        inputs, max_new_tokens=1000, do_sample=True, top_k=50, top_p=0.95
    )

    # output = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Post-processing of the output if there are no additional_instructions
    if not additional_instructions:
        # cut off at "Portionen"
        output = output.split('Portionen')[0] + 'Portionen.'

        # Cut off the first part before '%'
        output = output.split(PROMPT_ANSWER_SEPARATOR)[1]

        # TODO: cut off after '&' symbol for newest version of model
        output = output.split('&')[0]

    # Print time needed for generation with 2 decimal places
    print(f"Time needed: {time.time() - start_time:.2f} seconds")

    # Clear GPU cache
    torch.cuda.empty_cache()

    # Print output
    return output
