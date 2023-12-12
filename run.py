from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

INGREDIENT_SEPARATOR = '$'
PROMPT_ANSWER_SEPARATOR = '%'

BASE_MODEL_PATH = 'gpt2'


# Run the model
if __name__ == "__main__":

    ingredient_list = ['Paprika', 'Reis']

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
        "trained_model_gpt2/checkpoint-2000", trust_remote_code=True)

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

    # Generate text using model
    outputs = model.generate(
        inputs, max_new_tokens=1000, do_sample=True, top_k=50, top_p=0.95
    )
    # output = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Print output
    print(output)
