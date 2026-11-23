"""Genera los pasos del desarrollo matemático con sustitución numérica."""

from math import factorial


def _f(x, d=4):
    """Formato numérico con d decimales y coma decimal."""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pasos_mm1(lam, mu):
    rho = lam / mu
    p0 = 1 - rho
    l = lam / (mu - lam)
    lq = lam ** 2 / (mu * (mu - lam))
    w = 1 / (mu - lam)
    wq = lam / (mu * (mu - lam))
    return [
        ("ρ = λ / μ", f"{_f(lam)} / {_f(mu)}", _f(rho), "Utilización del sistema"),
        ("P₀ = 1 − ρ", f"1 − {_f(rho)}", _f(p0), "Probabilidad de sistema vacío"),
        ("L = λ / (μ − λ)", f"{_f(lam)} / ({_f(mu)} − {_f(lam)})", _f(l) + " clientes", "Clientes promedio en el sistema"),
        ("Lq = λ² / (μ(μ − λ))", f"{_f(lam)}² / ({_f(mu)} · ({_f(mu)} − {_f(lam)}))", _f(lq) + " clientes", "Clientes promedio en la cola"),
        ("W = 1 / (μ − λ)", f"1 / ({_f(mu)} − {_f(lam)})", _f(w), "Tiempo promedio en el sistema"),
        ("Wq = λ / (μ(μ − λ))", f"{_f(lam)} / ({_f(mu)} · ({_f(mu)} − {_f(lam)}))", _f(wq), "Tiempo promedio en la cola"),
        ("Pw = ρ", f"{_f(rho)}", _f(rho), "Probabilidad de que un cliente espere"),
    ]


def pasos_mms(lam, mu, s):
    a = lam / mu
    rho = lam / (s * mu)

    terminos = [a ** n / factorial(n) for n in range(s)]
    suma_parcial = sum(terminos)
    cola = (a ** s) / (factorial(s) * (1 - rho))
    p0 = 1 / (suma_parcial + cola)

    lq = p0 * (a ** s) * rho / (factorial(s) * (1 - rho) ** 2)
    l = lq + a
    wq = lq / lam
    w = wq + 1 / mu
    pw = (a ** s) * p0 / (factorial(s) * (1 - rho))

    terminos_txt = " + ".join(f"{_f(a)}^{n}/{n}!" for n in range(s))

    return [
        ("a = λ / μ", f"{_f(lam)} / {_f(mu)}", _f(a), "Carga ofrecida"),
        ("ρ = λ / (s·μ)", f"{_f(lam)} / ({s} · {_f(mu)})", _f(rho), "Utilización por servidor"),
        (
            "P₀ = [ Σ aⁿ/n! + aˢ/(s!(1−ρ)) ]⁻¹",
            f"[ ({terminos_txt}) + {_f(a)}^{s}/({s}!·(1−{_f(rho)})) ]⁻¹",
            _f(p0),
            "Probabilidad de sistema vacío",
        ),
        (
            "Lq = P₀·aˢ·ρ / (s!(1−ρ)²)",
            f"{_f(p0)} · {_f(a)}^{s} · {_f(rho)} / ({s}! · (1−{_f(rho)})²)",
            _f(lq) + " clientes",
            "Clientes promedio en la cola",
        ),
        ("L = Lq + a", f"{_f(lq)} + {_f(a)}", _f(l) + " clientes", "Clientes promedio en el sistema"),
        ("Wq = Lq / λ", f"{_f(lq)} / {_f(lam)}", _f(wq), "Tiempo promedio en la cola"),
        ("W = Wq + 1/μ", f"{_f(wq)} + 1/{_f(mu)}", _f(w), "Tiempo promedio en el sistema"),
        (
            "Pw = aˢ·P₀ / (s!(1−ρ))",
            f"{_f(a)}^{s} · {_f(p0)} / ({s}! · (1−{_f(rho)}))",
            _f(pw),
            "Probabilidad de esperar (Erlang C)",
        ),
    ]
