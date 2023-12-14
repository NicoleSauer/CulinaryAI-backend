import math
from datasets import Dataset
from transformers import AutoTokenizer, TrainingArguments, Trainer, AutoModelForCausalLM, DataCollatorForLanguageModeling
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm
import torch
import json
import os


INPUT_FILE_PATH = 'data/data_transformation/training_data.json'
# MODEL_PATH = 'microsoft/phi-1_5'
# MODEL_PATH = 'gpt2-large'
BASE_MODEL_PATH = 'gpt2'

LOCAL_MODEL_PATH = './trained_model_' + BASE_MODEL_PATH.replace('/', '_')
MODEL_PATH = LOCAL_MODEL_PATH if os.path.exists(
    LOCAL_MODEL_PATH) else BASE_MODEL_PATH


INGREDIENT_SEPARATOR = '$'
PROMPT_ANSWER_SEPARATOR = '%'

CLUSTER_FLAG = False

# Load HF Token from .env file
load_dotenv(find_dotenv())
access_token = os.environ["HF_TOKEN"]


# Load dataset from file
def load_data_generator_with_separator(recipe_list, separator=PROMPT_ANSWER_SEPARATOR):
    for recipe in recipe_list:
        for entry in recipe['training_data']:
            ingredient_string = ""
            for ingredient in entry['available_ingredients']:
                # Only add ingredient separator if not last ingredient
                if ingredient != entry['available_ingredients'][-1]:
                    ingredient_string += ingredient + \
                        INGREDIENT_SEPARATOR
                else:
                    ingredient_string += ingredient
            answer = entry['answer']
            # yield creates a Generator which means that the data is not loaded into memory all at once
            yield {"data": f"{ingredient_string}{separator}{answer}"}


def tokenize_entry(examples, tokenizer):
    return tokenizer(examples["data"], padding='max_length', truncation=True)


if __name__ == "__main__":
    print("Loading file and preparing training data...")
    with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as file:
        recipe_list = json.load(file)

    # Clear CUDA cache
    torch.cuda.empty_cache()

    print('Generating Dataset...')
    dataset = Dataset.from_generator(
        load_data_generator_with_separator, gen_kwargs={"recipe_list": recipe_list})

    print('Splitting Dataset into train and test...')
    dataset = dataset.train_test_split(
        test_size=0.2, shuffle=True, seed=42)

    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL_PATH, token=access_token)

    tokenizer.pad_token = tokenizer.eos_token

    print('Tokenizing training data...')
    tokenized_dataset = dataset.map(
        tokenize_entry,
        batched=False,
        num_proc=6,  # When training on cluster, set this to something else?
        remove_columns=dataset['train'].column_names,
        fn_kwargs={'tokenizer': tokenizer})

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False)

    print('Loading model...')
    if CLUSTER_FLAG:
        # Comment out torch_dtype=torch.float16 for cluster training or set it to auto
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH, token=access_token, trust_remote_code=True,
            # Set this to False to be able to download the model on the first run, set it to True afterwards
            local_files_only=True,
            # torch_dtype represents the data type of a PyTorch tensor -> bigger = high precision but higher memory usage, smaller = lower precision but also lower memory usage
            torch_dtype=torch.float16
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH, token=access_token, trust_remote_code=True,
            # Set this to False to be able to download the model on the first run, set it to True afterwards
            local_files_only=True,
            # torch_dtype=torch.float16
        )

    model.cuda()

    if CLUSTER_FLAG:
        # Play around with train_epochs, train_batch_size, eval_batch_size and maybe deactivate optimizer
        training_arguments = TrainingArguments(
            output_dir=LOCAL_MODEL_PATH,
            overwrite_output_dir=True,
            num_train_epochs=4,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            weight_decay=0.01,
            save_strategy='epoch',
            # save_steps=500,
            eval_steps=10000,
            # optim='adafactor'
        )
    else:
        training_arguments = TrainingArguments(
            output_dir=LOCAL_MODEL_PATH,
            overwrite_output_dir=True,
            num_train_epochs=4,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            weight_decay=0.01,
            save_strategy='steps',
            save_steps=1000,
            eval_steps=10000,
            save_total_limit=3,
            # optim='adafactor'
        )

    trainer = Trainer(
        model=model,
        args=training_arguments,
        train_dataset=tokenized_dataset['train'],
        eval_dataset=tokenized_dataset['test'],
        data_collator=data_collator
    )

    # Check which device is used for training
    current_device = torch.cuda.current_device()

    print('Training model with ' +
          torch.cuda.get_device_name(current_device) + '...')

    trainer.train(resume_from_checkpoint=True)
    trainer.save_model(LOCAL_MODEL_PATH)

    eval_results = trainer.evaluate()
    print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")
