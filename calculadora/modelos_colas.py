"""Motor de cálculo de Teoría de Colas.

Modelos implementados: M/M/1 y M/M/s con análisis de costos.
Notación: lam = tasa de llegada, mu = tasa de servicio por servidor,
s = número de servidores. lam y mu en la misma unidad de tiempo.
"""

from dataclasses import dataclass, field
from math import factorial


class ColaInestableError(ValueError):
    """Se lanza cuando la utilización es mayor o igual a 1."""


@dataclass
class ResultadoCola:
    modelo: str
    lam: float
    mu: float
    s: int
    rho: float
    p0: float
    l: float
    lq: float
    w: float
    wq: float
    pw: float
    a: float = 0.0
    distribucion: list[float] = field(default_factory=list)
    distribucion_acumulada: list[float] = field(default_factory=list)


def validar_entradas(lam: float, mu: float, s: int) -> None:
    if lam <= 0:
        raise ValueError("La tasa de llegada (lambda) debe ser mayor que cero.")
    if mu <= 0:
        raise ValueError("La tasa de servicio (mu) debe ser mayor que cero.")
    if not isinstance(s, int) or s < 1:
        raise ValueError("El número de servidores (s) debe ser un entero mayor o igual a 1.")
    if lam >= s * mu:
        raise ColaInestableError(
            f"El sistema no es estable: lambda ({lam:g}) es mayor o igual que "
            f"s*mu ({s * mu:g}). La cola crecería indefinidamente. "
            "Aumente el número de servidores o la tasa de servicio."
        )


def _distribucion_mm1(rho: float, n_max: int) -> tuple[list[float], list[float]]:
    pn = [(1 - rho) * rho ** n for n in range(n_max + 1)]
    acumulada, s_ = [], 0.0
    for p in pn:
        s_ += p
        acumulada.append(s_)
    return pn, acumulada


def _distribucion_mms(a: float, rho: float, s: int, p0: float, n_max: int) -> tuple[list[float], list[float]]:
    pn: list[float] = []
    for n in range(n_max + 1):
        if n <= s:
            pn.append((a ** n / factorial(n)) * p0)
        else:
            pn.append((a ** n / (factorial(s) * s ** (n - s))) * p0)
    acumulada, s_ = [], 0.0
    for p in pn:
        s_ += p
        acumulada.append(s_)
    return pn, acumulada


def calcular_mm1(lam: float, mu: float, n_max: int = 10) -> ResultadoCola:
    validar_entradas(lam, mu, 1)
    rho = lam / mu
    p0 = 1 - rho
    l = lam / (mu - lam)
    lq = (lam ** 2) / (mu * (mu - lam))
    w = 1 / (mu - lam)
    wq = lam / (mu * (mu - lam))
    pw = rho
    pn, pn_acum = _distribucion_mm1(rho, n_max)
    return ResultadoCola(
        modelo="M/M/1",
        lam=lam, mu=mu, s=1,
        rho=rho, p0=p0, l=l, lq=lq, w=w, wq=wq, pw=pw,
        a=rho,
        distribucion=pn,
        distribucion_acumulada=pn_acum,
    )


def calcular_mms(lam: float, mu: float, s: int, n_max: int = 10) -> ResultadoCola:
    validar_entradas(lam, mu, s)
    a = lam / mu
    rho = lam / (s * mu)

    suma = sum(a ** n / factorial(n) for n in range(s))
    cola = (a ** s) / (factorial(s) * (1 - rho))
    p0 = 1 / (suma + cola)

    lq = p0 * (a ** s) * rho / (factorial(s) * (1 - rho) ** 2)
    l = lq + a
    wq = lq / lam
    w = wq + 1 / mu
    pw = (a ** s) * p0 / (factorial(s) * (1 - rho))

    pn, pn_acum = _distribucion_mms(a, rho, s, p0, n_max)

    return ResultadoCola(
        modelo="M/M/s",
        lam=lam, mu=mu, s=s,
        rho=rho, p0=p0, l=l, lq=lq, w=w, wq=wq, pw=pw,
        a=a,
        distribucion=pn,
        distribucion_acumulada=pn_acum,
    )


@dataclass
class FilaCosto:
    s: int
    rho: float
    l: float
    lq: float
    wq: float
    w: float
    costo_servicio: float
    costo_espera: float
    costo_total: float


@dataclass
class ResultadoCostos:
    lam: float
    mu: float
    cs: float
    cw: float
    base: str  # "L" o "Lq"
    s_minimo_estable: int
    s_maximo: int
    filas: list[FilaCosto]
    s_optimo: int
    costo_total_optimo: float


def _s_minimo_estable(lam: float, mu: float) -> int:
    # Menor entero s tal que s*mu > lam
    s = 1
    while s * mu <= lam:
        s += 1
    return s


def analizar_costos(
    lam: float,
    mu: float,
    cs: float,
    cw: float,
    s_max: int,
    base: str = "L",
) -> ResultadoCostos:
    if lam <= 0 or mu <= 0:
        raise ValueError("lambda y mu deben ser mayores que cero.")
    if cs < 0 or cw < 0:
        raise ValueError("Los costos no pueden ser negativos.")
    if base not in ("L", "Lq"):
        raise ValueError("La base de costo de espera debe ser 'L' o 'Lq'.")

    s_min = _s_minimo_estable(lam, mu)
    if s_max < s_min:
        raise ValueError(
            f"El s máximo ({s_max}) es menor que el s mínimo estable ({s_min}). "
            "Aumente el s máximo."
        )

    filas: list[FilaCosto] = []
    for s in range(s_min, s_max + 1):
        r = calcular_mms(lam, mu, s, n_max=0)
        servicio = cs * s
        espera = cw * (r.l if base == "L" else r.lq)
        total = servicio + espera
        filas.append(FilaCosto(
            s=s, rho=r.rho, l=r.l, lq=r.lq, wq=r.wq, w=r.w,
            costo_servicio=servicio,
            costo_espera=espera,
            costo_total=total,
        ))

    fila_optima = min(filas, key=lambda f: f.costo_total)
    return ResultadoCostos(
        lam=lam, mu=mu, cs=cs, cw=cw, base=base,
        s_minimo_estable=s_min, s_maximo=s_max,
        filas=filas,
        s_optimo=fila_optima.s,
        costo_total_optimo=fila_optima.costo_total,
    )
