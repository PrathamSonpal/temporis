from fastapi import APIRouter
from ..db import get_session, init_db
from ..models import Teacher, Subject, ClassGroup, Room, Timeslot, ClassSubject
from sqlmodel import select

router = APIRouter(prefix="/init", tags=["init"])

@router.post("/seed")
def seed():
    init_db()
    with get_session() as s:
        # Clear existing
        for model in [ClassSubject, Timeslot, Room, ClassGroup, Subject, Teacher]:
            rows = s.exec(select(model)).all()
            for r in rows:
                s.delete(r)
        s.commit()

        # Teachers
        t_math = Teacher(name="Dr. Sharma", code="T-MATH", max_daily_load=5)
        t_ds = Teacher(name="Ms. Rao", code="T-DS", max_daily_load=5)
        t_os = Teacher(name="Mr. Khan", code="T-OS", max_daily_load=5)
        t_eng = Teacher(name="Mrs. Patel", code="T-ENG", max_daily_load=5)
        t_lab = Teacher(name="Lab Incharge", code="T-LAB1", max_daily_load=6)
        s.add_all([t_math, t_ds, t_os, t_eng, t_lab]); s.commit()

        # Subjects
        sub_math = Subject(name="Mathematics", code="MATH", type="theory", hours_per_week=4)
        sub_ds = Subject(name="Data Structures", code="DS", type="theory", hours_per_week=4)
        sub_os = Subject(name="Operating Systems", code="OS", type="theory", hours_per_week=4)
        sub_eng = Subject(name="English", code="ENG", type="theory", hours_per_week=2)
        sub_lab = Subject(name="DS Lab", code="DSLAB", type="lab", hours_per_week=2, allow_double_period=True)
        s.add_all([sub_math, sub_ds, sub_os, sub_eng, sub_lab]); s.commit()

        # Classes
        c2a = ClassGroup(name="CSE-2A", size=48)
        c2b = ClassGroup(name="CSE-2B", size=52)
        s.add_all([c2a, c2b]); s.commit()

        # Rooms
        r101 = Room(name="R101", capacity=60, type="theory")
        r102 = Room(name="R102", capacity=60, type="theory")
        laba = Room(name="LAB-A", capacity=30, type="lab")
        labb = Room(name="LAB-B", capacity=30, type="lab")
        s.add_all([r101, r102, laba, labb]); s.commit()

        # Timeslots Mon-Fri 6 periods + lunch at 12-1 (slot 4 marked lunch)
        days = ["Mon","Tue","Wed","Thu","Fri"]
        hours = [("09:00","10:00"),("10:00","11:00"),("11:00","12:00"),
                 ("12:00","13:00"),("13:00","14:00"),("14:00","15:00")]
        for d in days:
            for idx,(st,et) in enumerate(hours, start=1):
                s.add(Timeslot(day=d, start_time=st, end_time=et, slot_index=idx, is_lunch=(idx==4)))
        s.commit()

        # Mappings
        s.refresh(c2a); s.refresh(c2b)
        s.refresh(sub_math); s.refresh(sub_ds); s.refresh(sub_os); s.refresh(sub_eng); s.refresh(sub_lab)
        s.refresh(t_math); s.refresh(t_ds); s.refresh(t_os); s.refresh(t_eng); s.refresh(t_lab)
        mappings = [
            ClassSubject(class_id=c2a.id, subject_id=sub_math.id, teacher_id=t_math.id),
            ClassSubject(class_id=c2a.id, subject_id=sub_ds.id, teacher_id=t_ds.id),
            ClassSubject(class_id=c2a.id, subject_id=sub_os.id, teacher_id=t_os.id),
            ClassSubject(class_id=c2a.id, subject_id=sub_eng.id, teacher_id=t_eng.id),
            ClassSubject(class_id=c2a.id, subject_id=sub_lab.id, teacher_id=t_lab.id),
            ClassSubject(class_id=c2b.id, subject_id=sub_math.id, teacher_id=t_math.id),
            ClassSubject(class_id=c2b.id, subject_id=sub_ds.id, teacher_id=t_ds.id),
            ClassSubject(class_id=c2b.id, subject_id=sub_os.id, teacher_id=t_os.id),
            ClassSubject(class_id=c2b.id, subject_id=sub_eng.id, teacher_id=t_eng.id),
            ClassSubject(class_id=c2b.id, subject_id=sub_lab.id, teacher_id=t_lab.id),
        ]
        s.add_all(mappings); s.commit()

    return {"status":"seeded"}
