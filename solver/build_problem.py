from typing import Dict, List, Tuple
from sqlmodel import select
from ..models import ClassGroup, Subject, Teacher, Room, Timeslot, ClassSubject
from ..db import get_session

Var = Tuple[int,int,int,int]  # (class_id, subject_id, teacher_id, session_index)

def load_context():
    with get_session() as s:
        classes = s.exec(select(ClassGroup)).all()
        subjects = s.exec(select(Subject)).all()
        teachers = s.exec(select(Teacher)).all()
        rooms = s.exec(select(Room)).all()
        slots = s.exec(select(Timeslot)).all()
        maps = s.exec(select(ClassSubject)).all()
    by_id = lambda items: {x.id: x for x in items}
    return {
        "classes": by_id(classes),
        "subjects": by_id(subjects),
        "teachers": by_id(teachers),
        "rooms": by_id(rooms),
        "slots": by_id(slots),
        "slot_list": sorted(slots, key=lambda t:(t.day, t.slot_index)),
        "maps": maps,
    }

def sessions_for_map(ctx, m: ClassSubject) -> int:
    sub = ctx["subjects"][m.subject_id]
    return m.required_hours or sub.hours_per_week

def build_variables(ctx):
    vars_list = []
    for m in ctx["maps"]:
        n = sessions_for_map(ctx, m)
        for k in range(n):
            vars_list.append((m.class_id, m.subject_id, m.teacher_id, k))
    return vars_list

def timeslot_ok(slot, subject):
    if slot.is_lunch:
        return False
    return True

def build_domains(ctx) -> Dict[Var, List[Tuple[int,int]]]:
    domains = {}
    for v in build_variables(ctx):
        class_id, subject_id, teacher_id, k = v
        cl = ctx["classes"][class_id]
        sub = ctx["subjects"][subject_id]
        vals = []
        for slot in ctx["slot_list"]:
            if not timeslot_ok(slot, sub):
                continue
            for room in ctx["rooms"].values():
                if room.type != sub.type:
                    continue
                if room.capacity < cl.size:
                    continue
                vals.append((slot.id, room.id))
        domains[v] = vals
    return domains

def build_neighbors(variables: List[Var]) -> Dict[Var, set]:
    neighbors = {v:set() for v in variables}
    for i, v in enumerate(variables):
        c,s,t,k = v
        for j in range(i+1, len(variables)):
            u = variables[j]
            c2,s2,t2,k2 = u
            neighbors[v].add(u)
            neighbors[u].add(v)
    return neighbors

def consistent_factory(ctx):
    def consistent(v, val, u, uval):
        (slot_id, room_id) = val
        (slot2_id, room2_id) = uval
        if slot_id != slot2_id:
            return True
        c,s,t,k = v
        c2,s2,t2,k2 = u
        if t == t2:
            return False
        if c == c2:
            return False
        if room_id == room2_id:
            return False
        return True
    return consistent
