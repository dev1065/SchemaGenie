from ai.ollama_client import analyze_conversation
from models import Conversation, Message, Requirement
from sqlalchemy.orm import Session


def generate_conversation_response(
    conversation_id: int, user_content: str, db: Session
) -> Message:
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if conversation is None:
        raise ValueError("Conversation not found")

    user_message = Message(
        conversation_id=conversation_id, role="user", content=user_content
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
        {"role": message.role, "content": message.content} for message in messages
    ]

    analysis = analyze_conversation(conversation_messages)
    for extracted_requirement in analysis.requirements:
        requirement = (
            db.query(Requirement)
            .filter(
                Requirement.conversation_id == conversation_id,
                Requirement.key == extracted_requirement.key,
            )
            .first()
        )
        if requirement is None:
            requirement = Requirement(
                conversation_id=conversation_id,
                key=extracted_requirement.key,
                value=extracted_requirement.value,
            )
            db.add(requirement)
        else:
            requirement.value = extracted_requirement.value

    db.commit()
    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=analysis.next_question,
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    return ai_message
