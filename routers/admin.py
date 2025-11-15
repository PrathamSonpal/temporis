# routers/admin.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlmodel import select
import csv, io
from db import get_session
from models import Teacher, Subject, ClassGroup, Room, ClassSubject

router = APIRouter(prefix="/admin", tags=["admin"])

# --- Simple CRUD endpoints (create only for now) ---

@router.post("/teacher")
def create_teacher(name: str = Form(...), code: str = Form(...), max_daily_load: int = Form(6)):
    with get_session() as s:
        t = Teacher(name=name, code=code, max_daily_load=max_daily_load)
        s.add(t); s.commit(); s.refresh(t)
        return {"status": "ok", "teacher": t}

@router.post("/subject")
def create_subject(name: str = Form(...), code: str = Form(...), type: str = Form("theory"), hours_per_week: int = Form(2), allow_double_period: bool = Form(False)):
    if type not in ("theory", "lab"):
        raise HTTPException(status_code=400, detail="type must be 'theory' or 'lab'")
    with get_session() as s:
        sub = Subject(name=name, code=code, type=type, hours_per_week=hours_per_week, allow_double_period=allow_double_period)
        s.add(sub); s.commit(); s.refresh(sub)
        return {"status":"ok", "subject": sub}

@router.post("/class")
def create_class(name: str = Form(...), size: int = Form(40)):
    with get_session() as s:
        c = ClassGroup(name=name, size=size)
        s.add(c); s.commit(); s.refresh(c)
        return {"status":"ok", "class": c}

@router.post("/room")
def create_room(name: str = Form(...), capacity: int = Form(40), type: str = Form("theory")):
    if type not in ("theory", "lab"):
        raise HTTPException(status_code=400, detail="type must be 'theory' or 'lab'")
    with get_session() as s:
        r = Room(name=name, capacity=capacity, type=type)
        s.add(r); s.commit(); s.refresh(r)
        return {"status":"ok", "room": r}

@router.post("/map")  # map class to subject with teacher
def create_mapping(class_id: int = Form(...), subject_id: int = Form(...), teacher_id: int = Form(...), required_hours: int | None = Form(None)):
    with get_session() as s:
        # validate presence
        if not s.exec(select(ClassGroup).where(ClassGroup.id == class_id)).first():
            raise HTTPException(status_code=404, detail="class not found")
        if not s.exec(select(Subject).where(Subject.id == subject_id)).first():
            raise HTTPException(status_code=404, detail="subject not found")
        if not s.exec(select(Teacher).where(Teacher.id == teacher_id)).first():
            raise HTTPException(status_code=404, detail="teacher not found")
        m = ClassSubject(class_id=class_id, subject_id=subject_id, teacher_id=teacher_id, required_hours=required_hours)
        s.add(m); s.commit(); s.refresh(m)
        return {"status":"ok", "mapping": m}

# --- CSV bulk upload ---
# Expected CSV columns (case-insensitive): entity, name, code, type, hours_per_week, teacher_code, class_name, size, room_name, capacity
# Each row should start with entity: teacher|subject|class|room|mapping
# mapping rows require: entity=mapping, class_name, subject_code, teacher_code, required_hours (optional)

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    try:
        s = io.StringIO(content.decode("utf-8-sig"))
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to decode file as UTF-8")
    reader = csv.DictReader(s)
    results = {"created": 0, "skipped": 0, "errors": []}
    with get_session() as db:
        for i, row in enumerate(reader, start=1):
            entity = (row.get("entity") or "").strip().lower()
            try:
                if entity == "teacher":
                    name = row.get("name") or row.get("teacher_name")
                    code = row.get("code") or row.get("teacher_code")
                    if not name or not code:
                        raise ValueError("teacher requires name and code")
                    t = Teacher(name=name.strip(), code=code.strip(), max_daily_load=int(row.get("max_daily_load") or 6))
                    db.add(t); db.commit(); db.refresh(t); results["created"] += 1
                elif entity == "subject":
                    name = row.get("name"); code = row.get("code")
                    tp = (row.get("type") or "theory").strip()
                    hours = int(row.get("hours_per_week") or 2)
                    if not name or not code:
                        raise ValueError("subject requires name and code")
                    sub = Subject(name=name.strip(), code=code.strip(), type=tp, hours_per_week=hours, allow_double_period=(row.get("allow_double_period","").strip().lower() in ("1","true","yes")))
                    db.add(sub); db.commit(); db.refresh(sub); results["created"] += 1
                elif entity == "class":
                    name = row.get("name") or row.get("class_name")
                    size = int(row.get("size") or 40)
                    if not name:
                        raise ValueError("class requires name")
                    c = ClassGroup(name=name.strip(), size=size)
                    db.add(c); db.commit(); db.refresh(c); results["created"] += 1
                elif entity == "room":
                    name = row.get("name") or row.get("room_name")
                    capacity = int(row.get("capacity") or 30)
                    tp = (row.get("type") or "theory").strip()
                    if not name:
                        raise ValueError("room requires name")
                    r = Room(name=name.strip(), capacity=capacity, type=tp)
                    db.add(r); db.commit(); db.refresh(r); results["created"] += 1
                elif entity == "mapping" or entity == "classsubject" or entity == "map":
                    class_name = row.get("class_name")
                    subject_code = row.get("subject_code") or row.get("subject")
                    teacher_code = row.get("teacher_code") or row.get("teacher")
                    required_hours = row.get("required_hours")
                    if not class_name or not subject_code or not teacher_code:
                        raise ValueError("mapping requires class_name, subject_code, teacher_code")
                    c_obj = db.exec(select(ClassGroup).where(ClassGroup.name == class_name.strip())).first()
                    s_obj = db.exec(select(Subject).where(Subject.code == subject_code.strip())).first()
                    t_obj = db.exec(select(Teacher).where(Teacher.code == teacher_code.strip())).first()
                    if not c_obj or not s_obj or not t_obj:
                        raise ValueError("referenced class/subject/teacher not found")
                    m = ClassSubject(class_id=c_obj.id, subject_id=s_obj.id, teacher_id=t_obj.id, required_hours=(int(required_hours) if required_hours else None))
                    db.add(m); db.commit(); db.refresh(m); results["created"] += 1
                else:
                    results["skipped"] += 1
            except Exception as e:
                results["errors"].append({"row": i, "error": str(e), "rowdata": row})
    return results
