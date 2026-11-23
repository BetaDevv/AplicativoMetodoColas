from django import template

register = template.Library()


def _fmt(valor, decimales):
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return valor
    return f"{v:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@register.filter
def num4(valor):
    return _fmt(valor, 4)


@register.filter
def num2(valor):
    return _fmt(valor, 2)


@register.filter
def num1(valor):
    return _fmt(valor, 1)


@register.filter
def num0(valor):
    return _fmt(valor, 0)


@register.filter
def porc(valor):
    """Multiplica por 100 y devuelve con 1 decimal."""
    try:
        v = float(valor) * 100
    except (TypeError, ValueError):
        return valor
    return f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


@register.filter
def ancho(pn, pn_max):
    try:
        v = float(pn) / float(pn_max) * 100 if float(pn_max) > 0 else 0
    except (TypeError, ValueError, ZeroDivisionError):
        return 0
    return f"{v:.2f}"
