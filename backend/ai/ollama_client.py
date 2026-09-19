import ollama
from schemas import AIAnalysisResponse

MODEL_NAME = "qwen3.5:4b"


SYSTEM_PROMPT = """
You are SchemaGenie, an AI requirements analyst.

Your job is to understand the user's application requirements by asking
focused questions.

Rules:
- Never invent or assume requirements.
- Only treat information explicitly stated by the USER as a requirement.
- Ask only ONE question at a time.
- Never repeat a question that has already been answered.
- Ask about the most important missing requirement.
- Do not suggest features, technologies, architecture, databases, or other
  solutions unless the user asks for suggestions.
- Keep responses short and clear.
- Use the conversation history when answering the user.

Your goal is to understand the application well enough to create its
requirements and eventually its data model.
"""

ANALYSIS_SYSTEM_PROMPT = """
You are SchemaGenie's requirements extractor.

Your job is to read the ENTIRE conversation and extract every application
requirement explicitly stated by the USER.

The conversation contains messages with roles:
- USER
- ASSISTANT

IMPORTANT:
- Only USER messages can introduce or change requirements.
- Treat every USER message as potentially containing one or more requirements.
- Never skip a requirement just because it appears in a short or simple sentence.
- Never infer, assume, or invent requirements.
- Assistant messages are context only. Never extract requirements from them.
- If the user explicitly changes a previous requirement, keep only the latest value.
- Do not create duplicate requirements.
- Use concise snake_case keys.
- Preserve the meaning of the user's statement.

After extracting the requirements, ask exactly ONE question about the most
important requirement that is still missing.

Do not ask about something that the USER has already explicitly answered.

Return ONLY this JSON object:

{
  "requirements": [
    {
      "key": "short_snake_case_key",
      "value": "requirement"
    }
  ],
  "next_question": "one question"
}

Example:

USER: I want to build an e-commerce application.
ASSISTANT: What type of products will you sell?
USER: I will sell physical products.
ASSISTANT: Will users need accounts before purchasing?
USER: Yes, users must create an account before purchasing.

Correct output:

{
  "requirements": [
    {
      "key": "application_type",
      "value": "e-commerce application"
    },
    {
      "key": "product_type",
      "value": "physical products"
    },
    {
      "key": "account_required_for_purchase",
      "value": "users must create an account before purchasing"
    }
  ],
  "next_question": "Will multiple sellers be able to sell products?"
}

Notice that "I will sell physical products" MUST be extracted because it is
an explicit USER requirement.

If the user has not provided enough information to determine an important
requirement, ask one question about it.

If there are no important missing requirements, use an empty string for
next_question.

Return only the JSON object.
"""


def generate_response(messages: list[dict[str, str]]) -> str:
    messages_with_system_prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
    ]

    response = ollama.chat(
        model=MODEL_NAME, messages=messages_with_system_prompt, think=False
    )

    content = response["message"]["content"].strip()

    if not content:
        raise RuntimeError("LLM returned an empty response")

    return content


def analyze_conversation(messages: list[dict[str, str]]) -> AIAnalysisResponse:

    analysis_messages = [
        {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
        *messages,
    ]

    response = ollama.chat(
        model=MODEL_NAME,
        messages=analysis_messages,
        format=AIAnalysisResponse.model_json_schema(),
        think=False,
    )

    content = response["message"]["content"].strip()

    if not content:
        raise RuntimeError("LLM returned an empty analysis")

    return AIAnalysisResponse.model_validate_json(content)
