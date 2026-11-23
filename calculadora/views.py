from django.shortcuts import render

from .desarrollo import pasos_mm1, pasos_mms
from .forms import FormCostos, FormMM1, FormMMs
from .graficos import grafica_costos_svg
from .interpretacion import interpretar_cola, interpretar_costos
from .modelos_colas import (
    ColaInestableError,
    analizar_costos,
    calcular_mm1,
    calcular_mms,
)


EJEMPLO_MM1 = {
    "lam": "10",
    "mu": "12",
    "unidad": "h",
    "n_max": "10",
    "enunciado": (
        "A una droguería con una sola caja llegan en promedio 10 clientes por hora "
        "(distribución Poisson). El cajero atiende en promedio 12 clientes por hora "
        "(tiempo de servicio exponencial). Calcular los indicadores de desempeño."
    ),
}

EJEMPLO_MMS = {
    "lam": "20",
    "mu": "8",
    "s": "3",
    "unidad": "h",
    "n_max": "10",
    "enunciado": (
        "A una sucursal bancaria llegan 20 clientes por hora (Poisson). "
        "Cada asesor atiende 8 clientes por hora (exponencial). "
        "Hay 3 asesores. Calcular los indicadores de desempeño."
    ),
}

EJEMPLO_COSTOS = {
    "lam": "20",
    "mu": "8",
    "cs": "15000",
    "cw": "20000",
    "s_max": "6",
    "unidad": "h",
    "base": "L",
    "moneda": "COP",
    "enunciado": (
        "Mismo banco (λ = 20/h, μ = 8/h). Cada asesor cuesta 15.000 COP por hora y "
        "cada hora que un cliente permanece en el sistema se valora en 20.000 COP. "
        "Evaluar de s = 3 a s = 6 con costo de espera sobre L."
    ),
}


def inicio(request):
    return render(request, "calculadora/inicio.html")


def _minutos(valor, unidad):
    if unidad == "h":
        return valor * 60
    if unidad == "min":
        return valor
    return valor * 1440


def mm1(request):
    enunciado = EJEMPLO_MM1["enunciado"]

    if request.method == "POST":
        form = FormMM1(request.POST)
    elif request.GET.get("ejemplo") == "1":
        datos_iniciales = {k: v for k, v in EJEMPLO_MM1.items() if k != "enunciado"}
        form = FormMM1(initial=datos_iniciales)
    else:
        form = FormMM1()

    contexto = {"form": form, "enunciado": enunciado, "unidad_defecto": "h"}

    if request.method == "POST" and form.is_valid():
        lam = form.cleaned_data["lam"]
        mu = form.cleaned_data["mu"]
        unidad = form.cleaned_data["unidad"]
        n_max = form.cleaned_data["n_max"]
        try:
            resultado = calcular_mm1(lam, mu, n_max=n_max)
        except ColaInestableError as e:
            contexto["error_calculo"] = str(e)
            return render(request, "calculadora/mm1.html", contexto)

        contexto.update({
            "resultado": resultado,
            "unidad": unidad,
            "w_min": _minutos(resultado.w, unidad),
            "wq_min": _minutos(resultado.wq, unidad),
            "pasos": pasos_mm1(lam, mu),
            "interpretacion": interpretar_cola(resultado, unidad),
            "distribucion_zip": list(zip(
                range(len(resultado.distribucion)),
                resultado.distribucion,
                resultado.distribucion_acumulada,
            )),
            "pn_max": max(resultado.distribucion) if resultado.distribucion else 1.0,
        })

    return render(request, "calculadora/mm1.html", contexto)


def mms(request):
    enunciado = EJEMPLO_MMS["enunciado"]

    if request.method == "POST":
        form = FormMMs(request.POST)
    elif request.GET.get("ejemplo") == "1":
        datos_iniciales = {k: v for k, v in EJEMPLO_MMS.items() if k != "enunciado"}
        form = FormMMs(initial=datos_iniciales)
    else:
        form = FormMMs()

    contexto = {"form": form, "enunciado": enunciado, "unidad_defecto": "h"}

    if request.method == "POST" and form.is_valid():
        lam = form.cleaned_data["lam"]
        mu = form.cleaned_data["mu"]
        s = form.cleaned_data["s"]
        unidad = form.cleaned_data["unidad"]
        n_max = form.cleaned_data["n_max"]
        try:
            resultado = calcular_mms(lam, mu, s, n_max=n_max)
        except ColaInestableError as e:
            contexto["error_calculo"] = str(e)
            return render(request, "calculadora/mms.html", contexto)

        contexto.update({
            "resultado": resultado,
            "unidad": unidad,
            "w_min": _minutos(resultado.w, unidad),
            "wq_min": _minutos(resultado.wq, unidad),
            "pasos": pasos_mms(lam, mu, s),
            "interpretacion": interpretar_cola(resultado, unidad),
            "distribucion_zip": list(zip(
                range(len(resultado.distribucion)),
                resultado.distribucion,
                resultado.distribucion_acumulada,
            )),
            "pn_max": max(resultado.distribucion) if resultado.distribucion else 1.0,
        })

    return render(request, "calculadora/mms.html", contexto)


def costos(request):
    enunciado = EJEMPLO_COSTOS["enunciado"]

    if request.method == "POST":
        form = FormCostos(request.POST)
    elif request.GET.get("ejemplo") == "1":
        datos_iniciales = {k: v for k, v in EJEMPLO_COSTOS.items() if k != "enunciado"}
        form = FormCostos(initial=datos_iniciales)
    else:
        form = FormCostos()

    contexto = {"form": form, "enunciado": enunciado}

    if request.method == "POST" and form.is_valid():
        lam = form.cleaned_data["lam"]
        mu = form.cleaned_data["mu"]
        cs = form.cleaned_data["cs"]
        cw = form.cleaned_data["cw"]
        s_max = form.cleaned_data["s_max"]
        unidad = form.cleaned_data["unidad"]
        base = form.cleaned_data["base"]
        moneda = form.cleaned_data["moneda"]

        try:
            resultado = analizar_costos(lam, mu, cs, cw, s_max, base)
        except ValueError as e:
            contexto["error_calculo"] = str(e)
            return render(request, "calculadora/costos.html", contexto)

        filas = []
        for f in resultado.filas:
            filas.append({
                "s": f.s,
                "rho": f.rho,
                "l": f.l,
                "lq": f.lq,
                "wq_min": _minutos(f.wq, unidad),
                "costo_servicio": f.costo_servicio,
                "costo_espera": f.costo_espera,
                "costo_total": f.costo_total,
                "optima": f.s == resultado.s_optimo,
            })

        contexto.update({
            "resultado": resultado,
            "filas": filas,
            "unidad": unidad,
            "moneda": moneda,
            "grafica_svg": grafica_costos_svg(resultado.filas, resultado.s_optimo, moneda, unidad),
            "interpretacion": interpretar_costos(resultado, unidad, moneda),
        })

    return render(request, "calculadora/costos.html", contexto)
