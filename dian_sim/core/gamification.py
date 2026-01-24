import datetime
from sqlalchemy.orm import Session
from db.models import UserStats, Attempt, Achievement
import uuid

from core.rank_system import get_rank_info

def update_user_stats(db: Session, last_session_date: datetime.date, correct_count: int, total_questions: int):
    """Actualiza puntos y rachas del usuario."""
    stats = db.query(UserStats).first()
    if not stats:
        stats = UserStats(current_streak=0, max_streak=0, total_points=0, last_activity=datetime.datetime.utcnow())
        db.add(stats)
        db.flush()

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # Lógica de Racha
    last_date = stats.last_activity.date()
    if last_date != today:
        if last_date == yesterday:
            stats.current_streak += 1
        else:
            stats.current_streak = 1
        
    if stats.current_streak > stats.max_streak:
        stats.max_streak = stats.current_streak

    # Lógica de Puntos (10 pts por acierto + bono por racha)
    session_points = correct_count * 10
    if stats.current_streak > 1:
        session_points += (stats.current_streak * 5)
        
    old_rank, _ = get_rank_info(stats.total_points)
    stats.total_points += session_points
    new_rank, _ = get_rank_info(stats.total_points)
    
    stats.last_activity = datetime.datetime.utcnow()
    
    # Verificar logros
    new_achievements = check_new_achievements(db, stats, correct_count, total_questions)
    
    db.commit()
    
    return stats, session_points, new_achievements, (new_rank['name'] if new_rank['name'] != old_rank['name'] else None)

def check_new_achievements(db: Session, stats: UserStats, correct_count: int, total_questions: int):
    """Verifica y desbloquea nuevos logros."""
    already_unlocked = [a.name for a in db.query(Achievement).all()]
    new_ones = []

    def unlock(name, desc, icon):
        if name not in already_unlocked:
            ach = Achievement(name=name, description=desc, icon=icon)
            db.add(ach)
            new_ones.append(ach)

    # REGLAS DE LOGROS
    unlock("Primer Paso", "Completaste tu primer simulacro.", "🚶")
    
    if stats.current_streak >= 3:
        unlock("Constancia", "Racha de 3 días aprendiendo.", "🔥")
        
    if stats.current_streak >= 7:
        unlock("Imparable", "Racha de una semana completa.", "⚡")

    if total_questions >= 10 and correct_count == total_questions:
        unlock("Perfección", "Simulacro perfecto (mínimo 10 preguntas).", "🎯")

    if stats.total_points >= 1500:
        unlock("Veterano", "Alcanzaste el rango de Auditor Senior.", "🛡️")

    return new_ones
