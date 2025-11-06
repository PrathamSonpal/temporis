from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime


class RoomType(str, Enum):
    theory = "theory"
    lab = "lab"


class SubjectType(str, Enum):
    theory = "theory"
    lab = "lab"


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str
    max_daily_load: int = 6
    unavailable_json: Optional[str] = None


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str
    type: SubjectType = SubjectType.theory
    hours_per_week: int = 2
    allow_double_period: bool = False


class ClassGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: int = 40


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    capacity: int = 60
    type: RoomType = RoomType.theory


class Timeslot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day: str
    start_time: str
    end_time: str
    slot_index: int
    is_lunch: bool = False


class ClassSubject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="classgroup.id")
    subject_id: int = Field(foreign_key="subject.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    required_hours: Optional[int] = None


class Assignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="classgroup.id")
    subject_id: int = Field(foreign_key="subject.id")
    teacher_id: int = Field(foreign_key="teacher.id")
    room_id: int = Field(foreign_key="room.id")
    timeslot_id: int = Field(foreign_key="timeslot.id")
    is_double: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
