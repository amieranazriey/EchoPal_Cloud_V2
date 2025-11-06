# response_generator.py = defines a function that uses the Llama 3.1 model via Hugging Face’s Inference API to generate AI responses,
# optionally enhanced with contextual information retrieved from a knowledge base.

# Generation part from RAG

from huggingface_hub import InferenceClient

# Initialize Hugging Face Inference client with token
client = InferenceClient(model="meta-llama/Llama-3.1-8B-Instruct")

def generate_response(prompt, context=None):
    """
    Generate a response using Llama Instruct.
    If context is provided, prepend it to the prompt.
    """
    # Combine context with user prompt
    if context:
        full_prompt = f"Answer the question using the following context:\n{context}\n\nQuestion: {prompt}"
    else:
        full_prompt = prompt

    full_response = ""

    # Stream the response chunks as they arrive
    for chunk in client.chat_completion(
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=500,
            stream=True
    ):
        delta = chunk.choices[0].delta.get("content", "")
        if delta:
            full_response += delta

    return full_response

