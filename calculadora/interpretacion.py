"""Genera texto interpretativo a partir de un ResultadoCola o ResultadoCostos."""


def _f(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _f4(x):
    return _f(x, 4)


def interpretar_cola(res, unidad: str) -> dict:
    """Devuelve dict con parrafos de interpretación y advertencias."""
    w_min = res.w * 60 if unidad == "h" else (res.w if unidad == "min" else res.w * 1440)
    wq_min = res.wq * 60 if unidad == "h" else (res.wq if unidad == "min" else res.wq * 1440)

    parrafo = (
        f"Los servidores están ocupados el {_f(res.rho * 100)} % del tiempo. "
        f"En promedio hay {_f(res.l)} clientes en el sistema "
        f"({_f(res.lq)} esperando en la cola). "
        f"Cada cliente permanece {_f(w_min)} min en el sistema, "
        f"de los cuales {_f(wq_min)} son de espera."
    )

    advertencias = []
    if res.rho >= 0.85:
        advertencias.append(
            f"El sistema está muy cargado (ρ = {_f4(res.rho)}). "
            "Pequeñas variaciones en λ disparan la espera."
        )
    elif res.rho < 0.3:
        advertencias.append(
            f"Hay capacidad ociosa (ρ = {_f4(res.rho)}). "
            "Puede valer la pena revisar si hay más servidores de los necesarios."
        )

    return {"parrafo": parrafo, "advertencias": advertencias}


def interpretar_costos(res, unidad: str, moneda: str) -> str:
    fila_opt = next(f for f in res.filas if f.s == res.s_optimo)
    fila_min = res.filas[0]
    wq_opt_min = fila_opt.wq * 60 if unidad == "h" else (fila_opt.wq if unidad == "min" else fila_opt.wq * 1440)
    wq_min_min = fila_min.wq * 60 if unidad == "h" else (fila_min.wq if unidad == "min" else fila_min.wq * 1440)

    txt = (
        f"La opción de menor costo total es s = {res.s_optimo}, "
        f"con CT = {_f(res.costo_total_optimo, 0)} {moneda}/{unidad}."
    )
    if fila_opt.s != fila_min.s:
        txt += (
            f" Pasar de {fila_min.s} a {fila_opt.s} servidores reduce la espera promedio "
            f"de {_f(wq_min_min)} a {_f(wq_opt_min)} minutos."
        )
    return txt
