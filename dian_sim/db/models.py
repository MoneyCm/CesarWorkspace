import datetime
import json
import uuid
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    track = Column(String, nullable=False)  # FUNCIONAL | COMPORTAMENTAL | INTEGRIDAD
    competency = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    macro_dominio = Column(String, nullable=True) # Específico GOA
    micro_competencia = Column(String, nullable=True) # Específico GOA
    difficulty = Column(Integer, nullable=False) # 1-5
    stem = Column(Text, nullable=False)
    options_json = Column(JSON, nullable=False)
    correct_key = Column(String, nullable=True)
    rationale = Column(Text, nullable=True)
    source_refs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    hash_norm = Column(String, unique=True, nullable=False)

    attempts = relationship("Attempt", back_populates="question")

class Attempt(Base):
    __tablename__ = "attempts"

    attempt_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.question_id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    chosen_key = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_sec = Column(Integer, nullable=True)
    confidence_1_5 = Column(Integer, nullable=True)
    error_tag = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    question = relationship("Question", back_populates="attempts")

class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

class Achievement(Base):
    __tablename__ = "achievements"
    achievement_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    icon = Column(String) # Emoji or path
    unlocked_at = Column(DateTime, default=datetime.datetime.utcnow)


class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    track = Column(String, nullable=False)
    competency = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    macro_dominio = Column(String, nullable=True) # Específico GOA
    micro_competencia = Column(String, nullable=True) # Específico GOA
    mastery_score = Column(Float, default=0.0) # 0-100
    priority_weight = Column(Float, default=1.0)
    last_seen = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Unique constraint for track/competency/topic combination could be added via Index/UniqueConstraint
    # but for simplicity we'll handle uniqueness via application logic or add __table_args__

class Configuration(Base):
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True)
    key_name = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
