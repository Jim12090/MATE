
import argparse
import base64
import json
import requests
import sys
import os

def encode_image(image_path):
    """Encodes an image to base64 string."""
    if not os.path.exists(image_path):
        print(f"Error: Image file prohibited or not found at {image_path}")
        sys.exit(1)
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_ollama(model, image_path, system_prompt, user_query):
    """Sends a request to the local Ollama instance."""
    url = "http://localhost:11434/api/chat"
    
    messages = []
    
    # Add system prompt if provided
    if system_prompt:
        messages.append({
            "role": "system", 
            "content": system_prompt
        })
    
    # Prepare user message
    user_message = {
        "role": "user", 
        "content": user_query
    }
    
    # Add image if provided
    if image_path:
        try:
            image_b64 = encode_image(image_path)
            user_message["images"] = [image_b64]
        except Exception as e:
            print(f"Failed to encode image: {e}")
            sys.exit(1)
    
    messages.append(user_message)
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False  # Disable streaming for simple synchronous response
    }
    
    print(f"Sending request to Ollama (Model: {model})...")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data.get('message', {}).get('content', "No content in response")
        
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running (typically on http://localhost:11434)."
    except requests.exceptions.RequestException as e:
        return f"Error calling Ollama API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Evaluate Qwen-VL model via Ollama")
    
    # Required arguments (or reasonable defaults if running interactively, but args suggested by request)
    parser.add_argument("--image", "-i", type=str, required=True, help="Path to the image file")
    
    # Optional configurations
    parser.add_argument("--query", "-q", type=str, default="Describe this image", help="User query prompt")
    parser.add_argument("--system", "-s", type=str, default="你是一个专注智慧农牧领域的视觉分析助手，能够识别猪,猫,狗, 鸟, 人, 车辆.请仔细观察图片，然后回答问题。", help="System prompt")
    parser.add_argument("--model", "-m", type=str, default="qwen3-vl:2b", help="Ollama model tag to use")
    
    args = parser.parse_args()
    
    result = call_ollama(args.model, args.image, args.system, args.query)
    
    print("\n" + "="*20 + " RESULT " + "="*20)
    print(result)
    print("="*48)

if __name__ == "__main__":
    main()
