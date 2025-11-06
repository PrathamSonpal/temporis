from fastapi import APIRouter
try:
    from ..db import get_session
    from ..models import Teacher, Subject, ClassGroup, Room, Timeslot, Assignment
except ImportError:
    from db import get_session
    from models import Teacher, Subject, ClassGroup, Room, Timeslot, Assignment
from sqlmodel import select

router = APIRouter(prefix="/meta", tags=["meta"])

@router.get("")
def meta():
    with get_session() as s:
        return {
            "teachers": s.exec(select(Teacher)).all(),
            "subjects": s.exec(select(Subject)).all(),
            "classes": s.exec(select(ClassGroup)).all(),
            "rooms": s.exec(select(Room)).all(),
            "timeslots": s.exec(select(Timeslot)).all(),
        }

@router.get("/timetable")
def timetable(view: str, id: int):
    with get_session() as s:
        q = select(Assignment)
        if view == "class":
            q = q.where(Assignment.class_id == id)
        elif view == "teacher":
            q = q.where(Assignment.teacher_id == id)
        elif view == "room":
            q = q.where(Assignment.room_id == id)
        items = s.exec(q).all()
        slots = s.exec(select(Timeslot)).all()
        return {"assignments": items, "timeslots": slots}
