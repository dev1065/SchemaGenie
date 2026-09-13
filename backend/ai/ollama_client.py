import ollama

MODEL_NAME = "qwen3.5:0.8b"


def generate_response(messages: list[dict[str, str]]) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages
    )
    return response["message"]["content"]
