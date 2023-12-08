from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


# Run the model
if __name__ == "__main__":

    # Model input text
    input_text = "A tasty recipe for chocolate chip cookies: "

    # Use GPU if available
    if torch.cuda.is_available():
        torch.set_default_device("cuda")
    else:
        torch.set_default_device("cpu")

    # Use local model (if available)
    # model = AutoModelForCausalLM.from_pretrained("./phi-1_5", trust_remote_code=True)

    # Use stock model from HuggingFace
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/phi-1_5", trust_remote_code=True
    )

    # use stock tokenizer from HuggingFace
    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/phi-1_5", trust_remote_code=True
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
