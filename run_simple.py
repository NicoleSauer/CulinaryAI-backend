from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

# Run the model
if __name__ == "__main__":

    # Model input text
    input_text = "Nudeln$Tomaten$Zwiebeln"

    # Use local model (if available)
    # model = AutoModelForCausalLM.from_pretrained("./phi-1_5", trust_remote_code=True)

    # Use stock model from HuggingFace
    model = AutoModelForCausalLM.from_pretrained(
        "models/gpt2-large_2_epochs", trust_remote_code=True, local_files_only=False
    )

    # use stock tokenizer from HuggingFace
    tokenizer = AutoTokenizer.from_pretrained(
        "openai-community/gpt2-large", trust_remote_code=True, local_files_only=False, truncation=True, padding=True
    )

    # Encode input text into tokens
    inputs = tokenizer(input_text, return_tensors="pt").input_ids

    # Generate text using model
    outputs = model.generate(
        inputs, max_new_tokens=100, do_sample=True, top_k=50, top_p=0.95
    )
    output = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    # Print output
    print(output)
