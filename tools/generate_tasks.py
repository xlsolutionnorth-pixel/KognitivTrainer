#!/usr/bin/env python3
"""Erzeugt www/tasks.js mit genau 500 Aufgaben für den KognitivTrainer.

Aufruf:  python3 tools/generate_tasks.py
Der Zufall ist fest eingestellt (seed), daher entstehen bei jedem Aufruf dieselben Aufgaben.

Aufbau einer Aufgabe:
  id     eindeutige Nummer (1..500)
  cat    rechnen | geometrie | gedaechtnis | reaktion
  type   mc (Multiple Choice) oder ein interaktiver Typ (span, stroop, schulte …)
  lvl    1 = leicht, 2 = mittel, 3 = schwer
  title  kurzer Name
  q      Fragetext (bei mc)
  opts   Antwortmöglichkeiten (bei mc), ans = Index der richtigen
  expl   Erklärung der Lösung
  p      Parameter für interaktive Typen
"""
import json, math, os, random
from fractions import Fraction

R = random.Random(20261118)
TASKS = []
SEEN = set()


def fmt(x):
    """Zahl deutsch formatieren (Komma statt Punkt, ohne unnötige Nullen)."""
    if isinstance(x, Fraction):
        if x.denominator == 1:
            return str(x.numerator)
        return f"{x.numerator}/{x.denominator}"
    if isinstance(x, float):
        if abs(x - round(x)) < 1e-9:
            return str(int(round(x)))
        s = f"{x:.2f}".rstrip("0").rstrip(".")
        return s.replace(".", ",")
    return str(x)


def num_opts(ans, spread=None, n=4, allow_neg=False, integer=True):
    """Antwortmöglichkeiten um die richtige Zahl herum."""
    if spread is None:
        spread = max(2, int(abs(ans) * 0.15) if integer else abs(ans) * 0.15)
    cand = set()
    tries = 0
    while len(cand) < n - 1 and tries < 500:
        tries += 1
        if integer:
            d = R.choice([-1, 1]) * R.randint(1, max(1, int(spread)))
            # typische Denkfehler zusätzlich: ±10, ±1
            if R.random() < 0.25:
                d = R.choice([-10, 10, -1, 1, -2, 2])
            v = ans + d
        else:
            v = round(ans + R.choice([-1, 1]) * R.uniform(0.1, 1) * spread, 2)
        if v == ans or (not allow_neg and v < 0):
            continue
        cand.add(v)
    opts = list(cand) + [ans]
    R.shuffle(opts)
    return [fmt(o) for o in opts], opts.index(ans)


def text_opts(correct, wrong):
    opts = [correct] + list(wrong)
    R.shuffle(opts)
    return opts, opts.index(correct)


def add_mc(cat, lvl, title, q, opts, ans, expl, extra=None):
    key = (cat, q)
    if key in SEEN:
        return False
    if len(set(opts)) != len(opts):
        return False
    SEEN.add(key)
    t = {"cat": cat, "type": "mc", "lvl": lvl, "title": title, "q": q,
         "opts": opts, "ans": ans, "expl": expl}
    if extra:
        t.update(extra)
    TASKS.append(t)
    return True


def add_inter(cat, typ, lvl, title, q, p, expl):
    key = (cat, typ, json.dumps(p, sort_keys=True))
    if key in SEEN:
        return False
    SEEN.add(key)
    TASKS.append({"cat": cat, "type": typ, "lvl": lvl, "title": title,
                  "q": q, "p": p, "expl": expl})
    return True


def count(cat, title=None):
    return sum(1 for t in TASKS if t["cat"] == cat and (title is None or t["title"] == title))


def fill(target, fn):
    """Ruft fn so lange auf, bis target Aufgaben der Art dazugekommen sind."""
    start = len(TASKS)
    guard = 0
    while len(TASKS) - start < target:
        guard += 1
        assert guard < 20000, f"Generator hängt: {fn.__name__}"
        fn()


def lvl_for(i, n):
    return 1 if i < n / 3 else (2 if i < 2 * n / 3 else 3)

# ---------------------------------------------------------------------------
# A. RECHNEN & LOGIK (160)
# ---------------------------------------------------------------------------
C = "rechnen"


def kopfrechnen(n=40):
    for i in range(n):
        lvl = lvl_for(i, n)
        while True:
            op = R.choice("+-×÷")
            if lvl == 1:
                a, b = R.randint(12, 99), R.randint(5, 60)
                if op in "×÷":
                    a, b = R.randint(3, 12), R.randint(3, 12)
            elif lvl == 2:
                a, b = R.randint(120, 999), R.randint(45, 499)
                if op in "×÷":
                    a, b = R.randint(12, 39), R.randint(4, 15)
            else:
                a, b = R.randint(1200, 9999), R.randint(450, 4999)
                if op in "×÷":
                    a, b = R.randint(24, 99), R.randint(12, 49)
            if op == "+":
                r, ex = a + b, f"{a} + {b} = {a+b}. Tipp: erst die Zehner/Hunderter, dann die Einer addieren."
            elif op == "-":
                if b > a:
                    a, b = b, a
                r, ex = a - b, f"{a} − {b} = {a-b}. Tipp: auf den nächsten runden Wert ergänzen und dann weiterzählen."
            elif op == "×":
                r = a * b
                ex = f"{a} × {b} = {r}. Zerlegen hilft: {a} × {b} = {a} × {b//10*10} + {a} × {b%10}." if b >= 10 else f"{a} × {b} = {r}."
            else:
                r = a
                a = a * b
                ex = f"{a} ÷ {b} = {r}, denn {r} × {b} = {a}."
            sym = {"+": "+", "-": "−", "×": "×", "÷": "÷"}[op]
            q = f"Berechne im Kopf: {a} {sym} {b} = ?"
            o, k = num_opts(r)
            if add_mc(C, lvl, "Kopfrechnen", q, o, k, ex):
                break


def prozent(n=15):
    for i in range(n):
        lvl = lvl_for(i, n)
        while True:
            if lvl == 1:
                p = R.choice([10, 20, 25, 50, 5])
                g = R.choice(range(40, 401, 20))
            elif lvl == 2:
                p = R.choice([15, 30, 35, 40, 60, 75, 12])
                g = R.choice(range(60, 801, 20))
            else:
                p = R.choice([7, 13, 17, 18, 22, 35, 45])
                g = R.choice(range(100, 1001, 50))
            w = g * p / 100
            if abs(w - round(w)) > 1e-9 and lvl < 3:
                continue
            kind = R.choice(["wert", "rabatt"]) if lvl > 1 else "wert"
            if kind == "wert":
                q = f"Wie viel sind {p} % von {g}?"
                ans = w
                ex = f"{p} % von {g} = {g} × {p} ÷ 100 = {fmt(w)}. Tipp: 10 % ist {fmt(g/10)}, davon ausgehend hochrechnen."
            else:
                q = f"Ein Artikel kostet {g} €. Er wird um {p} % reduziert. Wie viel kostet er jetzt (in €)?"
                ans = g - w
                ex = f"Rabatt: {p} % von {g} € = {fmt(w)} €. Neuer Preis: {g} − {fmt(w)} = {fmt(ans)} €."
            integer = abs(ans - round(ans)) < 1e-9
            o, k = num_opts(int(round(ans)) if integer else ans, integer=integer)
            if add_mc(C, lvl, "Prozent", q, o, k, ex):
                break


def brueche(n=10):
    for i in range(n):
        lvl = lvl_for(i, n)
        while True:
            d1, d2 = R.choice([2, 3, 4, 5, 6, 8]), R.choice([2, 3, 4, 5, 6, 8, 10, 12])
            a, b = Fraction(R.randint(1, d1 - 1), d1), Fraction(R.randint(1, d2 - 1), d2)
            op = "+" if lvl == 1 else R.choice("+−×")
            if op == "+":
                r = a + b
            elif op == "−":
                if b > a:
                    a, b = b, a
                r = a - b
                if r == 0:
                    continue
            else:
                r = a * b
            wrong = set()
            # typische Fehler: Zähler+Zähler / Nenner+Nenner usw.
            wrong.add(Fraction(a.numerator + b.numerator, a.denominator + b.denominator))
            while len(wrong) < 6:
                wrong.add(r + Fraction(R.choice([-1, 1]) * R.randint(1, 3), r.denominator * R.choice([1, 2])))
            wrong = [w for w in wrong if w != r and w > 0][:3]
            if len(wrong) < 3:
                continue
            opts, k = text_opts(fmt(r), [fmt(w) for w in wrong])
            if op == "×":
                ex = f"Zähler mal Zähler, Nenner mal Nenner: {fmt(a)} × {fmt(b)} = {a.numerator*b.numerator}/{a.denominator*b.denominator} = {fmt(r)} (gekürzt)."
            else:
                L = a.denominator * b.denominator // math.gcd(a.denominator, b.denominator)
                ex = (f"Auf den gemeinsamen Nenner {L} bringen: {a.numerator*L//a.denominator}/{L} {op} "
                      f"{b.numerator*L//b.denominator}/{L} = {fmt(r)} (gekürzt).")
            if add_mc(C, lvl, "Brüche", f"Berechne: {fmt(a)} {op} {fmt(b)} = ?", opts, k, ex):
                break


def gleichungen(n=15):
    for i in range(n):
        lvl = lvl_for(i, n)
        while True:
            x = R.randint(2, 15) if lvl < 3 else R.randint(-9, 20)
            if lvl == 1:
                a, b = R.randint(2, 9), R.randint(1, 30)
                q = f"Löse nach x auf: {a}x + {b} = {a*x+b}"
                ex = f"{a}x = {a*x+b} − {b} = {a*x}  →  x = {a*x} ÷ {a} = {x}."
            elif lvl == 2:
                a, b, c = R.randint(2, 9), R.randint(1, 20), R.randint(2, 5)
                q = f"Löse nach x auf: {c}·(x + {b}) = {c*(x+b)}"
                ex = f"Durch {c} teilen: x + {b} = {x+b}  →  x = {x}."
            else:
                a, c = R.randint(3, 9), R.randint(1, 2)
                if a == c:
                    continue
                b, d = R.randint(1, 20), None
                d = a * x + b - c * x
                q = f"Löse nach x auf: {a}x + {b} = {c}x + {d}"
                ex = f"{a}x − {c}x = {d} − {b}  →  {a-c}x = {d-b}  →  x = {x}."
            o, k = num_opts(x, spread=4, allow_neg=True)
            if add_mc(C, lvl, "Gleichung", q, o, k, ex):
                break


def zahlenreihen(n=35):
    def gen(lvl):
        kind = R.choice({1: ["arith", "arith", "geo", "quad"],
                         2: ["diff", "alt", "geo", "fib", "quad", "mul_add"],
                         3: ["mul_add", "two", "cube", "fib", "diff2", "prime_like"]}[lvl])
        if kind == "arith":
            s, d = R.randint(1, 40), R.choice([3, 4, 5, 6, 7, 8, 9, 11, -3, -4])
            seq = [s + d * i for i in range(6)]
            if min(seq) < 0:
                return None
            ex = f"Es kommt jedes Mal {d} {'dazu' if d > 0 else 'weg'}."
        elif kind == "geo":
            s, f = R.randint(1, 5), R.choice([2, 3])
            seq = [s * f ** i for i in range(6)]
            ex = f"Jede Zahl wird mit {f} multipliziert."
        elif kind == "quad":
            o = R.randint(1, 6)
            seq = [(o + i) ** 2 for i in range(6)]
            ex = f"Quadratzahlen: {o}², {o+1}², {o+2}² …"
        elif kind == "diff":
            s, d0 = R.randint(1, 20), R.randint(1, 4)
            seq = [s]
            for i in range(5):
                seq.append(seq[-1] + d0 + i)
            ex = f"Der Abstand wächst jedes Mal um 1: +{d0}, +{d0+1}, +{d0+2} …"
        elif kind == "diff2":
            s, d0, k = R.randint(1, 10), R.randint(1, 3), R.randint(2, 3)
            seq = [s]
            d = d0
            for i in range(5):
                seq.append(seq[-1] + d)
                d *= k
            ex = f"Die Abstände werden jedes Mal mit {k} multipliziert: +{d0}, +{d0*k}, +{d0*k*k} …"
        elif kind == "alt":
            s, a, b = R.randint(5, 30), R.randint(2, 9), R.randint(1, 5)
            seq = [s]
            for i in range(5):
                seq.append(seq[-1] + (a if i % 2 == 0 else -b))
            ex = f"Abwechselnd +{a} und −{b}."
        elif kind == "fib":
            a, b = R.randint(1, 5), R.randint(1, 6)
            seq = [a, b]
            for i in range(4):
                seq.append(seq[-1] + seq[-2])
            ex = "Jede Zahl ist die Summe der beiden vorherigen."
        elif kind == "mul_add":
            s, m, a = R.randint(1, 4), 2, R.choice([1, 2, -1, 3])
            seq = [s]
            for i in range(5):
                seq.append(seq[-1] * m + a)
            if min(seq) < 0:
                return None
            ex = f"Jede Zahl mal {m}, dann {'+' if a > 0 else '−'}{abs(a)}."
        elif kind == "two":
            a, da, b, db = R.randint(1, 10), R.randint(2, 5), R.randint(20, 40), R.choice([-2, -3, 3, 4])
            seq = []
            for i in range(6):
                seq.append(a + da * (i // 2) if i % 2 == 0 else b + db * (i // 2))
            ex = f"Zwei Reihen ineinander: an den Stellen 1, 3, 5 jeweils +{da}, an den Stellen 2, 4, 6 jeweils {'+' if db > 0 else '−'}{abs(db)}."
        elif kind == "cube":
            o = R.randint(1, 4)
            seq = [(o + i) ** 3 for i in range(6)]
            ex = f"Kubikzahlen: {o}³, {o+1}³, {o+2}³ …"
        else:  # prime_like
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
            o = R.randint(0, 8)
            seq = primes[o:o + 6]
            ex = "Primzahlen – Zahlen, die nur durch 1 und sich selbst teilbar sind."
        return seq, ex

    for i in range(n):
        lvl = lvl_for(i, n)
        while True:
            g = gen(lvl)
            if not g:
                continue
            seq, ex = g
            ans = seq[-1]
            o, k = num_opts(ans, spread=max(3, abs(seq[-1] - seq[-2]) // 2 + 2))
            shown = ", ".join(str(v) for v in seq[:-1])
            if add_mc(C, lvl, "Zahlenreihe", f"Wie geht die Reihe weiter?  {shown}, ?", o, k,
                      ex + f" Die nächste Zahl ist {ans}."):
                break


NAMES = ["Anna", "Ben", "Clara", "David", "Emma", "Felix", "Greta", "Hannes", "Ida", "Jonas",
         "Kira", "Leon", "Mia", "Noah", "Olga", "Paul", "Rita", "Sami", "Tina", "Udo"]
WESEN = ["Blipse", "Kronks", "Zirbel", "Mumpfe", "Flonzen", "Gribbel", "Tranks", "Quesel",
         "Wurpen", "Snoffel", "Plunzen", "Drakel"]
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def logik(n=25):
    def syllogismus():
        x, y, z = R.sample(WESEN, 3)
        form = R.randint(0, 3)
        if form == 0:
            return (2, f"Alle {x} sind {y}. Alle {y} sind {z}. Folgt daraus: Alle {x} sind {z}?",
                    "Ja", f"Wenn alle {x} zu den {y} gehören und alle {y} zu den {z}, dann gehören auch alle {x} zu den {z} (Kettenschluss).")
        if form == 1:
            return (3, f"Alle {x} sind {y}. Einige {y} sind {z}. Folgt daraus sicher: Einige {x} sind {z}?",
                    "Nicht bestimmbar", f"Die {y}, die {z} sind, könnten ganz andere als die {x} sein. Es folgt also nichts Sicheres.")
        if form == 2:
            return (2, f"Keine {x} sind {y}. Alle {z} sind {y}. Folgt daraus: Keine {z} sind {x}?",
                    "Ja", f"Alle {z} gehören zu den {y}, und keine {x} gehören dazu – also können keine {z} {x} sein.")
        return (3, f"Einige {x} sind {y}. Einige {y} sind {z}. Folgt daraus sicher: Einige {x} sind {z}?",
                "Nicht bestimmbar", "Zwei „einige“-Aussagen lassen keinen sicheren Schluss zu – die Gruppen müssen sich nicht überschneiden.")

    def reihenfolge():
        ppl = R.sample(NAMES, 4 if R.random() < 0.5 else 3)
        order = ppl[:]  # größte zuerst
        adj = R.choice([("größer", "am kleinsten", "am größten"), ("schneller", "am langsamsten", "am schnellsten"),
                        ("älter", "am jüngsten", "am ältesten")])
        facts = [f"{order[i]} ist {adj[0]} als {order[i+1]}." for i in range(len(order) - 1)]
        R.shuffle(facts)
        ask_small = R.random() < 0.5
        corr = order[-1] if ask_small else order[0]
        q = " ".join(facts) + f" Wer ist {adj[1] if ask_small else adj[2]}?"
        lv = 1 if len(ppl) == 3 else 2
        return (lv, q, corr, "Ordnet man alle: " + " > ".join(order) + f". Also ist {corr} {adj[1] if ask_small else adj[2]}.", ppl)

    def alter():
        k = R.randint(2, 5)
        a = R.randint(4, 15)
        s = a * (k + 1)
        p1, p2 = R.sample(NAMES, 2)
        q = f"{p1} ist {k}-mal so alt wie {p2}. Zusammen sind beide {s} Jahre alt. Wie alt ist {p2}?"
        return (2, q, a, f"{p2} = x, {p1} = {k}x. Zusammen {k+1}x = {s}  →  x = {a}.")

    def wochentag():
        t = R.randrange(7)
        d = R.randint(9, 60)
        q = f"Heute ist {TAGE[t]}. Welcher Wochentag ist in {d} Tagen?"
        r = TAGE[(t + d) % 7]
        return (2 if d < 30 else 3, q, r, f"{d} Tage = {d//7} volle Wochen + {d%7} Tage. {TAGE[t]} + {d%7} Tage = {r}.", "tage")

    def uhrzeit():
        h, m = R.randint(6, 20), R.choice(range(0, 60, 5))
        dh, dm = R.randint(1, 4), R.choice(range(5, 60, 5))
        tot = (h * 60 + m + dh * 60 + dm) % (24 * 60)
        q = f"Es ist {h}:{m:02d} Uhr. Wie spät ist es in {dh} Stunden und {dm} Minuten?"
        r = f"{tot//60}:{tot%60:02d}"
        wrong = set()
        while len(wrong) < 3:
            w = (tot + R.choice([-60, 60, -10, 10, -5, 5, 30, -30])) % 1440
            if w != tot:
                wrong.add(f"{w//60}:{w%60:02d}")
        return (1, q, r, f"{h}:{m:02d} + {dh} h = {h+dh}:{m:02d}, dann + {dm} min = {r} Uhr.", list(wrong))

    gens = [syllogismus, reihenfolge, alter, wochentag, uhrzeit]
    made = 0
    guard = 0
    while made < n:
        guard += 1
        g = gens[made % len(gens)]()
        lv, q, corr = g[0], g[1], g[2]
        ex = g[3]
        if g is None:
            continue
        if isinstance(corr, int):
            o, k = num_opts(corr, spread=4)
        elif corr in ("Ja", "Nein", "Nicht bestimmbar"):
            o, k = text_opts(corr, [x for x in ("Ja", "Nein", "Nicht bestimmbar") if x != corr])
        elif len(g) > 4 and g[4] == "tage":
            o, k = text_opts(corr, R.sample([t for t in TAGE if t != corr], 3))
        elif len(g) > 4 and isinstance(g[4], list) and corr in g[4]:
            o, k = text_opts(corr, [p for p in g[4] if p != corr][:3])
        else:
            o, k = text_opts(corr, g[4])
        if add_mc(C, lv, "Logik", q, o, k, ex):
            made += 1


def textaufgaben(n=20):
    def tempo():
        v, t = R.choice([40, 50, 60, 70, 80, 90, 100, 120]), R.choice([1.5, 2, 2.5, 3, 0.5, 0.75])
        s = v * t
        if s != int(s):
            return None
        return (1, f"Ein Auto fährt {v} km/h. Wie viele Kilometer schafft es in {fmt(t)} Stunden?", int(s),
                f"Strecke = Geschwindigkeit × Zeit = {v} × {fmt(t)} = {int(s)} km.")

    def preis():
        st, p = R.randint(3, 12), R.choice([0.45, 0.8, 1.2, 1.5, 2.5, 3.2, 0.65])
        tot = round(st * p, 2)
        return (1, f"Ein Brötchen kostet {fmt(p)} €. Was kosten {st} Brötchen (in €)?", tot,
                f"{st} × {fmt(p)} € = {fmt(tot)} €.")

    def arbeit():
        a, ta = R.choice([(2, 6), (3, 4), (4, 6), (3, 8), (6, 4), (5, 6)]), None
        w, d = a
        w2 = R.choice([x for x in (2, 3, 4, 6, 8, 12) if (w * d) % x == 0 and x != w])
        return (2, f"{w} Maler brauchen {d} Tage für ein Haus. Wie viele Tage brauchen {w2} Maler (gleiches Tempo)?",
                w * d // w2, f"Gesamtarbeit = {w} × {d} = {w*d} Maler-Tage. Mit {w2} Malern: {w*d} ÷ {w2} = {w*d//w2} Tage.")

    def zins():
        k, p = R.choice([500, 1000, 2000, 1500, 800, 2500]), R.choice([2, 3, 4, 5])
        j = R.choice([1, 2])
        if j == 1:
            return (2, f"Du legst {k} € zu {p} % Zinsen für 1 Jahr an. Wie viel Zinsen bekommst du (in €)?",
                    k * p // 100, f"{p} % von {k} € = {k*p//100} €.")
        tot = round(k * (1 + p / 100) ** 2, 2)
        return (3, f"Du legst {k} € zu {p} % Zinsen an, Zinsen werden mitverzinst. Wie viel Geld hast du nach 2 Jahren (in €)?",
                tot, f"{k} × 1,0{p} × 1,0{p} = {fmt(tot)} €. Im 2. Jahr gibt es auch Zinsen auf die Zinsen.")

    def mischung():
        a, b = R.randint(2, 9), R.randint(2, 9)
        pa, pb = R.choice([2, 3, 4, 5]), R.choice([6, 8, 10, 12])
        tot = a * pa + b * pb
        return (2, f"Du kaufst {a} Hefte zu je {pa} € und {b} Bücher zu je {pb} €. Wie viel zahlst du insgesamt (in €)?",
                tot, f"{a} × {pa} + {b} × {pb} = {a*pa} + {b*pb} = {tot} €.")

    def treffen():
        v1, v2 = R.choice([40, 50, 60, 80]), R.choice([20, 30, 40, 60, 70])
        s = (v1 + v2) * R.choice([1, 2, 3])
        t = s // (v1 + v2)
        return (3, f"Zwei Züge fahren sich auf {s} km Strecke entgegen, mit {v1} km/h und {v2} km/h. Nach wie vielen Stunden treffen sie sich?",
                t, f"Sie nähern sich mit {v1}+{v2} = {v1+v2} km/h. {s} ÷ {v1+v2} = {t} Stunden.")

    gens = [tempo, preis, arbeit, zins, mischung, treffen]
    made = 0
    while made < n:
        g = gens[made % len(gens)]()
        if not g:
            continue
        lv, q, a, ex = g
        integer = abs(a - round(a)) < 1e-9
        o, k = num_opts(int(round(a)) if integer else a, integer=integer)
        if add_mc(C, lv, "Textaufgabe", q, o, k, ex):
            made += 1

# ---------------------------------------------------------------------------
# B. GEOMETRIE & RÄUMLICH (120)
# ---------------------------------------------------------------------------
G = "geometrie"


def flaechen(n=30):
    def rechteck():
        a, b = R.randint(3, 25), R.randint(2, 18)
        if R.random() < 0.5:
            return 1, f"Ein Rechteck ist {a} cm lang und {b} cm breit. Wie groß ist seine Fläche (cm²)?", a * b, f"Fläche = Länge × Breite = {a} × {b} = {a*b} cm².", {"shape": "rect", "a": a, "b": b}
        return 1, f"Ein Rechteck ist {a} cm lang und {b} cm breit. Wie groß ist sein Umfang (cm)?", 2 * (a + b), f"Umfang = 2 × (Länge + Breite) = 2 × ({a} + {b}) = {2*(a+b)} cm.", {"shape": "rect", "a": a, "b": b}

    def dreieck():
        g, h = R.randint(4, 20) * 2, R.randint(3, 15)
        return 2, f"Ein Dreieck hat die Grundseite {g} cm und die Höhe {h} cm. Wie groß ist die Fläche (cm²)?", g * h // 2, f"Fläche = Grundseite × Höhe ÷ 2 = {g} × {h} ÷ 2 = {g*h//2} cm².", {"shape": "tri", "g": g, "h": h}

    def kreis():
        r = R.randint(2, 12)
        if R.random() < 0.5:
            A = round(math.pi * r * r, 1)
            return 3, f"Ein Kreis hat den Radius {r} cm. Wie groß ist seine Fläche ungefähr (cm², π ≈ 3,14)?", A, f"Fläche = π × r² = 3,14 × {r}² = 3,14 × {r*r} ≈ {fmt(A)} cm².", {"shape": "circle", "r": r}
        U = round(2 * math.pi * r, 1)
        return 3, f"Ein Kreis hat den Radius {r} cm. Wie groß ist sein Umfang ungefähr (cm, π ≈ 3,14)?", U, f"Umfang = 2 × π × r = 2 × 3,14 × {r} ≈ {fmt(U)} cm.", {"shape": "circle", "r": r}

    def trapez():
        a, c, h = R.randint(6, 20), R.randint(2, 10), R.randint(2, 10)
        if (a + c) * h % 2:
            return None
        return 3, f"Ein Trapez hat die parallelen Seiten {a} cm und {c} cm, die Höhe ist {h} cm. Wie groß ist die Fläche (cm²)?", (a + c) * h // 2, f"Fläche = (a + c) ÷ 2 × h = ({a} + {c}) ÷ 2 × {h} = {(a+c)*h//2} cm².", None

    def quadrat_rueck():
        s = R.randint(3, 15)
        return 2, f"Ein Quadrat hat die Fläche {s*s} cm². Wie lang ist eine Seite (cm)?", s, f"Seite = √{s*s} = {s} cm, denn {s} × {s} = {s*s}.", {"shape": "rect", "a": s, "b": s, "hide": True, "area": s * s}

    gens = [rechteck, dreieck, quadrat_rueck, kreis, trapez]
    made = 0
    while made < n:
        g = gens[made % len(gens)]()
        if not g:
            continue
        lv, q, a, ex, fig = g
        integer = abs(a - round(a)) < 1e-9
        if integer:
            o, k = num_opts(int(round(a)))
        else:
            vals = {a}
            while len(vals) < 4:
                vals.add(round(a * R.choice([0.5, 0.75, 1.25, 2, 1.5, 0.9, 1.1]), 1))
            vals = list(vals)
            R.shuffle(vals)
            o, k = [fmt(v) for v in vals], vals.index(a)
        if add_mc(G, lv, "Fläche & Umfang", q, o, k, ex, {"fig": fig} if fig else None):
            made += 1


def winkel(n=20):
    made = 0
    while made < n:
        kind = made % 4
        if kind == 0:
            a, b = R.randint(20, 100), R.randint(20, 70)
            if a + b >= 170:
                continue
            c = 180 - a - b
            q, ans, ex, lv = (f"In einem Dreieck sind zwei Winkel {a}° und {b}°. Wie groß ist der dritte Winkel?", c,
                              f"Die Winkelsumme im Dreieck ist 180°: 180 − {a} − {b} = {c}°.", 1)
            fig = {"shape": "angles", "a": a, "b": b}
        elif kind == 1:
            h, m = R.randint(1, 12), R.choice(range(0, 60, 5))
            ang = abs(30 * h + 0.5 * m - 6 * m) % 360
            ang = min(ang, 360 - ang)
            if ang != int(ang):
                continue
            ang = int(ang)
            q, ans, ex, lv = (f"Welchen (kleineren) Winkel bilden die Uhrzeiger um {h}:{m:02d} Uhr?", ang,
                              f"Stundenzeiger: {h}×30° + {m}×0,5° = {fmt(30*h+0.5*m)}°. Minutenzeiger: {m}×6° = {6*m}°. Differenz (kleinere Seite) = {ang}°.", 3)
            fig = {"shape": "clock", "h": h, "m": m}
        elif kind == 2:
            k = R.choice([5, 6, 8, 9, 10, 12])
            q, ans, ex, lv = (f"Wie groß ist ein Innenwinkel in einem regelmäßigen {k}-Eck?", (k - 2) * 180 // k,
                              f"Winkelsumme = ({k} − 2) × 180° = {(k-2)*180}°. Geteilt durch {k} Ecken = {(k-2)*180//k}°.", 3)
            if (k - 2) * 180 % k:
                continue
            fig = {"shape": "poly", "k": k}
        else:
            a = R.randint(15, 165)
            if R.random() < 0.5:
                q, ans, ex, lv = (f"Zwei Winkel ergänzen sich zu einem gestreckten Winkel (180°). Einer ist {a}°. Wie groß ist der andere?", 180 - a,
                                  f"Nebenwinkel ergänzen sich zu 180°: 180 − {a} = {180-a}°.", 1)
            else:
                a = a % 85 + 5
                q, ans, ex, lv = (f"Zwei Winkel ergänzen sich zu einem rechten Winkel (90°). Einer ist {a}°. Wie groß ist der andere?", 90 - a,
                                  f"Sie ergänzen sich zu 90°: 90 − {a} = {90-a}°.", 2)
            fig = None
        o, k2 = num_opts(ans, spread=15)
        if add_mc(G, lv, "Winkel", q, o, k2, ex, {"fig": fig} if fig else None):
            made += 1


def pythagoras(n=12):
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (12, 16, 20), (7, 24, 25), (15, 20, 25), (10, 24, 26), (20, 21, 29), (9, 40, 41), (12, 35, 37)]
    R.shuffle(triples)
    for i, (a, b, c) in enumerate(triples[:n]):
        if i % 2 == 0:
            q = f"Ein rechtwinkliges Dreieck hat die Katheten {a} cm und {b} cm. Wie lang ist die Hypotenuse (cm)?"
            ans, ex = c, f"c² = a² + b² = {a*a} + {b*b} = {c*c}  →  c = √{c*c} = {c} cm."
        else:
            q = f"Ein rechtwinkliges Dreieck hat die Hypotenuse {c} cm und eine Kathete {a} cm. Wie lang ist die andere Kathete (cm)?"
            ans, ex = b, f"b² = c² − a² = {c*c} − {a*a} = {b*b}  →  b = {b} cm."
        o, k = num_opts(ans, spread=4)
        fig = {"shape": "right", "a": a, "b": b} if i % 2 == 0 else {"shape": "right", "a": a, "b": "?", "c": c}
        add_mc(G, 2 if c < 20 else 3, "Pythagoras", q, o, k, ex, {"fig": fig})


def koerper(n=13):
    made = 0
    while made < n:
        kind = made % 3
        if kind == 0:
            s = R.randint(2, 12)
            if R.random() < 0.5:
                q, a, ex, lv = f"Ein Würfel hat die Kantenlänge {s} cm. Wie groß ist sein Volumen (cm³)?", s ** 3, f"V = a³ = {s} × {s} × {s} = {s**3} cm³.", 2
            else:
                q, a, ex, lv = f"Ein Würfel hat die Kantenlänge {s} cm. Wie groß ist seine Oberfläche (cm²)?", 6 * s * s, f"O = 6 × a² = 6 × {s*s} = {6*s*s} cm².", 2
        elif kind == 1:
            l, b, h = R.randint(2, 12), R.randint(2, 9), R.randint(2, 8)
            q, a, ex, lv = f"Ein Quader ist {l} cm lang, {b} cm breit und {h} cm hoch. Wie groß ist sein Volumen (cm³)?", l * b * h, f"V = l × b × h = {l} × {b} × {h} = {l*b*h} cm³.", 2
        else:
            l, b, h = R.randint(10, 50), R.randint(10, 40), R.randint(10, 30)
            q, a, ex, lv = (f"Ein Aquarium ist {l} cm lang, {b} cm breit und {h} cm hoch. Wie viele Liter passen hinein? (1 Liter = 1000 cm³)",
                            l * b * h / 1000, f"{l} × {b} × {h} = {l*b*h} cm³ = {fmt(l*b*h/1000)} Liter.", 3)
        integer = abs(a - round(a)) < 1e-9
        o, k = num_opts(int(round(a)) if integer else a, integer=integer)
        if add_mc(G, lv, "Körper", q, o, k, ex):
            made += 1


# --- Mentale Rotation / Spiegelung mit Polyominos ---
def norm(cells):
    mx = min(x for x, y in cells)
    my = min(y for x, y in cells)
    return tuple(sorted((x - mx, y - my) for x, y in cells))


def rot(cells):
    return norm([(y, -x) for x, y in cells])


def mir(cells):
    return norm([(-x, y) for x, y in cells])


def rotations(c):
    out = [norm(c)]
    for _ in range(3):
        out.append(rot(out[-1]))
    return out


def random_poly(k):
    cells = {(0, 0)}
    while len(cells) < k:
        x, y = R.choice(list(cells))
        dx, dy = R.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        cells.add((x + dx, y + dy))
    return norm(cells)


def rotation_tasks(n=25):
    made = 0
    while made < n:
        lvl = lvl_for(made, n)
        k = {1: 5, 2: 6, 3: 8}[lvl]
        base = random_poly(k)
        rs = rotations(base)
        ms = rotations(mir(base))
        if set(rs) & set(ms) or len(set(rs)) < 4:
            continue  # Form muss „händig“ sein, sonst ist die Aufgabe nicht eindeutig
        turn = R.choice([1, 2, 3])
        correct = rs[turn]
        wrong = R.sample(ms, 3)
        opts = [correct] + wrong
        R.shuffle(opts)
        ans = opts.index(correct)
        q = "Welche Figur ist nur GEDREHT (nicht gespiegelt) die Figur oben?"
        key = (G, q + str(base))
        if key in SEEN:
            continue
        SEEN.add(key)
        TASKS.append({"cat": G, "type": "shape", "lvl": lvl, "title": "Mentale Rotation", "q": q,
                      "p": {"base": base, "opts": opts}, "ans": ans,
                      "expl": f"Die richtige Figur ist um {turn*90}° gedreht. Die anderen sind Spiegelbilder – egal wie man sie dreht, sie passen nicht deckungsgleich auf die Ausgangsfigur."})
        made += 1


def spiegel_tasks(n=10):
    made = 0
    while made < n:
        lvl = 2 if made < 5 else 3
        base = random_poly(6 if lvl == 2 else 7)
        m = mir(base)
        rs = rotations(base)
        if m in rs:
            continue
        wrong_pool = [r for r in rs[1:] if r != m] + [r for r in rotations(m)[1:] if r != m]
        wrong_pool = list(dict.fromkeys(wrong_pool))
        if len(wrong_pool) < 3:
            continue
        opts = [m] + R.sample(wrong_pool, 3)
        R.shuffle(opts)
        q = "Welche Figur ist das Spiegelbild der Figur oben (Spiegel senkrecht rechts daneben)?"
        key = (G, q + str(base))
        if key in SEEN:
            continue
        SEEN.add(key)
        TASKS.append({"cat": G, "type": "shape", "lvl": lvl, "title": "Spiegelbild", "q": q,
                      "p": {"base": base, "opts": opts}, "ans": opts.index(m),
                      "expl": "Beim Spiegeln an einer senkrechten Achse wird links und rechts vertauscht, oben und unten bleiben gleich. Gedrehte Figuren sind keine Spiegelbilder."})
        made += 1


def koordinaten(n=10):
    made = 0
    while made < n:
        if made % 2 == 0:
            (x1, y1), (dx, dy) = (R.randint(-5, 5), R.randint(-5, 5)), R.choice([(3, 4), (6, 8), (5, 12), (4, 3), (8, 6)])
            x2, y2 = x1 + dx * R.choice([1, -1]), y1 + dy * R.choice([1, -1])
            d = int(math.hypot(dx, dy))
            q = f"Wie weit sind die Punkte A({x1}|{y1}) und B({x2}|{y2}) voneinander entfernt?"
            ex = f"Δx = {abs(x2-x1)}, Δy = {abs(y2-y1)}. Abstand = √({abs(x2-x1)}² + {abs(y2-y1)}²) = √{d*d} = {d}."
            o, k = num_opts(d, spread=3)
            lv = 3
        else:
            x, y = R.randint(-6, 6), R.randint(-6, 6)
            kind = R.choice(["x", "y"])
            if kind == "x":
                corr = f"({x}|{-y})"
                q = f"Der Punkt P({x}|{y}) wird an der x-Achse gespiegelt. Wo liegt der Bildpunkt?"
                ex = f"Beim Spiegeln an der x-Achse ändert sich nur das Vorzeichen der y-Koordinate: ({x}|{-y})."
            else:
                corr = f"({-x}|{y})"
                q = f"Der Punkt P({x}|{y}) wird an der y-Achse gespiegelt. Wo liegt der Bildpunkt?"
                ex = f"Beim Spiegeln an der y-Achse ändert sich nur das Vorzeichen der x-Koordinate: ({-x}|{y})."
            if x == 0 or y == 0:
                continue
            cands = {f"({-x}|{-y})", f"({y}|{x})", f"({x}|{y})", f"({-x}|{y})", f"({x}|{-y})"} - {corr}
            o, k = text_opts(corr, R.sample(sorted(cands), 3))
            lv = 2
        if add_mc(G, lv, "Koordinaten", q, o, k, ex):
            made += 1

# ---------------------------------------------------------------------------
# C. GEDÄCHTNIS & AUFMERKSAMKEIT (120)
# ---------------------------------------------------------------------------
M = "gedaechtnis"
WOERTER = ["Apfel", "Brücke", "Kerze", "Wolke", "Hammer", "Tiger", "Gabel", "Insel", "Spiegel", "Trommel",
           "Laterne", "Kompass", "Teppich", "Möwe", "Schlüssel", "Banane", "Fenster", "Zelt", "Geige", "Koffer",
           "Rakete", "Pinsel", "Leiter", "Muschel", "Kaktus", "Anker", "Besen", "Krone", "Ziege", "Uhr",
           "Feder", "Kessel", "Mantel", "Nadel", "Ofen", "Pilz", "Rose", "Sattel", "Tasse", "Vulkan",
           "Wagen", "Zwiebel", "Burg", "Drache", "Eimer", "Flöte", "Glocke", "Harfe", "Igel", "Jacke"]


def memory_tasks():
    # Zahlenspanne vorwärts 20
    for i in range(20):
        L = 4 + i * 6 // 20  # 4..9
        add_inter(M, "span", 1 if L <= 5 else (2 if L <= 7 else 3), "Zahlen merken",
                  f"Merke dir die {L} Ziffern und tippe sie danach in derselben Reihenfolge ein.",
                  {"len": L, "ms": 1000 - min(400, i * 20), "rev": False, "v": i},
                  f"Trainiert das Arbeitsgedächtnis. Tipp: Ziffern in Gruppen bündeln (z. B. 3-3), so wie bei Telefonnummern. Die meisten Menschen schaffen 7 ± 2 Ziffern.")
    for i in range(10):
        L = 3 + i * 4 // 10
        add_inter(M, "span", 2 if L <= 4 else 3, "Zahlen rückwärts",
                  f"Merke dir die {L} Ziffern und tippe sie danach RÜCKWÄRTS ein.",
                  {"len": L, "ms": 1000, "rev": True, "v": i},
                  "Rückwärts wiedergeben verlangt, die Ziffern im Kopf umzusortieren – eine klassische Übung für das Arbeitsgedächtnis.")
    for i in range(15):
        L = 3 + i * 6 // 15
        add_inter(M, "simon", 1 if L <= 4 else (2 if L <= 6 else 3), "Farbfolge",
                  f"Schau dir an, in welcher Reihenfolge die Felder aufleuchten ({L} Schritte), und tippe sie nach.",
                  {"len": L, "ms": 700 - i * 15, "v": i},
                  "Visuell-räumliches Gedächtnis. Tipp: Die Folge innerlich mitsprechen (z. B. „rot, blau, blau, gelb“).")
    for i in range(15):
        L = 5 + i * 6 // 15
        words = R.sample(WOERTER, L + 4)
        add_inter(M, "words", 1 if L <= 6 else (2 if L <= 8 else 3), "Wörter merken",
                  f"Merke dir {L} Wörter. Danach musst du sie unter anderen Wörtern wiedererkennen.",
                  {"words": words[:L], "distract": words[L:], "ms": 1500 - i * 30},
                  "Tipp: Verknüpfe die Wörter zu einer verrückten Geschichte – Bilder im Kopf bleiben viel besser hängen als einzelne Wörter.")
    for i in range(15):
        g = 3 if i < 5 else (4 if i < 11 else 5)
        k = {3: 3 + i % 3, 4: 4 + i % 4, 5: 6 + i % 4}[g]
        add_inter(M, "grid", {3: 1, 4: 2, 5: 3}[g], "Positionen merken",
                  f"Merke dir, welche {k} Felder kurz aufleuchten, und tippe sie danach an.",
                  {"size": g, "k": k, "ms": 1600 - i * 40, "v": i},
                  "Räumliches Arbeitsgedächtnis. Tipp: Sieh die leuchtenden Felder als ein Muster oder eine Form, nicht als einzelne Punkte.")
    for i in range(15):
        trials = 10 + (i // 5) * 5
        add_inter(M, "stroop", 1 + i // 5, "Stroop-Test",
                  f"Tippe auf die FARBE, in der das Wort geschrieben ist – nicht auf das, was dort steht. {trials} Durchgänge.",
                  {"trials": trials, "incong": 0.5 + i * 0.03, "limit": 2500 - i * 100},
                  "Der Stroop-Effekt: Lesen läuft automatisch ab, deshalb stört das Wort. Hier trainierst du, automatische Reaktionen zu unterdrücken (Inhibition).")
    SETS = [["O", "Q"], ["E", "F"], ["b", "d"], ["6", "9"], ["M", "N"], ["▲", "▼"], ["◐", "◑"], ["8", "B"],
            ["p", "q"], ["C", "G"], ["★", "☆"], ["1", "l"], ["u", "v"], ["2", "Z"], ["◆", "◇"]]
    for i in range(15):
        g = 4 + i // 4
        a, b = SETS[i]
        add_inter(M, "odd", 1 + i // 5, "Finde das Andere",
                  f"In dem Raster ist genau ein Zeichen anders. Finde es so schnell wie möglich – 5 Runden.",
                  {"size": g, "a": a, "b": b, "rounds": 5},
                  "Trainiert selektive Aufmerksamkeit und visuelle Suche. Tipp: Den Blick nicht hektisch springen lassen, sondern Zeile für Zeile abtasten.")
    SYM = ["★", "●", "▲", "■", "◆", "♥", "♣", "✿"]
    for i in range(15):
        g = 5 + i // 3
        add_inter(M, "count", 1 + i // 5, "Symbole zählen",
                  f"Zähle, wie oft das gesuchte Symbol im Feld vorkommt.",
                  {"size": g, "target": SYM[i % len(SYM)], "kinds": 3 + i // 4, "v": i},
                  "Konzentration und Genauigkeit. Tipp: Zeilenweise zählen und am Ende jeder Zeile die Zwischensumme merken.")

# ---------------------------------------------------------------------------
# D. REAKTION & TEMPO (100)
# ---------------------------------------------------------------------------
X = "reaktion"


def reaction_tasks():
    for i in range(15):
        add_inter(X, "react", 1 + i // 5, "Reaktionstest",
                  "Warte, bis das Feld GRÜN wird, und tippe dann sofort. Nicht zu früh tippen!",
                  {"trials": 3 + i // 3, "goal": 420 - i * 10, "min": 1000, "max": 3500 + i * 100},
                  "Misst deine einfache Reaktionszeit. Typisch sind 200–300 ms. Ausgeruht, ohne Ablenkung und mit regelmäßigem Training wirst du schneller.")
    for i in range(15):
        add_inter(X, "gonogo", 1 + i // 5, "Go / No-Go",
                  "Tippe nur bei einem GRÜNEN Kreis. Bei einem ROTEN Kreis nicht tippen!",
                  {"trials": 12 + i, "nogo": 0.25 + i * 0.015, "show": 1100 - i * 35},
                  "Trainiert Impulskontrolle: schnell reagieren, aber im richtigen Moment bremsen können.")
    for i in range(15):
        add_inter(X, "arrows", 1 + i // 5, "Pfeil-Richtung",
                  "Tippe auf die Seite, in die der MITTLERE Pfeil zeigt. Die anderen Pfeile ignorieren.",
                  {"trials": 10 + i, "incong": 0.3 + i * 0.03, "limit": 2000 - i * 60},
                  "Das ist der Flanker-Test: Er trainiert, störende Reize in der Umgebung auszublenden.")
    for i in range(15):
        add_inter(X, "compare", 1 + i // 5, "Schneller Vergleich",
                  "Welche Seite ist größer? Tippe so viele richtig wie möglich in 30 Sekunden.",
                  {"secs": 30, "mode": ["zahl", "zahl", "term"][i // 5], "range": 20 + i * 15, "goal": 14 + i // 2},
                  "Verarbeitungsgeschwindigkeit: schnelles Erfassen und Entscheiden. Bei Termen hilft Überschlagen statt exaktem Rechnen.")
    for i in range(15):
        g = 3 if i < 4 else (4 if i < 9 else 5)
        add_inter(X, "schulte", {3: 1, 4: 2, 5: 3}[g], "Schulte-Tabelle",
                  f"Tippe die Zahlen von 1 bis {g*g} der Reihe nach an – so schnell wie möglich.",
                  {"size": g, "goal": {3: 12, 4: 25, 5: 45}[g] - (i % 5) * {3: 1, 4: 2, 5: 3}[g], "v": i},
                  "Schulte-Tabellen trainieren das periphere Sehen und die Suchgeschwindigkeit. Profis schauen in die Mitte und finden die Zahlen aus dem Augenwinkel.")
    for i in range(15):
        add_inter(X, "targets", 1 + i // 5, "Ziele treffen",
                  "Tippe die Kreise an, bevor sie verschwinden.",
                  {"count": 10 + i, "life": 1500 - i * 60, "size": 64 - i * 2},
                  "Auge-Hand-Koordination und Reaktion. Tipp: Blick locker in der Mitte halten, nicht jedem Kreis hinterherschauen.")
    for i in range(10):
        add_inter(X, "sprint", 1 + i // 4, "Rechen-Sprint",
                  "Löse so viele Rechnungen wie möglich in 45 Sekunden.",
                  {"secs": 45, "max": 10 + i * 6, "ops": "+-" if i < 4 else ("+-×" if i < 8 else "+-×÷"), "goal": 10 + i},
                  "Automatisiertes Kopfrechnen entlastet das Arbeitsgedächtnis. Tempo kommt durch Wiederholung.")


def main():
    kopfrechnen(); prozent(); brueche(); gleichungen(); zahlenreihen(); logik(); textaufgaben()
    flaechen(); winkel(); pythagoras(); koerper(); rotation_tasks(); spiegel_tasks(); koordinaten()
    memory_tasks()
    reaction_tasks()
    cats = {}
    for t in TASKS:
        cats[t["cat"]] = cats.get(t["cat"], 0) + 1
    print("Kategorien:", cats, "gesamt:", len(TASKS))
    assert cats == {"rechnen": 160, "geometrie": 120, "gedaechtnis": 120, "reaktion": 100}, cats
    # innerhalb jeder Kategorie nach Stufe sortieren, dann durchnummerieren
    order = ["rechnen", "geometrie", "gedaechtnis", "reaktion"]
    TASKS.sort(key=lambda t: (order.index(t["cat"]), t["lvl"]))
    for i, t in enumerate(TASKS, 1):
        t["id"] = i
    import re
    money = re.compile(r"(?<![\d,])(\d+),(\d)(?!\d)( ?€)")
    for t in TASKS:
        if t["type"] == "mc" and "(in €)" in t["q"]:
            t["opts"] = [o + ",00" if "," not in o else (o + "0" if len(o.split(",")[1]) == 1 else o) for o in t["opts"]]
            t["q"] = money.sub(lambda m: f"{m.group(1)},{m.group(2)}0{m.group(3)}", t["q"])
            t["expl"] = money.sub(lambda m: f"{m.group(1)},{m.group(2)}0{m.group(3)}", t["expl"])
            assert len(set(t["opts"])) == len(t["opts"])
    for t in TASKS:
        if t["type"] in ("mc", "shape"):
            assert 0 <= t["ans"] < len(t.get("opts") or t["p"]["opts"]), t
    out = os.path.join(os.path.dirname(__file__), "..", "www", "tasks.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("// Automatisch erzeugt von tools/generate_tasks.py – nicht von Hand bearbeiten\n")
        f.write("window.TASKS = ")
        json.dump(TASKS, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print("geschrieben:", os.path.abspath(out))


if __name__ == "__main__":
    main()
