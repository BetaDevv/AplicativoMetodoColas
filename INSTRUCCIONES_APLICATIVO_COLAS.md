# Aplicativo de Teoría de Colas (M/M/1 y M/M/s) — Especificación para Claude Code

## 1. Contexto

Trabajo final de **Investigación de Operaciones** (ITM, Ingeniería de Sistemas). La línea asignada es **Teoría de Colas (Sistemas de Espera)**: un calculador de parámetros de desempeño para modelos M/M/1 y M/M/s que permita analizar **costo de servicio vs. costo de espera**.

Requisitos de la consigna que el aplicativo debe cumplir sí o sí:

- **Interfaz de usuario:** entrada de datos clara (tasas, número de servidores, costos).
- **Motor de cálculo:** fórmulas de M/M/1 y M/M/s implementadas correctamente.
- **Salida de resultados:** indicadores de desempeño legibles.
- **Semiautomatización:** el usuario cambia los datos y obtiene resultados nuevos sin tocar código.
- La evaluadora va a tomar el ejemplo base, **cambiar algún parámetro** y verificar que la respuesta sea coherente. El aplicativo tiene que facilitar exactamente eso.

## 2. Principios de diseño (importante)

- **Simple.** Django con plantillas renderizadas en el servidor. Nada de React, Vue, HTMX ni frameworks JS. Cero o casi cero JavaScript.
- **Que no parezca hecho por IA.** Esto aplica a la interfaz, al código y a los textos:
  - Sin emojis, sin degradados, sin tarjetas con sombras exageradas, sin íconos decorativos, sin frases tipo "¡Optimiza tu sistema con potentes cálculos!".
  - Aspecto de herramienta académica sobria: tipografía del sistema, tablas con bordes simples, un solo color de acento (por ejemplo azul oscuro), fondo blanco.
  - Textos de la interfaz cortos, en español neutro y técnico, como los escribiría un estudiante de ingeniería.
  - Código con nombres en español coherentes con la notación del curso (`lam`, `mu`, `s`, `rho`, `p0`, `lq`, `l`, `wq`, `w`). Comentarios breves y solo donde aporten (por ejemplo, citar la fórmula). No comentar lo obvio, no docstrings larguísimos, no "# Paso 1: ...".
  - No sobre-ingenierizar: sin capas de servicios, repositorios, DTOs ni patrones innecesarios. Una app de Django, un módulo de cálculo, unas pocas vistas.
- **Sin base de datos de negocio.** No hace falta guardar nada. SQLite queda solo porque Django lo trae por defecto (o se desactiva). No usar el admin.

## 3. Stack

- Python 3.11+ y Django 5.x.
- `matplotlib` para las gráficas, generadas en el servidor como SVG y embebidas en la plantilla. Si se prefiere evitar dependencias, las barras de probabilidades se pueden dibujar con HTML/CSS (divs con ancho proporcional).
- CSS propio en un único archivo `static/css/estilos.css` (corto, menos de 150 líneas). Sin Bootstrap ni Tailwind.
- `requirements.txt` con lo mínimo: `Django`, `matplotlib`.

Estructura sugerida:

```
colas/
├── manage.py
├── requirements.txt
├── README.md
├── colas/              # proyecto (settings, urls)
└── calculadora/        # app
    ├── modelos_colas.py   # motor de cálculo puro, sin Django
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── tests.py
    ├── templates/calculadora/
    │   ├── base.html
    │   ├── inicio.html
    │   ├── mm1.html
    │   ├── mms.html
    │   └── costos.html
    └── static/css/estilos.css
```

## 4. Motor de cálculo (`modelos_colas.py`)

Funciones puras, sin dependencia de Django, para poder probarlas aisladas. Usar `math.factorial`. Devolver diccionarios o `dataclass` simples.

Notación: λ = tasa de llegada, μ = tasa de servicio por servidor, s = número de servidores. λ y μ deben estar en la **misma unidad de tiempo** (por ejemplo clientes/hora).

### 4.1 M/M/1

- ρ = λ / μ
- P0 = 1 − ρ
- Pn = (1 − ρ) ρⁿ
- L = λ / (μ − λ)
- Lq = λ² / (μ (μ − λ))
- W = 1 / (μ − λ)
- Wq = λ / (μ (μ − λ))
- Probabilidad de que un cliente espere: Pw = ρ

### 4.2 M/M/s

- a = λ / μ, ρ = λ / (s μ)
- P0 = [ Σₙ₌₀^{s−1} aⁿ / n! + aˢ / (s! (1 − ρ)) ]⁻¹
- Pn = (aⁿ / n!) P0 si n ≤ s; Pn = aⁿ / (s! sⁿ⁻ˢ) P0 si n > s
- Lq = P0 aˢ ρ / (s! (1 − ρ)²)
- L = Lq + a
- Wq = Lq / λ
- W = Wq + 1/μ
- Probabilidad de esperar (Erlang C): Pw = aˢ P0 / (s! (1 − ρ))

Con s = 1, M/M/s debe dar exactamente lo mismo que M/M/1 (agregar un test que lo verifique).

### 4.3 Costos

- Costo de servicio por unidad de tiempo: CS = Cs · s
- Costo de espera por unidad de tiempo: CE = Cw · L (opción por defecto) o Cw · Lq (si el usuario indica que solo cuesta el tiempo en cola)
- Costo total: CT = CS + CE
- Función que, dado λ, μ, Cs, Cw y un rango de s (desde el mínimo estable hasta un máximo que define el usuario), devuelva la tabla de costos y el **s óptimo** (mínimo CT).

### 4.4 Validaciones

- λ > 0, μ > 0, s entero ≥ 1, costos ≥ 0.
- **Condición de estabilidad:** ρ < 1 (λ < s μ). Si no se cumple, no calcular: mostrar un mensaje claro, por ejemplo: "El sistema no es estable: λ (20) es mayor o igual que s·μ (16). La cola crecería indefinidamente. Aumente el número de servidores o la tasa de servicio."
- En el análisis de costos, el s mínimo es el menor entero con s μ > λ (calcularlo automáticamente e informarlo).

## 5. Historias de usuario

Usuario principal: estudiante o docente de Investigación de Operaciones (y, en el ejemplo, el administrador de un negocio que debe decidir cuántos servidores poner).

**HU-01 — Elegir el modelo**
Como usuario quiero ver en la página de inicio una breve explicación de los modelos disponibles (M/M/1, M/M/s, análisis de costos) y sus supuestos (llegadas Poisson, servicio exponencial, disciplina FIFO, población y cola infinitas), para saber cuál usar.
- Criterio: la página de inicio tiene tres enlaces y un párrafo corto por modelo. Nada más.

**HU-02 — Calcular un M/M/1**
Como usuario quiero ingresar λ y μ y la unidad de tiempo, y obtener ρ, P0, L, Lq, W, Wq y Pw, para conocer el desempeño de un sistema con un solo servidor.
- Criterio: formulario en la misma página que los resultados (el formulario se mantiene lleno tras calcular, para que modificar un dato sea inmediato).
- Criterio: tiempos W y Wq mostrados en la unidad ingresada **y** convertidos a minutos (p. ej. "0,5 h = 30,0 min").

**HU-03 — Calcular un M/M/s**
Como usuario quiero ingresar λ, μ y s, y obtener los mismos indicadores más la probabilidad de esperar (Erlang C).
- Mismos criterios que HU-02.

**HU-04 — Ver el procedimiento**
Como estudiante quiero ver el desarrollo paso a paso con las fórmulas y los valores reemplazados, para verificar el cálculo a mano y para usarlo en la guía.
- Criterio: sección "Desarrollo" debajo de los resultados, con cada fórmula, la sustitución numérica y el resultado. Ejemplo: `L = λ / (μ − λ) = 10 / (12 − 10) = 5,0000 clientes`.
- Puede ir dentro de un `<details>` para no saturar la pantalla.

**HU-05 — Distribución de probabilidades**
Como usuario quiero ver la tabla de Pn para n = 0 … N (N configurable, por defecto 10) con la probabilidad acumulada, y una gráfica de barras, para entender cuántos clientes suele haber en el sistema.

**HU-06 — Comparar costo de servicio vs. costo de espera**
Como administrador quiero ingresar λ, μ, el costo por servidor por unidad de tiempo (Cs), el costo de espera por cliente por unidad de tiempo (Cw) y un número máximo de servidores a evaluar, para saber cuántos servidores minimizan el costo total.
- Criterio: tabla con una fila por cada s (desde el mínimo estable hasta el máximo): s, ρ, L, Lq, Wq (min), CS, CE, CT. La fila del s óptimo resaltada (fondo suave o negrita, sin colores chillones).
- Criterio: gráfica con tres líneas (CS, CE, CT) contra s, marcando el mínimo.
- Criterio: selector para indicar si el costo de espera se calcula sobre L (tiempo en el sistema) o sobre Lq (solo tiempo en cola).
- Criterio: moneda configurable en texto (por defecto COP) y valores con separador de miles.

**HU-07 — Interpretación de resultados**
Como usuario quiero un párrafo corto que interprete los resultados en lenguaje sencillo, para sustentar el análisis.
- Criterio: texto generado con plantillas fijas a partir de los números (sin APIs externas ni IA). Ejemplo: "Los servidores están ocupados el 83,3 % del tiempo. En promedio hay 5,0 clientes en el sistema y cada cliente permanece 30,0 minutos, de los cuales 25,0 son de espera."
- Reglas simples de advertencia: si ρ ≥ 0,85, indicar que el sistema está muy cargado y pequeñas variaciones en λ disparan la espera; si ρ < 0,3, indicar que hay capacidad ociosa.
- En costos: "La opción de menor costo total es s = 4, con CT = 120.662 COP/h. Pasar de 3 a 4 servidores reduce la espera promedio de 10,5 a 1,6 minutos."

**HU-08 — Cargar el ejemplo base y modificarlo**
Como evaluadora quiero un botón "Cargar ejemplo" que llene el formulario con el caso de la guía, para luego cambiar un parámetro y validar que el resultado sea coherente.
- Criterio: botón (enlace GET con parámetros, o `?ejemplo=1`) en cada página de modelo.
- Criterio: el ejemplo de cada página trae su enunciado corto encima del formulario.

**HU-09 — Comparar con el escenario anterior** (opcional, solo si sale simple)
Como usuario quiero ver, después de cambiar un dato, los resultados anteriores junto a los nuevos, para observar el efecto del cambio.
- Implementación sencilla: guardar el último resultado en la sesión de Django y mostrar una columna "Anterior" y "Diferencia" en la tabla de indicadores.

**HU-10 — Errores claros**
Como usuario quiero mensajes de error en español junto al campo incorrecto (valor negativo, vacío, s no entero, sistema inestable), para corregir sin adivinar.

## 6. Flujo de pantallas

1. **Inicio** (`/`): título del aplicativo, curso, breve descripción de los modelos y tres enlaces.
2. **M/M/1** (`/mm1/`): enunciado del ejemplo, formulario, botón Calcular y botón Cargar ejemplo. Al calcular, en la misma página: tabla de indicadores, interpretación, tabla y gráfica de Pn, desarrollo paso a paso.
3. **M/M/s** (`/mms/`): igual que M/M/1 con el campo s.
4. **Costos** (`/costos/`): formulario con λ, μ, Cs, Cw, s máximo, base de costo (L o Lq), moneda. Resultados: s mínimo estable, tabla comparativa, gráfica, recomendación.

Navegación: barra superior simple con texto (Inicio · M/M/1 · M/M/s · Costos). Formularios con método POST y CSRF. Formato numérico con 4 decimales en indicadores y coma decimal (configurar `USE_L10N`/`LANGUAGE_CODE = "es-co"` o formatear manualmente).

## 7. Ejemplos base (deben venir precargados con "Cargar ejemplo")

### 7.1 M/M/1 — Caja de una droguería
A una droguería con una sola caja llegan en promedio 10 clientes por hora (Poisson) y el cajero atiende en promedio 12 clientes por hora (exponencial).

Resultados esperados: ρ = 0,8333; P0 = 0,1667; L = 5,0000; Lq = 4,1667; W = 0,5 h (30 min); Wq = 0,4167 h (25 min).

### 7.2 M/M/s — Taquillas de un banco
A una sucursal llegan 20 clientes por hora; cada asesor atiende 8 clientes por hora; hay 3 asesores.

Resultados esperados (s = 3): ρ = 0,8333; P0 = 0,0449; Lq = 3,5112; L = 6,0112; Wq = 10,53 min; W = 18,03 min; Pw = 0,7022.

### 7.3 Costos — ¿Cuántos asesores contratar?
Mismo banco (λ = 20/h, μ = 8/h). Cada asesor cuesta 15.000 COP/h y cada hora que un cliente permanece en el sistema se valora en 20.000 COP. Evaluar de s = 3 (mínimo estable) a s = 6, con costo de espera sobre L.

| s | ρ | L | Wq (min) | CT (COP/h) |
|---|---|---|---|---|
| 3 | 0,8333 | 6,0112 | 10,53 | 165.225 |
| 4 | 0,6250 | 3,0331 | 1,60 | **120.662** |
| 5 | 0,5000 | 2,6304 | 0,39 | 127.607 |
| 6 | 0,4167 | 2,5339 | 0,10 | 140.678 |

Óptimo: **s = 4**.

Estos valores son la referencia para los tests y para la guía de usuario.

## 8. Pruebas (`tests.py`)

- Tests del motor con los valores de la sección 7 (tolerancia 1e-3).
- M/M/s con s = 1 igual a M/M/1.
- Suma de Pn para n grande ≈ 1.
- Ley de Little: L = λW y Lq = λWq.
- Sistema inestable lanza error / devuelve mensaje, no calcula.
- Costos: el óptimo del ejemplo 7.3 es s = 4.
- Un test por vista que verifique que responde 200 y que con datos inválidos muestra el error.

## 9. README.md del proyecto

Corto: requisitos, cómo instalar (`python -m venv`, `pip install -r requirements.txt`), cómo correr (`python manage.py runserver`), cómo correr tests y una tabla con las rutas. Sin badges ni emojis.

## 10. Lo que NO hay que hacer

- No usar React, ni SPA, ni APIs REST, ni Django REST Framework.
- No agregar login, usuarios, base de datos de escenarios ni panel de administración.
- No llamar a ninguna API de IA para generar textos.
- No agregar animaciones, modo oscuro, landing page de marketing ni ilustraciones.
- No incluir modelos fuera del alcance (M/M/1/K, M/G/1, simulación de eventos) salvo que se pida después.

## 11. Orden de trabajo sugerido

1. Crear proyecto y app, `modelos_colas.py` con sus tests y verificar los valores de la sección 7.
2. Vistas y plantillas de M/M/1 y M/M/s con formulario, resultados, interpretación y desarrollo.
3. Tabla y gráfica de Pn.
4. Página de costos con tabla, gráfica y recomendación.
5. Botones "Cargar ejemplo", mensajes de error y (si queda simple) comparación con el escenario anterior.
6. README y revisión final de textos para que suenen naturales y sin relleno.
