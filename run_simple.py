from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

# Run the model
if __name__ == "__main__":

    # Model input text
    input_text = "Paprika$Nudeln"

    # Use local model (if available)
    # model = AutoModelForCausalLM.from_pretrained("./phi-1_5", trust_remote_code=True)

    # Use stock model from HuggingFace
    model = AutoModelForCausalLM.from_pretrained(
        "models/Phi-1_5_1_epoch/", trust_remote_code=True, revision='24f9ea14df973a49a0d87c16d04df88d90067468', local_files_only=False
    )

    # use stock tokenizer from HuggingFace
    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/phi-1_5", trust_remote_code=True, revision='24f9ea14df973a49a0d87c16d04df88d90067468', local_files_only=False
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
