from ai.ollama_client import generate_response
from models import Conversation, Message
from sqlalchemy.orm import Session


def generate_conversation_response(
    conversation_id: int,
    user_content: str,
    db: Session
) -> Message:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if conversation is None:
        raise ValueError("Conversation not found")

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=user_content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    conversation_messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]

    ai_response = generate_response(conversation_messages)

    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response
    )

    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return ai_message
