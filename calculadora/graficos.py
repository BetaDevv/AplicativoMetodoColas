"""Genera gráficas en SVG embebidas (strings). Matplotlib solo para costos."""

import io

import matplotlib
matplotlib.use("Agg")  # backend sin GUI
import matplotlib.pyplot as plt


def grafica_costos_svg(filas, s_optimo, moneda="COP", unidad="h") -> str:
    ss = [f.s for f in filas]
    cs = [f.costo_servicio for f in filas]
    ce = [f.costo_espera for f in filas]
    ct = [f.costo_total for f in filas]

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(ss, cs, marker="o", label="Costo de servicio (CS)", color="#334155")
    ax.plot(ss, ce, marker="s", label="Costo de espera (CE)", color="#94a3b8", linestyle="--")
    ax.plot(ss, ct, marker="D", label="Costo total (CT)", color="#1e40af", linewidth=2)

    opt_ct = ct[ss.index(s_optimo)]
    ax.axvline(s_optimo, color="#1e40af", linestyle=":", alpha=0.6)
    ax.annotate(
        f"s óptimo = {s_optimo}",
        xy=(s_optimo, opt_ct),
        xytext=(5, 10), textcoords="offset points",
        fontsize=9, color="#1e40af",
    )

    ax.set_xlabel("Número de servidores (s)")
    ax.set_ylabel(f"Costo ({moneda}/{unidad})")
    ax.set_xticks(ss)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best", frameon=False, fontsize=9)
    fig.tight_layout()

    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
