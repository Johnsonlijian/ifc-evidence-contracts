"""E3: tightness of interval evaluation for the evidence-contract fragment.

Claims:
  T1: For AND/OR formulas of coordinatewise nondecreasing atoms under a common source ordering, Kleene interval evaluation with
      per-atom A-/A+ equals the exact min/max over all joint completions,
      even when several atoms share one source.
  T2: For general formulas (with NOT), interval evaluation is a sound outer
      bound: [exact_min, exact_max] ⊆ [eval_lo, eval_hi].
  T3: Counterexample of looseness: f = (p=X) AND (p!=X) with p masked gives
      eval = pending although every completion yields fail.

Run: deterministic, no external deps.
"""
import itertools
import json
import sys

# ---------- three-valued Kleene helpers ----------
# Values: 0 = fail, 1 = pass, None = pending
def k_and(a, b):
    if a == 0 or b == 0:
        return 0
    if a == 1 and b == 1:
        return 1
    return None

def k_or(a, b):
    if a == 1 or b == 1:
        return 1
    if a == 0 and b == 0:
        return 0
    return None

def k_not(a):
    if a is None:
        return None
    return 1 - a

def k_eval(expr, atom_lo, atom_hi):
    """Interval (Kleene) evaluation. expr is a tuple AST:
    ('and', l, r) | ('or', l, r) | ('not', x) | ('atom', i)
    atom_lo[i] / atom_hi[i] are the per-atom min/max truth values."""
    def ev(e):
        tag = e[0]
        if tag == "atom":
            return atom_lo[e[1]], atom_hi[e[1]]
        if tag == "not":
            x = ev(e[1])
            # NOT reverses the interval ends
            nl = k_not(x[1]); nh = k_not(x[0])
            return nl, nh
        l = ev(e[1]); r = ev(e[2])
        if tag == "and":
            return k_and(l[0], r[0]), k_and(l[1], r[1])
        if tag == "or":
            return k_or(l[0], r[0]), k_or(l[1], r[1])
        raise ValueError(tag)
    return ev(expr)

def exact_eval(expr, atom_values):
    """Evaluate expr given concrete atom truth values."""
    tag = expr[0]
    if tag == "atom":
        return atom_values[expr[1]]
    if tag == "not":
        return k_not(exact_eval(expr[1], atom_values))
    if tag == "and":
        return k_and(exact_eval(expr[1], atom_values), exact_eval(expr[2], atom_values))
    if tag == "or":
        return k_or(exact_eval(expr[1], atom_values), exact_eval(expr[2], atom_values))
    raise ValueError(tag)

# ---------- atom/source model ----------
# Each atom i is a Boolean function of the sources it depends on.
# atom_fn = {i: (sources_tuple, fn)} where fn(values_tuple) -> 0/1.
# Monotone atoms: fn nondecreasing in each source value (domains ordered).

def atom_bounds(sources, atom_fn, masks, domains):
    """Per-atom min/max over the joint domain of its own sources (all masked
    sources vary; unmasked are fixed). This mirrors per-atom A-/A+ computed
    independently per source set, then combined by Kleene logic."""
    lo = {}; hi = {}
    for i, (srcs, fn) in atom_fn.items():
        vals = []
        for combo in itertools.product(*[domains[s] if s in masks else (sources[s],)
                                        for s in srcs]):
            d = dict(zip(srcs, combo))
            vals.append(fn(tuple(d[s] for s in srcs)))
        lo[i] = min(vals); hi[i] = max(vals)
    return lo, hi

def joint_bounds(sources, masks, domains, expr, atom_fn):
    """Exact min/max of formula value over joint completions of masked sources."""
    masked = sorted(masks)
    saw0 = False; saw1 = False
    for combo in itertools.product(*[domains[s] for s in masked]):
        src = dict(sources)
        for s, v in zip(masked, combo):
            src[s] = v
        atom_values = {}
        for i, (ss, fn) in atom_fn.items():
            atom_values[i] = fn(tuple(src[s] for s in ss))
        v = exact_eval(expr, atom_values)
        if v == 0:
            saw0 = True
        elif v == 1:
            saw1 = True
    if not saw0 and not saw1:
        return None, None
    mn = 0 if saw0 else 1
    mx = 1 if saw1 else 0
    return mn, mx

def run():
    domains = {0: (0, 1), 1: (0, 1, 2)}
    results = {"monotone_exact_ok": True, "sound_ok": True, "counterexamples": []}
    tests = 0
    loose_examples = []

    # Build a small formula family generator
    def gen_formulas(n_atoms, depth):
        atoms = [("atom", i) for i in range(n_atoms)]
        if depth == 0:
            return atoms
        sub = gen_formulas(n_atoms, depth - 1)
        out = []
        for a in atoms:
            out.append(a)
        for x in sub:
            for y in sub:
                out.append(("and", x, y))
                out.append(("or", x, y))
                out.append(("not", x))
        return out

    formulas = gen_formulas(3, 2)

    # Atom functions: shared-source atoms, monotone and non-monotone.
    # atom0: s0 == 1          (monotone in {0,1}; for domain {0,1,2}: value==1)
    # atom1: s0 >= 1          (monotone)
    # atom2: s1 == 2          (monotone w.r.t. ordered domain)
    # atom3: s1 != 1          (non-monotone)
    # atom4: s0 == 0          (non-monotone)
    atom_fns = {
        0: ((0,), lambda v: 1 if v[0] == 1 else 0),
        1: ((0,), lambda v: 1 if v[0] >= 1 else 0),
        2: ((1,), lambda v: 1 if v[0] == 2 else 0),
        3: ((1,), lambda v: 1 if v[0] != 1 else 0),
        4: ((0,), lambda v: 1 if v[0] == 0 else 0),
    }
    # subset of monotone atoms: 0,1,2
    monotone_atom_ids = {0, 1, 2}

    for n_sources in (1, 2):
        for n_atoms in range(2, 5):
            atoms_used = list(range(n_atoms))
            if n_sources == 1:
                atoms_used = [0, 1, 4][:n_atoms]
            else:
                atoms_used = [0, 1, 2, 3][:n_atoms]
            fs = gen_formulas(len(atoms_used), 1)
            for expr in fs:
                used = _atoms_in(expr)
                if not used:
                    continue
                fn = {i: atom_fns[atoms_used[i]] for i in used}
                for masks in _mask_sets(set(range(n_sources)), max(1, n_sources)):
                    for vals in itertools.product(*[domains[s] for s in range(n_sources)]):
                        sources = {s: vals[s] for s in range(n_sources)}
                        lo, hi = atom_bounds(sources, fn, masks, domains)
                        ev = k_eval(expr, lo, hi)
                        mn, mx = joint_bounds(sources, masks, domains, expr, fn)
                        tests += 1
                        is_mono = _is_monotone(expr, {i: atoms_used[i] for i in used}, monotone_atom_ids)
                        if is_mono:
                            # T1: exact equality
                            ok = (ev[0] == mn and ev[1] == mx)
                            if not ok:
                                results["monotone_exact_ok"] = False
                                results["counterexamples"].append(
                                    {"expr": repr(expr), "masks": sorted(masks),
                                     "sources": sources, "interval": ev, "exact": (mn, mx)})
                        # T2: soundness
                        sound = _interval_contains(ev, mn, mx)
                        if not sound:
                            results["sound_ok"] = False
                            results["counterexamples"].append(
                                {"kind": "unsound", "expr": repr(expr),
                                 "interval": ev, "exact": (mn, mx)})
                        if not is_mono and ev[0] is not None and ev[1] is not None \
                                and (mn is not None and mx is not None) \
                                and not (ev[0] == mn and ev[1] == mx):
                            loose_examples.append({"expr": repr(expr), "masks": sorted(masks),
                                                   "sources": sources,
                                                   "interval": ev, "exact": (mn, mx)})

    # T3 concrete counterexample: f = (s0==1) AND (s0!=1), s0 masked
    expr_t3 = ("and", ("atom", 0), ("not", ("atom", 0)))
    fn_t3 = {0: atom_fns[0], 1: atom_fns[3]}  # atom1 = s0!=1 for shared-source mixed polarity
    # rebuild with atom 1 meaning s0 != 1
    fn_t3 = {0: ((0,), lambda v: 1 if v[0] == 1 else 0),
             1: ((0,), lambda v: 1 if v[0] != 1 else 0)}
    expr_t3b = ("and", ("atom", 0), ("atom", 1))
    lo, hi = atom_bounds({0: 0}, fn_t3, {0}, domains)
    ev = k_eval(expr_t3b, lo, hi)
    mn, mx = joint_bounds({0: 0}, {0}, domains, expr_t3b, fn_t3)
    t3 = {"expr": "f = (p==X) AND (p!=X), p masked",
          "interval_eval": ev, "exact": (mn, mx),
          "loose": not (ev[0] == mn and ev[1] == mx)}

    summary = {
        "tests": tests,
        "monotone_exact_ok": results["monotone_exact_ok"],
        "sound_ok": results["sound_ok"],
        "counterexamples": results["counterexamples"][:5],
        "loose_examples_count": len(loose_examples),
        "loose_examples": loose_examples[:5],
        "T3_explicit": t3,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    ok = results["monotone_exact_ok"] and results["sound_ok"] and t3["loose"]
    print("VERDICT:", "PASS (T1 exact for monotone, T2 sound, T3 loose counterexample exists)" if ok
          else "CHECK NEEDED")
    return 0 if ok else 1

def _atoms_in(expr):
    s = set()
    def rec(e):
        if e[0] == "atom":
            s.add(e[1])
        elif e[0] == "not":
            rec(e[1])
        else:
            rec(e[1]); rec(e[2])
    rec(expr)
    return s

def _mask_sets(sources, n):
    s = sorted(sources)
    out = []
    for r in range(1, len(s) + 1):
        for c in itertools.combinations(s, r):
            out.append(set(c))
    return out

def _is_monotone(expr, atom_map, monotone_ids):
    """True if every atom maps to a monotone atom fn and formula has no NOT."""
    def rec(e):
        if e[0] == "atom":
            return atom_map[e[1]] in monotone_ids
        if e[0] == "not":
            return False
        return rec(e[1]) and rec(e[2])
    return rec(expr)

def _interval_contains(ev, mn, mx):
    if mn is None:
        return True  # no determinate completions: any interval contains
    if ev[0] is None or ev[1] is None:
        return True  # interval = full [0,1]
    return ev[0] <= mn and ev[1] >= mx

if __name__ == "__main__":
    sys.exit(run())
