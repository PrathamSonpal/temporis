from fastapi import APIRouter
from sqlmodel import delete, select
try:
    from ..db import get_session
    from ..models import Assignment
    from ..solver.csp import CSP
    from ..solver.build_problem import load_context, build_variables, build_domains, build_neighbors, consistent_factory
except ImportError:
    from db import get_session
    from models import Assignment
    from solver.csp import CSP
    from solver.build_problem import load_context, build_variables, build_domains, build_neighbors, consistent_factory

router = APIRouter(prefix="/solve", tags=["solve"])

@router.post("")
def solve():
    ctx = load_context()
    variables = build_variables(ctx)
    domains = build_domains(ctx)
    neighbors = build_neighbors(variables)
    consistent = consistent_factory(ctx)

    csp = CSP(variables, domains, neighbors, consistent)
    assignment = csp.backtrack()
    status = "feasible" if assignment else "infeasible"

    saved = 0
    if assignment:
        with get_session() as s:
            s.exec(delete(Assignment))
            s.commit()
            for v, val in assignment.items():
                (slot_id, room_id) = val
                c_id, s_id, t_id, k = v
                a = Assignment(class_id=c_id, subject_id=s_id, teacher_id=t_id, room_id=room_id, timeslot_id=slot_id)
                s.add(a)
            s.commit()
            saved = len(s.exec(select(Assignment)).all())

    return {"status": status, "saved": saved, "variables": len(variables)}
