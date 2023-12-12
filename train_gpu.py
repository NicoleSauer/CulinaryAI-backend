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
MODEL_PATH = 'gpt2'

CLUSTER_FLAG = False

# Load HF Token from .env file
load_dotenv(find_dotenv())
access_token = os.environ["HF_TOKEN"]


# Load dataset from file
def load_data_generator_with_separator(recipe_list, separator='\t\t'):
    for recipe in recipe_list:
        for entry in recipe['training_data']:
            prompt = entry['prompt']
            answer = entry['answer']
            # yield creates a Generator which means that the data is not loaded into memory all at once
            yield {"data": f"{prompt}{separator}{answer}"}


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
        MODEL_PATH, token=access_token)

    tokenizer.pad_token = tokenizer.eos_token

    print('Tokenizing training data...')
    tokenized_dataset = dataset.map(
        tokenize_entry,
        batched=False,
        num_proc=6,
        remove_columns=dataset['train'].column_names,
        fn_kwargs={'tokenizer': tokenizer})

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False)

    if CLUSTER_FLAG:
        # Comment out torch_dtype=torch.float16 for cluster training
        print('Loading model...')
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH, token=access_token, trust_remote_code=True,
            local_files_only=True,
            torch_dtype=torch.float16
        )
    else:
        print('Loading model...')
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH, token=access_token, trust_remote_code=True,
            local_files_only=True,
            # torch_dtype=torch.float16
        )

    model.cuda()

    if CLUSTER_FLAG:
        # Play around with train_epochs, train_batch_size, eval_batch_size and maybe deactivate optimizer
        training_arguments = TrainingArguments(
            output_dir='./trained_model' + MODEL_PATH.replace('/', '_'),
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
            output_dir='./trained_model' + MODEL_PATH.replace('/', '_'),
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

    trainer = Trainer(
        model=model,
        args=training_arguments,
        train_dataset=tokenized_dataset['train'],
        eval_dataset=tokenized_dataset['test'],
        data_collator=data_collator
    )

    print('Training model...')
    trainer.train()
    trainer.save_model('./trained_model_' + MODEL_PATH.replace('/', '_'))

    eval_results = trainer.evaluate()
    print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")
