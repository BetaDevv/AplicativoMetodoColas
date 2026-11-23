# Calculadora de Teoría de Colas

Aplicativo del trabajo final de **Investigación de Operaciones** (ITM — Ingeniería de Sistemas).
Calcula los indicadores de desempeño de los modelos **M/M/1** y **M/M/s** y realiza un
**análisis de costos** (costo de servicio vs. costo de espera) para recomendar el número
óptimo de servidores.

## Requisitos

- Python 3.11 o superior
- pip

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Cómo correr el aplicativo

```bash
source venv/bin/activate
python manage.py runserver
```

Luego abrir `http://127.0.0.1:8000/` en el navegador.

## Cómo correr las pruebas

```bash
python manage.py test
```

Las pruebas verifican los valores de los ejemplos base contra los resultados esperados
(tolerancia 1e-3), la ley de Little, la detección de sistemas inestables y el óptimo
del análisis de costos.

## Rutas

| Ruta | Descripción |
|------|-------------|
| `/` | Inicio. Breve descripción de los modelos y sus supuestos. |
| `/mm1/` | Modelo M/M/1: formulario, indicadores, distribución Pn y desarrollo paso a paso. |
| `/mms/` | Modelo M/M/s: igual que M/M/1 más la probabilidad de esperar (Erlang C). |
| `/costos/` | Análisis de costos. Tabla comparativa por número de servidores y gráfica CS/CE/CT. |

Cada página de modelo tiene un botón **Cargar ejemplo** que llena el formulario con el
caso de referencia descrito encima.

## Ejemplos base

- **M/M/1 — Droguería:** λ = 10/h, μ = 12/h.
- **M/M/s — Banco:** λ = 20/h, μ = 8/h, s = 3.
- **Costos — Banco:** mismos λ y μ, Cs = 15.000 COP/h, Cw = 20.000 COP/h, s de 3 a 6.
  Óptimo esperado: s = 4 con CT ≈ 120.662 COP/h.

## Estructura del proyecto

```
.
├── manage.py
├── requirements.txt
├── colas/                        # proyecto Django (settings, urls, wsgi)
└── calculadora/                  # app principal
    ├── modelos_colas.py          # motor de cálculo (funciones puras)
    ├── desarrollo.py             # pasos con sustitución numérica
    ├── interpretacion.py         # textos interpretativos
    ├── graficos.py               # gráfica de costos en SVG
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── tests.py
    ├── templatetags/formato.py   # filtros de formato numérico es-CO
    ├── templates/calculadora/
    └── static/css/estilos.css
```
