from collections import defaultdict

class CSP:
    def __init__(self, variables, domains, neighbors, consistent):
        self.variables = list(variables)
        self.domains = {v: list(domains[v]) for v in self.variables}
        self.neighbors = neighbors
        self.consistent = consistent
        self.assignment = {}

    def mrv(self):
        unassigned = [v for v in self.variables if v not in self.assignment]
        return min(unassigned, key=lambda v: len(self.domains[v]))

    def lcv(self, v):
        def conflicts(val):
            c = 0
            for u in self.neighbors[v]:
                if u in self.assignment:
                    if not self.consistent(v, val, u, self.assignment[u]):
                        c += 1
                    continue
                for uval in self.domains[u]:
                    if not self.consistent(v, val, u, uval):
                        c += 1
            return c
        return sorted(self.domains[v], key=conflicts)

    def forward_check(self, v, val, pruned):
        for u in self.neighbors[v]:
            if u in self.assignment: 
                continue
            to_remove = [uval for uval in list(self.domains[u]) if not self.consistent(v, val, u, uval)]
            if to_remove:
                for r in to_remove:
                    self.domains[u].remove(r)
                pruned[u].extend(to_remove)
                if not self.domains[u]:
                    return False
        return True

    def backtrack(self):
        if len(self.assignment) == len(self.variables):
            return dict(self.assignment)
        v = self.mrv()
        for val in self.lcv(v):
            ok = True
            for u, uval in self.assignment.items():
                if not self.consistent(v, val, u, uval):
                    ok = False; break
            if not ok:
                continue
            self.assignment[v] = val
            pruned = defaultdict(list)
            if self.forward_check(v, val, pruned):
                res = self.backtrack()
                if res:
                    return res
            del self.assignment[v]
            for u, vals in pruned.items():
                self.domains[u].extend(vals)
        return None
