from models import Conversation, Requirement
from sqlalchemy.orm import Session


def create_requirement(
    conversation_id: int,
    key: str,
    value: str,
    db: Session
) -> Requirement:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if conversation is None:
        raise ValueError("Conversation not found")

    requirement = Requirement(
        conversation_id=conversation_id,
        key=key,
        value=value
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return requirement


def get_requirements(
    conversation_id: int,
    db: Session
) -> list[Requirement]:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if conversation is None:
        raise ValueError("Conversation not found")
    requirements = (
        db.query(Requirement)
        .filter(Requirement.conversation_id == conversation_id)
        .order_by(Requirement.created_at)
        .all()
    )

    return requirements


def update_requirement(
    requirement_id: int,
    value: str,
    db: Session
) -> Requirement:
    requirement = (
        db.query(Requirement)
        .filter(Requirement.id == requirement_id)
        .first()
    )

    if requirement is None:
        raise ValueError("Requirement not found")

    requirement.value = value
    db.commit()
    db.refresh(requirement)

    return requirement


def delete_requirement(
    requirement_id: int,
    db: Session
) -> None:
    requirement = (
        db.query(Requirement)
        .filter(Requirement.id == requirement_id)
        .first()
    )

    if requirement is None:
        raise ValueError("Requirement not found")

    db.delete(requirement)
    db.commit()


