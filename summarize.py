import os
import argparse
from openai import OpenAI, APIConnectionError, AuthenticationError

# --- Configuration ---
# The base URL of your local API gateway
# The '/v1' part is crucial for the OpenAI library to work correctly.
LOCAL_API_BASE = "http://localhost:8000/v1"

def summarize_text(api_key: str, model_name: str, text_to_summarize: str) -> str:
    """
    Summarizes the given text using a local LLM via the API gateway.

    Args:
        api_key: The API key generated from your dashboard.
        model_name: The name of the Ollama model to use (e.g., 'llama3:8b').
        text_to_summarize: The block of text you want to summarize.

    Returns:
        The summarized text as a string, or an error message.
    """
    print(f"\n[*] Attempting to summarize using model: '{model_name}'...")

    try:
        # Step 1: Initialize the OpenAI client to point to our local gateway
        client = OpenAI(
            base_url=LOCAL_API_BASE,
            api_key=api_key,
        )

        # Step 2: Create the prompt
        # A good prompt is key to getting a good summary.
        prompt = f"Please provide a concise, one-paragraph summary of the following text:\n\n---\n\n{text_to_summarize}"
        
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Step 3: Send the request to the LLM
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2,  # Lower temperature for more factual summaries
            max_tokens=150,   # Limit the length of the summary
        )

        # Step 4: Extract and return the summary
        summary = response.choices[0].message.content.strip()
        return summary

    except APIConnectionError:
        return f"[ERROR] Could not connect to the server at {LOCAL_API_BASE}. Is your FastAPI server running?"
    except AuthenticationError:
        return "[ERROR] Authentication failed. Your API key is invalid or unauthorized for this model. Please check your key and permissions."
    except Exception as e:
        return f"[ERROR] An unexpected error occurred: {e}"

if __name__ == "__main__":
    # Set up command-line argument parsing for flexibility
    parser = argparse.ArgumentParser(description="Summarize text using a local LLM gateway.")
    parser.add_argument("--key", type=str, help="Your API key for the gateway.")
    parser.add_argument("--model", type=str, default="llama3:8b", help="The name of the model to use (default: llama3:8b).")
    parser.add_argument("--file", type=str, default="input.txt", help="Path to the text file to summarize (default: input.txt).")
    
    args = parser.parse_args()

    # Get the API key from command-line argument or environment variable
    api_key = args.key or os.environ.get("OLLAMA_API_KEY")

    if not api_key:
        print("[FATAL] API key not found!")
        print("Please provide it using the --key argument or by setting the OLLAMA_API_KEY environment variable.")
        exit(1)

    # Read the text from the specified file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            original_text = f.read()
    except FileNotFoundError:
        print(f"[FATAL] The input file '{args.file}' was not found.")
        exit(1)

    # Call the summarization function
    summary_result = summarize_text(api_key, args.model, original_text)

    # Print the results
    print("\n" + "="*50)
    print("--- ORIGINAL TEXT ---")
    print(original_text)
    print("\n" + "="*50)
    print("--- SUMMARY ---")
    print(summary_result)
    print("="*50)