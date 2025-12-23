import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def _get_hf_token() -> str:
    """Fetch and sanitize HF token to avoid malformed Authorization headers."""
    token = os.environ.get("HF_TOKEN", "").strip()
    # Some dashboards prepend "HF_TOKEN="; strip it if present
    if token.lower().startswith("hf_token="):
        token = token.split("=", 1)[1].strip()
    if not token:
        raise ValueError("HF_TOKEN environment variable is missing or empty.")
    return token


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=_get_hf_token(),
)

def ask_llm(messages, temperature=0.0, max_tokens=2048):
    try:
        completion = client.chat.completions.create(
            model="Qwen/Qwen3-30B-A3B-Thinking-2507:nebius",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        if not completion.choices or len(completion.choices) == 0:
            return "Error: No choices returned from API"
        
        message = completion.choices[0].message
        
        # For thinking models, prefer content (final answer) over reasoning_content (thinking process)
        # Only use reasoning_content if content is not available, and extract just the final answer
        content = None
        if hasattr(message, 'content') and message.content:
            content = message.content
        elif hasattr(message, 'reasoning_content') and message.reasoning_content:
            # Extract final answer from reasoning content - remove all thinking process
            reasoning = message.reasoning_content
            
            # Strategy: Find where the actual answer/product list starts
            # Look for patterns that indicate the final conclusion
            
            # Pattern 1: Look for "So the products we extract are:" or similar
            import re
            patterns = [
                r"So the products (?:we )?extract (?:are|is):\s*(.+)",
                r"Products (?:extracted|we extract|are):\s*(.+)",
                r"Final (?:products|answer):\s*(.+)",
                r"Therefore,? the products (?:are|is):\s*(.+)",
                r"The products (?:are|is):\s*(.+)",
                r"So we (?:extract|suggest):\s*(.+)",
            ]
            
            final_answer = None
            for pattern in patterns:
                match = re.search(pattern, reasoning, re.IGNORECASE | re.DOTALL)
                if match:
                    final_answer = match.group(1).strip()
                    # Clean up - remove any trailing reasoning
                    # Stop at common reasoning continuation words
                    stop_words = ['But note:', 'However,', 'Given', 'We are', 'Step']
                    for stop_word in stop_words:
                        if stop_word in final_answer:
                            final_answer = final_answer.split(stop_word)[0].strip()
                    if final_answer:
                        break
            
            # Pattern 2: Look for JSON in the reasoning
            if not final_answer:
                json_match = re.search(r'\{[^{}]*"products"[^{}]*\[[^\]]*\][^{}]*\}', reasoning, re.DOTALL)
                if json_match:
                    final_answer = json_match.group(0).strip()
            
            # Pattern 3: Look for numbered/bulleted product lists at the end
            if not final_answer:
                lines = reasoning.split('\n')
                product_lines = []
                for i in range(len(lines) - 1, max(0, len(lines) - 15), -1):
                    line = lines[i].strip()
                    # Look for product list indicators
                    if (line and (
                        re.match(r'^\d+\.\s*(roti|lentils|vegetables|product)', line, re.IGNORECASE) or
                        re.match(r'^-\s*(roti|lentils|vegetables|product)', line, re.IGNORECASE) or
                        ('product' in line.lower() and len(line) < 100)
                    )):
                        product_lines.insert(0, line)
                        if len(product_lines) >= 3:  # Found enough products
                            break
                
                if product_lines:
                    final_answer = '\n'.join(product_lines)
            
            # Pattern 4: If still nothing, try to extract a concise summary from the end
            if not final_answer:
                # Get last 300 characters and try to extract meaningful content
                last_part = reasoning[-300:].strip()
                # Remove common reasoning phrases
                cleaned = re.sub(r'(But note:|However,|Given that|We are|Step \d+:)', '', last_part, flags=re.IGNORECASE)
                cleaned = cleaned.strip()
                if len(cleaned) > 50:  # Only use if substantial
                    final_answer = cleaned
            
            # If we found a final answer, use it; otherwise return a message asking for JSON
            if final_answer and len(final_answer) > 20:
                content = final_answer
            else:
                # Fallback: Return a message indicating we need JSON output
                content = "Please provide your response in JSON format with the products list."
        elif hasattr(message, 'text') and message.text:
            content = message.text
        
        if content is None or content == "":
            # Return debug info
            import json
            debug_info = {
                "completion_id": getattr(completion, 'id', None),
                "model": getattr(completion, 'model', None),
                "message_role": getattr(message, 'role', None),
                "has_reasoning_content": hasattr(message, 'reasoning_content'),
                "has_content": hasattr(message, 'content'),
                "choices_count": len(completion.choices) if completion.choices else 0
            }
            return f"Error: Content is None. Debug info: {json.dumps(debug_info, indent=2)}"
        
        return content
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error: {str(e)}\n\nTraceback:\n{error_details}"
