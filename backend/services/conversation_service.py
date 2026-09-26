from ai.ollama_client import analyze_conversation
from ai.requirement_reconciler import reconcile_requirements
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
    existing_requirements = (
        db.query(Requirement)
        .filter(Requirement.conversation_id == conversation_id)
        .order_by(Requirement.created_at)
        .all()
    )
    existing_requirement_data = [
        {"id": requirement.id, "key": requirement.key, "value": requirement.value}
        for requirement in existing_requirements
    ]
    new_requirement_data = [
        {
            "key": requirement.key,
            "value": requirement.value,
        }
        for requirement in analysis.requirements
    ]
    reconciliation = reconcile_requirements(
        existing_requirement_data, new_requirement_data
    )
    for change in reconciliation.changes:
        if change.action == "create":
            requirement = Requirement(
                conversation_id=conversation_id,
                key=change.key,
                value=change.value,
            )
            db.add(requirement)

        elif change.action == "update":
            requirement = (
                db.query(Requirement)
                .filter(
                    Requirement.id == change.requirement_id,
                    Requirement.conversation_id == conversation_id,
                )
                .first()
            )

            if requirement is None:
                raise ValueError("Requirement to update was not found")

            requirement.value = change.value
        elif change.action == "ignore":
            continue

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
