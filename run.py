from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time

INGREDIENT_SEPARATOR = '$'
PROMPT_ANSWER_SEPARATOR = '%'
ANSWER_ENDING = '&'

BASE_MODEL_PATH = 'microsoft/phi-1_5'


# Run the model
if __name__ == "__main__":

    ingredient_list = ['Kaviar', 'Senf', 'Hackfleisch']

    # Model input text
    input_text = ""
    for ingredient in ingredient_list:
        # Only add ingredient separator if not last ingredient
        if ingredient != ingredient_list[-1]:
            input_text += ingredient + INGREDIENT_SEPARATOR
        else:
            input_text += ingredient

    # Add prompt answer separator
    input_text += PROMPT_ANSWER_SEPARATOR

    # Use GPU if available
    if torch.cuda.is_available():
        torch.set_default_device("cuda")
    else:
        torch.set_default_device("cpu")

    # Use local model (if available)
    model = AutoModelForCausalLM.from_pretrained(
        "trained_model_microsoft_phi-1_5/checkpoint-220000", trust_remote_code=True)

    # Use stock model from HuggingFace
    # model = AutoModelForCausalLM.from_pretrained(
    #     "microsoft/phi-1_5", trust_remote_code=True
    # )

    # use stock tokenizer from HuggingFace
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL_PATH, trust_remote_code=True, padding=True, truncation=True
    )

    # Encode input text into tokens
    inputs = tokenizer(input_text, return_tensors="pt").input_ids

    # Set start time
    start_time = time.time()

    # Generate text using model
    outputs = model.generate(
        inputs, max_new_tokens=1000, do_sample=True, top_k=50, top_p=0.95
    )
    # output = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # cut off at "Portionen"
    # output = output.split('Portionen')[0] + 'Portionen.'

    # Cut off the first part before '%'
    output = output.split(PROMPT_ANSWER_SEPARATOR)[1]

    # TODO: cut off after '&' symbol for newest version of model
    output = output.split('&')[0]

    # Print output
    print(output)

    # Print time needed for generation with 2 decimal places
    print(f"Time needed: {time.time() - start_time:.2f} seconds")
