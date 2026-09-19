from ai.ollama_client import analyze_conversation

messages = [
    {"role": "user", "content": "I want to build an e-commerce application."},
    {"role": "assistant", "content": "What type of products will you sell?"},
    {"role": "user", "content": "I will sell physical products."},
    {
        "role": "assistant",
        "content": "Will users need accounts before making purchases?",
    },
    {"role": "user", "content": "Yes, users must create an account before purchasing."},
]


result = analyze_conversation(messages)

print(result)
print()

print("Requirements:")

for requirement in result.requirements:
    print(f"{requirement.key} = {requirement.value}")

print()

print("Next question:")
print(result.next_question)
