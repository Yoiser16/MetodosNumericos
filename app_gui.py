"""
INTERFAZ GRÁFICA - MÉTODOS NUMÉRICOS
=====================================
Interfaz moderna con tkinter para los métodos numéricos del curso.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import math
import re
import sys
import os
import time
import urllib.error
import urllib.request

try:
    import pandas as pd
    PANDAS_DISPONIBLE = True
except Exception:
    PANDAS_DISPONIBLE = False

try:
    import numpy as np
    import matplotlib.pyplot as plt
    MATPLOTLIB_DISPONIBLE = True
except Exception:
    MATPLOTLIB_DISPONIBLE = False

# Importar la clase con los métodos numéricos
sys.path.insert(0, os.path.dirname(__file__))
from metodos_numericos import MetodosNumericos

# ─────────────────────────── PALETAS DE COLORES ──────────────────────────
TEMAS = {
    "dark": {
        "BG":         "#1e1e2e",
        "SIDEBAR_BG": "#181825",
        "CARD_BG":    "#313244",
        "SURFACE":    "#45475a",
        "TEXT":       "#cdd6f4",
        "SUBTEXT":    "#a6adc8",
        "ACCENT":     "#89b4fa",
        "ACCENT2":    "#cba6f7",
        "GREEN":      "#a6e3a1",
        "RED":        "#f38ba8",
        "YELLOW":     "#f9e2af",
        "BTN_HOVER":  "#7aa2f7",
        "ICONO":      "☀️  Modo claro",
    },
    "light": {
        "BG":         "#eff1f5",
        "SIDEBAR_BG": "#dce0e8",
        "CARD_BG":    "#ccd0da",
        "SURFACE":    "#bcc0cc",
        "TEXT":       "#4c4f69",
        "SUBTEXT":    "#6c6f85",
        "ACCENT":     "#1e66f5",
        "ACCENT2":    "#8839ef",
        "GREEN":      "#40a02b",
        "RED":        "#d20f39",
        "YELLOW":     "#df8e1d",
        "BTN_HOVER":  "#04a5e5",
        "ICONO":      "🌙  Modo oscuro",
    },
}

# Variables globales de tema (inicialmente dark)
T = dict(TEMAS["dark"])
BG         = T["BG"]
SIDEBAR_BG = T["SIDEBAR_BG"]
CARD_BG    = T["CARD_BG"]
SURFACE    = T["SURFACE"]
TEXT       = T["TEXT"]
SUBTEXT    = T["SUBTEXT"]
ACCENT     = T["ACCENT"]
ACCENT2    = T["ACCENT2"]
GREEN      = T["GREEN"]
RED        = T["RED"]
YELLOW     = T["YELLOW"]
BTN_HOVER  = T["BTN_HOVER"]


mn = MetodosNumericos()

# ─────────────────────── CARGA DE .env ──────────────────────────────────────
_ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
_LAST_CALCS_FILE = os.path.join(os.path.dirname(__file__), "ultimos_calculos.json")

def _cargar_env():
    """Lee el archivo .env del proyecto y carga las variables en os.environ."""
    if not os.path.isfile(_ENV_FILE):
        return
    with open(_ENV_FILE, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            clave = clave.strip()
            valor = valor.strip().strip('"').strip("'")
            if clave and clave not in os.environ:   # no sobreescribe si ya existe
                os.environ[clave] = valor

_cargar_env()

def _guardar_env(datos: dict):
    """Guarda claves en el archivo .env (crea o actualiza)."""
    actual = {}
    if os.path.isfile(_ENV_FILE):
        with open(_ENV_FILE, encoding="utf-8") as fh:
            for linea in fh:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                k, _, v = linea.partition("=")
                actual[k.strip()] = v.strip().strip('"').strip("'")
    actual.update({k: v for k, v in datos.items() if v is not None})
    with open(_ENV_FILE, "w", encoding="utf-8") as fh:
        fh.write("# Configuración IA – Métodos Numéricos\n")
        for k, v in actual.items():
            fh.write(f'{k}="{v}"\n')
    # Aplicar inmediatamente en el proceso actual
    for k, v in datos.items():
        if v is not None:
            os.environ[k] = v


def _cargar_ultimos_calculos() -> dict:
    """Carga el historial de últimos cálculos por método."""
    if not os.path.isfile(_LAST_CALCS_FILE):
        return {}
    try:
        with open(_LAST_CALCS_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _serializar_json(valor):
    """Convierte datos complejos en valores serializables para JSON."""
    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor
    if isinstance(valor, dict):
        return {str(k): _serializar_json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_serializar_json(v) for v in valor]
    return str(valor)


def _guardar_ultimos_calculos(data: dict):
    """Guarda el historial de últimos cálculos por método."""
    with open(_LAST_CALCS_FILE, "w", encoding="utf-8") as fh:
        json.dump(_serializar_json(data), fh, ensure_ascii=False, indent=2)


def math_env(**kwargs):
    """Entorno seguro para eval con funciones matemáticas disponibles."""
    env = vars(math).copy()
    env["math"] = math
    env.update({
        "sen": math.sin,
        "tg": math.tan,
        "ln": math.log,
        "raiz": math.sqrt,
        "arcsen": math.asin,
        "arctg": math.atan,
    })
    env.update(kwargs)
    return env


def normalizar_expresion(expr: str) -> str:
    """Acepta alias y símbolos comunes escritos por estudiantes."""
    texto = (expr or "").strip()
    if not texto:
        return texto

    reemplazos = {
        "√(": "sqrt(",
        "√": "sqrt",
        "^": "**",
        "π": "pi",
        "²": "**2",
        "³": "**3",
    }
    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    aliases = {
        r"\bsen\b": "sin",
        r"\btg\b": "tan",
        r"\bln\b": "log",
        r"\braiz\b": "sqrt",
        r"\barcsen\b": "asin",
        r"\barctg\b": "atan",
    }
    for patron, reemplazo in aliases.items():
        texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE)

    return texto


def eval_num(texto: str) -> float:
    """Evalúa una expresión numérica (acepta pi, math.pi, 2*pi, etc.)."""
    return float(eval(normalizar_expresion(texto), math_env()))


def eval_func(expr: str):
    """Retorna un lambda f(x) evaluando la expresión."""
    expr_normalizada = normalizar_expresion(expr)
    return lambda x: eval(expr_normalizada, math_env(x=x))


def eval_func2(expr: str):
    """Retorna un lambda f(x, y) evaluando la expresión."""
    expr_normalizada = normalizar_expresion(expr)
    return lambda x, y: eval(expr_normalizada, math_env(x=x, y=y))


def sugerir_sintaxis_local(expr: str, variables=("x",)):
    """Fallback local para corregir expresiones matemáticas comunes."""
    original = (expr or "").strip()
    if not original:
        return []

    sugerencias = []
    propuesta = original

    reemplazos = {
        "sen(": "sin(",
        "tg(": "tan(",
        "ln(": "log(",
        "√(": "sqrt(",
        "^": "**",
    }

    for viejo, nuevo in reemplazos.items():
        if viejo in propuesta:
            propuesta = propuesta.replace(viejo, nuevo)

    if "=" in propuesta and "==" not in propuesta:
        sugerencias.append("Escribe solo la expresión, no una ecuación completa. Ejemplo: x**2 - 4")

    # Inserta multiplicación implícita en casos frecuentes
    propuesta = re.sub(r"(\d)([A-Za-z(])", r"\1*\2", propuesta)
    propuesta = re.sub(r"(\))([A-Za-z0-9(])", r"\1*\2", propuesta)
    propuesta = re.sub(r"([A-Za-z])\(", r"\1*(", propuesta)

    funciones = ("sin", "cos", "tan", "exp", "log", "sqrt")
    for fn in funciones:
        propuesta = propuesta.replace(f"{fn}*(", f"{fn}(")

    if propuesta != original:
        sugerencias.append(f"Prueba escribirla así: {propuesta}")

    if "^" in original:
        sugerencias.append("Para potencias usa ** en lugar de ^. Ejemplo: x**2")
    if "sen(" in original:
        sugerencias.append("Usa sin(x) en lugar de sen(x)")
    if re.search(r"\d+[A-Za-z]", original):
        sugerencias.append("Parece que falta un *. Ejemplo: 2*x en lugar de 2x")
    if any(var + "(" in original for var in variables):
        sugerencias.append("Parece que falta un * antes del paréntesis. Ejemplo: x*(x+1)")

    # eliminar duplicados preservando orden
    vistas = set()
    unicas = []
    for item in sugerencias:
        if item not in vistas:
            vistas.add(item)
            unicas.append(item)
    return unicas


def _consultar_modelo_json(system_prompt: str, user_prompt: str):
    """Realiza una consulta JSON a un endpoint compatible con OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("IA_API_KEY")
    if not api_key:
        return None, "Configura OPENAI_API_KEY o IA_API_KEY para habilitar sugerencias con IA."

    api_url = os.getenv("OPENAI_API_URL") or os.getenv("IA_API_URL") or "https://api.openai.com/v1/chat/completions"
    model = os.getenv("OPENAI_MODEL") or os.getenv("IA_MODEL") or "gpt-5.4"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "MetodosNumericos/1.0 (Python)",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        data = json.loads(content)
        data["model"] = model
        return data, None
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="ignore")
        return None, f"La API respondió con error HTTP {exc.code}. {detalle[:180]}"
    except Exception as exc:
        return None, f"No fue posible consultar la IA: {exc}"


def consultar_ia_sintaxis(expr: str, detalle_error: str, variables=("x",)):
    """Consulta un modelo por API para sugerir una corrección de sintaxis."""
    prompt = (
        "Eres un asistente experto en sintaxis matemática para estudiantes de métodos numéricos. "
        "Debes corregir expresiones escritas por usuarios en Python matemático. "
        "Responde en JSON con las claves suggestion y explanation. "
        "La sugerencia debe ser una única expresión válida y breve. "
        "Variables permitidas: " + ", ".join(variables) + ". "
        f"Expresión original: {expr}. "
        f"Error detectado: {detalle_error}."
    )
    data, error = _consultar_modelo_json(
        "Corrige expresiones matemáticas para Python y responde solo JSON válido.",
        prompt,
    )
    if error:
        return None, error

    try:
        suggestion = str(data.get("suggestion", "")).strip()
        explanation = str(data.get("explanation", "")).strip()
        if suggestion:
            return {
                "suggestion": suggestion,
                "explanation": explanation or "La IA encontró una forma válida de escribir la expresión.",
                "model": data.get("model", "desconocido"),
            }, None
        return None, "La IA no devolvió una sugerencia utilizable."
    except Exception as exc:
        return None, f"No fue posible consultar la IA: {exc}"


def consultar_ia_contexto(detalle_error: str, contexto: str = "", datos=None):
    """Pide a la IA una explicación y una acción sugerida para cualquier error del sistema."""
    datos_txt = json.dumps(datos or {}, ensure_ascii=False)
    prompt = (
        "Eres un asistente para una app de métodos numéricos. "
        "Debes ayudar al estudiante a entender el error y qué corregir. "
        "Responde en JSON con las claves suggestion y explanation. "
        "La sugerencia debe ser una acción concreta y breve. "
        f"Contexto: {contexto or 'general'}. "
        f"Detalle del error: {detalle_error}. "
        f"Datos adicionales: {datos_txt}."
    )
    data, error = _consultar_modelo_json(
        "Explica errores de métodos numéricos y responde solo JSON válido.",
        prompt,
    )
    if error:
        return None, error

    suggestion = str(data.get("suggestion", "")).strip()
    explanation = str(data.get("explanation", "")).strip()
    if suggestion or explanation:
        return {
            "suggestion": suggestion or "Revisa los datos de entrada y vuelve a intentar.",
            "explanation": explanation or "La IA detectó que hace falta corregir la entrada antes de continuar.",
            "model": data.get("model", "desconocido"),
        }, None
    return None, "La IA no devolvió una orientación utilizable."


# ═══════════════════════════════════════════════════════════════════════════
#                           CLASE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Métodos Numéricos")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self._tema_actual = "dark"
        self._panel_actual = None
        self._metodo_actual = None
        self._btn_activo   = None
        self._widgets_tema = []   # lista de (widget, {prop: clave_tema})
        self._cache_ia = {}
        self._ultimos_calculos = _cargar_ultimos_calculos()
        self.configure(bg=T["BG"])
        self._build_ui()
        self._mostrar_inicio()

    # ──────────────────────────── CONSTRUCCIÓN UI ────────────────────────────

    def _build_ui(self):
        # ── Sidebar ──────────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=T["SIDEBAR_BG"], width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / título
        logo_frame = tk.Frame(self.sidebar, bg=T["SIDEBAR_BG"], pady=20)
        logo_frame.pack(fill="x")
        lbl1 = tk.Label(logo_frame, text="∑ Métodos", font=("Segoe UI", 16, "bold"),
             bg=T["SIDEBAR_BG"], fg=T["ACCENT"])
        lbl1.pack()
        lbl2 = tk.Label(logo_frame, text="Numéricos", font=("Segoe UI", 16, "bold"),
             bg=T["SIDEBAR_BG"], fg=T["ACCENT"])
        lbl2.pack()
        self._reg(lbl1, bg="SIDEBAR_BG", fg="ACCENT")
        self._reg(lbl2, bg="SIDEBAR_BG", fg="ACCENT")
        self._reg(logo_frame, bg="SIDEBAR_BG")
        sep0 = tk.Frame(self.sidebar, bg=T["SURFACE"], height=1)
        sep0.pack(fill="x", padx=15)
        self._reg(sep0, bg="SURFACE")
        self._reg(self.sidebar, bg="SIDEBAR_BG")

        # Área contenido principal
        self.main = tk.Frame(self, bg=T["BG"])
        self.main.pack(side="left", fill="both", expand=True)
        self._reg(self.main, bg="BG")
        self._reg(self, bg="BG")

        # ── Menú lateral ─────────────────────────────────────────────────────
        categorias = [
            ("🏠  Inicio",              None),
            ("",                        None),   # separador visual
            ("📐  Raíces",              [
                ("Bisección",           self._panel_biseccion),
                ("Newton-Raphson",      self._panel_newton),
                ("Secante",             self._panel_secante),
                ("Falsa Posición",      self._panel_falsa_posicion),
            ]),
            ("📊  Interpolación",       [
                ("Lagrange",            self._panel_lagrange),
                ("Newton Divididas",    self._panel_newton_interp),
            ]),
            ("∫  Integración",         [
                ("Trapecio",            self._panel_trapecio),
                ("Simpson 1/3",         self._panel_simpson13),
                ("Simpson 3/8",         self._panel_simpson38),
            ]),
            ("🔢  Sistemas Lineales",   [
                ("Gauss Eliminación",   self._panel_gauss),
                ("Gauss-Seidel",        self._panel_gauss_seidel),
            ]),
            ("Δ  Derivación",          [
                ("Dif. Progresiva",     self._panel_dif_prog),
                ("Dif. Regresiva",      self._panel_dif_reg),
                ("Dif. Central",        self._panel_dif_central),
            ]),
            ("〜  Ec. Diferenciales",  [
                ("Euler",               self._panel_euler),
                ("Runge-Kutta 4",       self._panel_rk4),
            ]),
        ]

        self._btns_sub = {}

        for cat in categorias:
            nombre, hijos = cat
            if nombre == "":
                sep = tk.Frame(self.sidebar, bg=T["SURFACE"], height=1)
                sep.pack(fill="x", padx=15, pady=4)
                self._reg(sep, bg="SURFACE")
                continue

            if hijos is None:
                # Botón simple (Inicio)
                btn = tk.Button(
                    self.sidebar, text=nombre,
                    font=("Segoe UI", 10, "bold"),
                    bg=T["SIDEBAR_BG"], fg=T["TEXT"], bd=0, cursor="hand2",
                    activebackground=T["CARD_BG"], activeforeground=T["ACCENT"],
                    anchor="w", padx=18, pady=8,
                    command=self._mostrar_inicio
                )
                btn.pack(fill="x")
                self._agregar_hover(btn)
                self._reg(btn, bg="SIDEBAR_BG", fg="TEXT",
                          activebackground="CARD_BG", activeforeground="ACCENT")
            else:
                # Categoría colapsable
                cat_frame = tk.Frame(self.sidebar, bg=T["SIDEBAR_BG"])
                cat_frame.pack(fill="x")
                self._reg(cat_frame, bg="SIDEBAR_BG")

                # Sub-frame con ítems (oculto por defecto)
                sub_frame = tk.Frame(self.sidebar, bg=T["SIDEBAR_BG"])
                self._reg(sub_frame, bg="SIDEBAR_BG")

                def toggle(sf=sub_frame):
                    if sf.winfo_ismapped():
                        sf.pack_forget()
                    else:
                        sf.pack(fill="x")

                cat_btn = tk.Button(
                    cat_frame, text=nombre,
                    font=("Segoe UI", 10, "bold"),
                    bg=T["SIDEBAR_BG"], fg=T["ACCENT2"], bd=0, cursor="hand2",
                    activebackground=T["CARD_BG"], activeforeground=T["ACCENT2"],
                    anchor="w", padx=18, pady=8,
                    command=toggle
                )
                cat_btn.pack(fill="x")
                self._agregar_hover(cat_btn, hover_fg=T["ACCENT2"])
                self._reg(cat_btn, bg="SIDEBAR_BG", fg="ACCENT2",
                          activebackground="CARD_BG", activeforeground="ACCENT2")

                for nombre_sub, fn in hijos:
                    b = tk.Button(
                        sub_frame, text=f"   {nombre_sub}",
                        font=("Segoe UI", 9),
                        bg=T["SIDEBAR_BG"], fg=T["SUBTEXT"], bd=0, cursor="hand2",
                        activebackground=T["CARD_BG"], activeforeground=T["ACCENT"],
                        anchor="w", padx=28, pady=5,
                        command=fn
                    )
                    b.pack(fill="x")
                    self._agregar_hover(b)
                    self._btns_sub[nombre_sub] = b
                    self._reg(b, bg="SIDEBAR_BG", fg="SUBTEXT",
                              activebackground="CARD_BG", activeforeground="ACCENT")

        # ── Botones inferiores del sidebar ───────────────────────────────────
        tk.Frame(self.sidebar, bg=T["SURFACE"], height=1).pack(fill="x", padx=15, pady=8, side="bottom")

        self._btn_tema = tk.Button(
            self.sidebar, text=T["ICONO"],
            font=("Segoe UI", 9), bd=0, cursor="hand2",
            bg=T["SIDEBAR_BG"], fg=T["SUBTEXT"],
            activebackground=T["CARD_BG"], activeforeground=T["ACCENT"],
            anchor="w", padx=18, pady=8,
            command=self._toggle_tema
        )
        self._btn_tema.pack(fill="x", side="bottom")
        self._reg(self._btn_tema, bg="SIDEBAR_BG", fg="SUBTEXT",
                  activebackground="CARD_BG", activeforeground="ACCENT")

        btn_ia = tk.Button(
            self.sidebar, text="🤖  Configurar IA",
            font=("Segoe UI", 9), bd=0, cursor="hand2",
            bg=T["SIDEBAR_BG"], fg=T["SUBTEXT"],
            activebackground=T["CARD_BG"], activeforeground=T["ACCENT2"],
            anchor="w", padx=18, pady=8,
            command=lambda: self._cambiar_panel(self._panel_config_ia)
        )
        btn_ia.pack(fill="x", side="bottom")
        self._reg(btn_ia, bg="SIDEBAR_BG", fg="SUBTEXT",
                  activebackground="CARD_BG", activeforeground="ACCENT2")

    # ──────────────────────── TEMADO ─────────────────────────────────────────

    def _reg(self, widget, **props):
        """Registra un widget para ser repintado al cambiar de tema (no-op: se reconstruye)."""
        pass

    def _toggle_tema(self):
        global T, BG, SIDEBAR_BG, CARD_BG, SURFACE, TEXT, SUBTEXT
        global ACCENT, ACCENT2, GREEN, RED, YELLOW, BTN_HOVER
        self._tema_actual = "light" if self._tema_actual == "dark" else "dark"
        nuevo = TEMAS[self._tema_actual]
        T.update(nuevo)
        # Actualizar globales para que default-args y lambdas capturados
        # en la nueva construcción tomen los valores correctos
        BG         = T["BG"]
        SIDEBAR_BG = T["SIDEBAR_BG"]
        CARD_BG    = T["CARD_BG"]
        SURFACE    = T["SURFACE"]
        TEXT       = T["TEXT"]
        SUBTEXT    = T["SUBTEXT"]
        ACCENT     = T["ACCENT"]
        ACCENT2    = T["ACCENT2"]
        GREEN      = T["GREEN"]
        RED        = T["RED"]
        YELLOW     = T["YELLOW"]
        BTN_HOVER  = T["BTN_HOVER"]
        # Reconstruir toda la interfaz
        self.configure(bg=T["BG"])
        for w in self.winfo_children():
            w.destroy()
        self._panel_actual = None
        self._btn_activo   = None
        self._widgets_tema = []
        self._build_ui()
        self._mostrar_inicio()

    def _agregar_hover(self, btn, hover_fg=ACCENT):
        fg_hover = hover_fg  # captura el valor actual en el cierre
        btn.bind("<Enter>", lambda e, b=btn, fg=fg_hover: b.config(bg=T["CARD_BG"], fg=fg))
        btn.bind("<Leave>", lambda e, b=btn: b.config(
            bg=T["SIDEBAR_BG"],
            fg=T["SUBTEXT"] if b.cget("font") == ("Segoe UI", 9) else b.cget("fg")
        ))

    # ──────────────────────── GESTIÓN DE PANELES ─────────────────────────────

    def _cambiar_panel(self, nuevo_panel_fn, nombre_btn=None):
        if self._panel_actual:
            self._panel_actual.destroy()
        frame = tk.Frame(self.main, bg=T["BG"])
        frame.pack(fill="both", expand=True)
        nuevo_panel_fn(frame)
        self._panel_actual = frame
        self._metodo_actual = nombre_btn

        if self._btn_activo and self._btn_activo in self._btns_sub.values():
            self._btn_activo.config(fg=T["SUBTEXT"])
        if nombre_btn and nombre_btn in self._btns_sub:
            self._btns_sub[nombre_btn].config(fg=T["ACCENT"])
            self._btn_activo = self._btns_sub[nombre_btn]

    def _mostrar_inicio(self):
        if self._panel_actual:
            self._panel_actual.destroy()
        frame = tk.Frame(self.main, bg=T["BG"])
        frame.pack(fill="both", expand=True)
        self._panel_actual = frame
        self._metodo_actual = None

        center = tk.Frame(frame, bg=T["BG"])
        center.place(relx=0.5, rely=0.42, anchor="center")

        tk.Label(center, text="∑", font=("Segoe UI", 60), bg=T["BG"], fg=T["ACCENT"]).pack()
        tk.Label(center, text="Métodos Numéricos",
                 font=("Segoe UI", 22, "bold"), bg=T["BG"], fg=T["TEXT"]).pack(pady=(0, 6))
        tk.Label(center,
                 text="Selecciona un método del menú lateral para comenzar.",
                 font=("Segoe UI", 11), bg=T["BG"], fg=T["SUBTEXT"]).pack()

        # Tarjetas resumen
        grid = tk.Frame(center, bg=T["BG"])
        grid.pack(pady=30)
        tarjetas = [
            ("📐", "Raíces",        "Bisección · Newton · Secante · Falsa Pos."),
            ("📊", "Interpolación", "Lagrange · Newton Divididas"),
            ("∫",  "Integración",   "Trapecio · Simpson 1/3 · Simpson 3/8"),
            ("Δ",  "Derivación",    "Progresiva · Regresiva · Central"),
            ("🔢", "Sistemas",      "Elim. Gaussiana · Gauss-Seidel"),
            ("〜", "EDO",           "Euler · Runge-Kutta 4"),
        ]
        for i, (ico, titulo, desc) in enumerate(tarjetas):
            c = tk.Frame(grid, bg=T["CARD_BG"], padx=16, pady=12, relief="flat")
            c.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")
            tk.Label(c, text=ico, font=("Segoe UI", 18), bg=T["CARD_BG"], fg=T["ACCENT"]).pack()
            tk.Label(c, text=titulo, font=("Segoe UI", 10, "bold"),
                     bg=T["CARD_BG"], fg=T["TEXT"]).pack()
            tk.Label(c, text=desc, font=("Segoe UI", 8),
                     bg=T["CARD_BG"], fg=T["SUBTEXT"], wraplength=160, justify="center").pack()

    # ─────────────────────── WIDGETS DE AYUDA ────────────────────────────────

    def _titulo(self, parent, texto, subtexto=""):
        tk.Label(parent, text=texto, font=("Segoe UI", 16, "bold"),
                 bg=T["BG"], fg=T["ACCENT"]).pack(anchor="w", padx=30, pady=(24, 0))
        if subtexto:
            tk.Label(parent, text=subtexto, font=("Segoe UI", 9),
                     bg=T["BG"], fg=T["SUBTEXT"]).pack(anchor="w", padx=30)
        tk.Frame(parent, bg=T["SURFACE"], height=1).pack(fill="x", padx=30, pady=8)

    def _campo(self, parent, label, valor_default="", ancho=30):
        row = tk.Frame(parent, bg=T["BG"])
        row.pack(anchor="w", padx=30, pady=3)
        tk.Label(row, text=label, font=("Segoe UI", 9), bg=T["BG"],
             fg=T["SUBTEXT"], width=26, anchor="w").pack(side="left")
        var = tk.StringVar(value=valor_default)
        entry = tk.Entry(row, textvariable=var, font=("Consolas", 10),
                 bg=T["CARD_BG"], fg=T["TEXT"], insertbackground=T["TEXT"],
                         relief="flat", bd=6, width=ancho)
        entry.pack(side="left")
        return var

    def _default_metodo(self, metodo: str, campo: str, fallback: str) -> str:
        """Devuelve el último valor guardado para un campo de un método."""
        metodo_data = self._ultimos_calculos.get(metodo, {})
        entradas = metodo_data.get("entradas", {}) if isinstance(metodo_data, dict) else {}
        valor = entradas.get(campo, fallback)
        return str(valor)

    def _guardar_calculo(self, metodo: str, entradas: dict, resultado: dict):
        """Persistencia del último cálculo por método."""
        self._ultimos_calculos[metodo] = {
            "entradas": {k: str(v) for k, v in entradas.items()},
            "resultado": _serializar_json(resultado),
            "timestamp": int(time.time()),
        }
        _guardar_ultimos_calculos(self._ultimos_calculos)

    def _boton_calcular(self, parent, comando):
        btn = tk.Button(
            parent, text="  Calcular  ", font=("Segoe UI", 10, "bold"),
            bg=T["ACCENT"], fg=T["BG"], relief="flat", cursor="hand2",
            activebackground=T["BTN_HOVER"], activeforeground=T["BG"],
            padx=20, pady=8, command=comando
        )
        btn.pack(anchor="w", padx=30, pady=(12, 8))

    def _rango_grafica(self, var_a=None, var_b=None, var_x0=None, var_x1=None):
        """Define un rango razonable para graficar según los campos disponibles."""
        try:
            if var_a is not None and var_b is not None:
                a = eval_num(var_a.get())
                b = eval_num(var_b.get())
                if a == b:
                    a, b = a - 1, b + 1
                if a > b:
                    a, b = b, a
                return a, b

            if var_x0 is not None and var_x1 is not None:
                x0 = eval_num(var_x0.get())
                x1 = eval_num(var_x1.get())
                m = (x0 + x1) / 2
                r = max(abs(x1 - x0), 1.0)
                return m - 2 * r, m + 2 * r

            if var_x0 is not None:
                x0 = eval_num(var_x0.get())
                return x0 - 5, x0 + 5
        except Exception:
            pass

        return -10, 10

    def _graficar_funcion(self, expr, a, b):
        if not MATPLOTLIB_DISPONIBLE:
            messagebox.showerror(
                "Matplotlib no disponible",
                "No se pudo importar matplotlib/numpy.\n"
                "Instala con: pip install matplotlib numpy"
            )
            return

        try:
            f = eval_func(expr)
            xs = np.linspace(a, b, 800)
            ys = []
            for x in xs:
                try:
                    y = f(float(x))
                    ys.append(float(y))
                except Exception:
                    ys.append(np.nan)

            plt.figure("Grafica de f(x)", figsize=(8, 4.8))
            plt.plot(xs, ys, color=T["ACCENT"], linewidth=2)
            plt.axhline(0, color=T["SUBTEXT"], linewidth=1)
            plt.axvline(0, color=T["SUBTEXT"], linewidth=1)
            plt.title(f"f(x) = {expr}")
            plt.xlabel("x")
            plt.ylabel("f(x)")
            plt.grid(True, alpha=0.25)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error al graficar", str(e))

    def _boton_graficar(self, parent, var_fx, var_a=None, var_b=None, var_x0=None, var_x1=None):
        def graficar():
            try:
                a, b = self._rango_grafica(var_a, var_b, var_x0, var_x1)
                self._graficar_funcion(var_fx.get(), a, b)
            except Exception as e:
                messagebox.showerror("Error al graficar", str(e))

        btn = tk.Button(
            parent, text="  Graficar f(x)  ", font=("Segoe UI", 10, "bold"),
            bg=T["ACCENT2"], fg=T["BG"], relief="flat", cursor="hand2",
            activebackground=T["BTN_HOVER"], activeforeground=T["BG"],
            padx=20, pady=8, command=graficar
        )
        btn.pack(anchor="w", padx=30, pady=(4, 4))

    def _area_resultado(self, parent):
        tk.Frame(parent, bg=T["SURFACE"], height=1).pack(fill="x", padx=30, pady=(6, 4))
        header = tk.Frame(parent, bg=T["BG"])
        header.pack(fill="x", padx=30)
        tk.Label(header, text="Resultados", font=("Segoe UI", 10, "bold"),
                 bg=T["BG"], fg=T["SUBTEXT"]).pack(side="left", anchor="w")

        txt = scrolledtext.ScrolledText(
            parent, font=("Consolas", 9),
            bg=T["CARD_BG"], fg=T["TEXT"], insertbackground=T["TEXT"],
            relief="flat", bd=0, padx=10, pady=10,
            state="disabled", wrap="word"
        )

        btn_exportar = tk.Button(
            header, text="Exportar DataFrame a Excel", font=("Segoe UI", 8, "bold"),
            bg=T["ACCENT2"], fg=T["BG"], relief="flat", cursor="hand2",
            activebackground=T["BTN_HOVER"], activeforeground=T["BG"],
            padx=10, pady=4,
            command=lambda t=txt: self._exportar_dataframe_excel(t)
        )
        btn_exportar.pack(side="right")
        txt.pack(fill="both", expand=True, padx=30, pady=(4, 20))
        txt.tag_config("titulo",      foreground=T["ACCENT"],  font=("Consolas", 9, "bold"))
        txt.tag_config("valor",       foreground=T["GREEN"])
        txt.tag_config("error",       foreground=T["RED"])
        txt.tag_config("advertencia", foreground=T["YELLOW"])
        txt.tag_config("cabecera",    foreground=T["ACCENT2"], font=("Consolas", 9, "bold"))
        txt.tag_config("normal",      foreground=T["TEXT"])
        txt._ultimo_dataframe = None
        txt._ultimo_resultado = None
        return txt

    def _exportar_dataframe_excel(self, txt):
        """Exporta a Excel el último resultado del panel, como DataFrame."""
        if not PANDAS_DISPONIBLE:
            messagebox.showerror(
                "Pandas no disponible",
                "Para exportar a Excel necesitas pandas instalado."
            )
            return

        filas = getattr(txt, "_ultimo_dataframe", None)
        resultado = getattr(txt, "_ultimo_resultado", None)
        if not filas and resultado is None:
            messagebox.showwarning(
                "Sin DataFrame",
                "Aún no hay resultados para exportar en este método."
            )
            return

        metodo = (self._metodo_actual or "resultado").strip().lower()
        nombre_sugerido = re.sub(r"\s+", "_", metodo)
        nombre_sugerido = nombre_sugerido.replace("/", "_").replace("\\", "_")
        nombre_sugerido = re.sub(r"[^a-z0-9_áéíóúñü-]", "", nombre_sugerido)
        if not nombre_sugerido:
            nombre_sugerido = "resultado"

        ruta = filedialog.asksaveasfilename(
            title="Guardar DataFrame como Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"{nombre_sugerido}.xlsx"
        )
        if not ruta:
            return

        try:
            if filas:
                df = pd.DataFrame(filas)
            else:
                df = self._resultado_a_dataframe(resultado)
            df.to_excel(ruta, index=False)
            messagebox.showinfo("Exportación exitosa", f"Archivo exportado en:\n{ruta}")
        except Exception as exc:
            messagebox.showerror(
                "No se pudo exportar",
                f"Error al crear el Excel: {exc}\n\n"
                "Si falta el motor de Excel, instala: pip install openpyxl"
            )

    def _escribir(self, txt, partes):
        """partes: lista de (texto, tag)"""
        txt.config(state="normal")
        txt.delete("1.0", "end")
        for texto, tag in partes:
            txt.insert("end", texto, tag)
        txt.config(state="disabled")

    def _tabla_como_dataframe(self, filas):
        """Convierte una lista de filas a una vista estilo DataFrame."""
        if not filas:
            return ""

        if PANDAS_DISPONIBLE:
            df = pd.DataFrame(filas)
            return df.to_string(index=False, float_format=lambda x: f"{x:.8f}")

        cols = list(filas[0].keys())
        header = "  " + "".join(f"{c:<16}" for c in cols)
        body = []
        for fila in filas:
            linea = "  "
            for _, valor in fila.items():
                if isinstance(valor, float):
                    linea += f"{valor:<16.8f}"
                else:
                    linea += f"{str(valor):<16}"
            body.append(linea)
        return "\n".join([header, "  " + "─" * (16 * len(cols)), *body])

    def _resultado_a_dataframe(self, resultado: dict):
        """Convierte cualquier resultado de método en un DataFrame exportable."""
        if not isinstance(resultado, dict):
            return pd.DataFrame([{"resultado": str(resultado)}])

        fila = {}
        for key, val in resultado.items():
            if key == "resultados":
                continue

            if isinstance(val, list):
                if all(isinstance(x, (int, float, str, bool)) or x is None for x in val):
                    for i, x in enumerate(val, 1):
                        fila[f"{key}_{i}"] = x
                else:
                    fila[key] = json.dumps(_serializar_json(val), ensure_ascii=False)
            elif isinstance(val, dict):
                for k2, v2 in val.items():
                    fila[f"{key}_{k2}"] = _serializar_json(v2)
            else:
                fila[key] = val

        if not fila:
            fila = {"resultado": "Sin datos exportables"}
        return pd.DataFrame([fila])

    # ─── mensajes de error enriquecidos ──────────────────────────────────────

    _ERRORES = {
        "cambio de signo": (
            "El intervalo [a, b] no cumple f(a)·f(b) < 0",
            "La función debe tener signos opuestos en los extremos.\n"
            "  → Elige un intervalo donde la función cambie de signo.\n"
            "  → Ejemplo: si f(1) > 0 y f(2) < 0, usa a=1, b=2."
        ),
        "límite inferior a no puede ser mayor": (
            "El intervalo está invertido",
            "El límite inferior a no puede ser mayor al superior b.\n"
            "  → Intercambia los valores de a y b antes de calcular."
        ),
        "límites de integración no pueden ser iguales": (
            "El intervalo no puede tener longitud cero",
            "Los valores a y b no pueden ser iguales.\n"
            "  → Ingresa un intervalo con longitud mayor que cero."
        ),
        "derivada": (
            "La derivada f'(x) es cero o muy cercana a cero",
            "Newton-Raphson no puede continuar con f'(x) ≈ 0.\n"
            "  → Elige un x₀ diferente, alejado de puntos críticos.\n"
            "  → Verifica que f'(x) esté bien escrita."
        ),
        "denominador": (
            "Denominador muy cercano a cero (método Secante)",
            "Los puntos x₀ y x₁ generan f(x₁)-f(x₀) ≈ 0.\n"
            "  → Elige valores más separados entre sí."
        ),
        "singular": (
            "La matriz A es singular (no tiene solución única)",
            "El sistema no puede resolverse porque la matriz es singular.\n"
            "  → Verifica que las ecuaciones sean independientes entre sí.\n"
            "  → Comprueba que no haya filas con todos ceros."
        ),
        "convergencia": (
            "El método no convergió en el número de iteraciones dado",
            "  → Aumenta el número máximo de iteraciones.\n"
            "  → Prueba con una tolerancia menos exigente (ej: 1e-4).\n"
            "  → Verifica que el método sea adecuado para esta función."
        ),
    }

    def _mostrar_error(self, txt, exc, expresion=None, variables=("x",)):
        """Muestra errores priorizando mensajes generados por IA."""
        msg = str(exc)
        tipo = type(exc).__name__
        expr = (expresion or "").strip()

        if isinstance(exc, (SyntaxError, NameError)) and expr:
            cache_key = ("sintaxis", expr, msg, tuple(variables))
            respuesta = self._cache_ia.get(cache_key)
            error_ia = None
            if respuesta is None:
                respuesta, error_ia = consultar_ia_sintaxis(expr, msg, variables=variables)
                self._cache_ia[cache_key] = respuesta or {"error": error_ia}
            elif isinstance(respuesta, dict) and "error" in respuesta:
                error_ia = respuesta["error"]
                respuesta = None

            if respuesta:
                titulo = "🤖  Alerta generada por IA"
                detalle = (
                    f"  → Exprésalo así: {respuesta['suggestion']}\n"
                    f"  → {respuesta['explanation']}\n"
                    f"  → Modelo consultado: {respuesta['model']}"
                )
            else:
                titulo = "⚠  No fue posible consultar la IA"
                detalle = (
                    f"Detalle técnico: {msg}\n"
                    f"Estado de IA: {error_ia or 'sin respuesta'}"
                )
        else:
            cache_key = ("error", tipo, msg, expr, tuple(variables))
            respuesta = self._cache_ia.get(cache_key)
            error_ia = None
            if respuesta is None:
                respuesta, error_ia = consultar_ia_contexto(
                    msg,
                    contexto=f"Excepción {tipo} en la interfaz",
                    datos={"expresion": expr, "variables": list(variables), "tipo": tipo},
                )
                self._cache_ia[cache_key] = respuesta or {"error": error_ia}
            elif isinstance(respuesta, dict) and "error" in respuesta:
                error_ia = respuesta["error"]
                respuesta = None

            if respuesta:
                titulo = "🤖  Alerta generada por IA"
                detalle = (
                    f"  → {respuesta['suggestion']}\n"
                    f"  → {respuesta['explanation']}\n"
                    f"  → Modelo consultado: {respuesta['model']}"
                )
            else:
                titulo = "⚠  No fue posible consultar la IA"
                detalle = (
                    f"Detalle técnico: {msg}\n"
                    f"Estado de IA: {error_ia or 'sin respuesta'}"
                )

        self._escribir(txt, [
            (titulo + "\n", "titulo"),
            ("─" * 60 + "\n", "normal"),
            (detalle + "\n", "error"),
        ])

    def _mostrar_resultado(self, txt, resultado: dict, contexto=None):
        txt._ultimo_dataframe = None
        txt._ultimo_resultado = resultado
        if "error" in resultado:
            msg_raw = resultado["error"].lower()
            msg_original = resultado["error"]
            titulo_err = "🤖  Alerta generada por IA"
            detalle_err = ""
            contexto = contexto or {}
            datos_ia = dict(resultado)
            if contexto:
                datos_ia.update(contexto)

            if "cambio de signo" in msg_raw and contexto.get("expresion"):
                try:
                    expr = contexto.get("expresion", "")
                    a = float(contexto.get("a"))
                    b = float(contexto.get("b"))
                    f_eval = eval_func(expr)
                    puntos = [a, b, (a + b) / 2, a - 1.0, b + 1.0, 0.0]
                    valores = []
                    for p in puntos:
                        y = float(f_eval(float(p)))
                        if math.isfinite(y):
                            valores.append(y)

                    if valores and all(v > 0 for v in valores):
                        detalle_err += (
                            "\n\n  Diagnóstico automático:\n"
                            "  → En los puntos muestreados, f(x) fue siempre positiva.\n"
                            "  → Es posible que no exista raíz real para esta función."
                        )
                        datos_ia["diagnostico_local"] = "f(x) positiva en todos los puntos muestreados"
                    elif valores and all(v < 0 for v in valores):
                        detalle_err += (
                            "\n\n  Diagnóstico automático:\n"
                            "  → En los puntos muestreados, f(x) fue siempre negativa.\n"
                            "  → Es posible que no exista raíz real para esta función."
                        )
                        datos_ia["diagnostico_local"] = "f(x) negativa en todos los puntos muestreados"
                except Exception:
                    pass

            cache_key = ("resultado", msg_original)
            ayuda_ia = self._cache_ia.get(cache_key)
            error_ia = None
            if ayuda_ia is None:
                ayuda_ia, error_ia = consultar_ia_contexto(
                    msg_original,
                    contexto="Resultado de método numérico con error",
                    datos=datos_ia,
                )
                self._cache_ia[cache_key] = ayuda_ia or {"error": error_ia}
            elif isinstance(ayuda_ia, dict) and "error" in ayuda_ia:
                error_ia = ayuda_ia["error"]
                ayuda_ia = None

            if ayuda_ia:
                detalle_err += f"  → {ayuda_ia['suggestion']}\n"
                detalle_err += f"  → {ayuda_ia['explanation']}\n"
                detalle_err += f"  → Modelo consultado: {ayuda_ia['model']}"
            elif error_ia:
                titulo_err = "⚠  No fue posible consultar la IA"
                detalle_err = (
                    f"Detalle técnico: {msg_original}\n"
                    f"Estado de IA: {error_ia}"
                )
            else:
                titulo_err = "⚠  No fue posible consultar la IA"
                detalle_err = f"Detalle técnico: {msg_original}"

            self._escribir(txt, [
                (titulo_err + "\n", "titulo"),
                ("─" * 60 + "\n", "normal"),
                (detalle_err + "\n", "advertencia"),
            ])
            return

        partes = []
        partes.append(("✔  Resultado\n", "titulo"))
        partes.append(("─" * 60 + "\n", "normal"))

        # Campos principales que siempre se muestran primero
        campos_principales = ["raiz", "integral", "derivada", "solucion",
                               "valor_interpolado", "metodo", "iteraciones",
                               "error_final", "puntos", "paso",
                               "subintervalos", "ancho_intervalo",
                               "numero_puntos", "punto_x", "numero_ecuaciones"]

        for key in campos_principales:
            if key in resultado:
                val = resultado[key]
                label = key.replace("_", " ").capitalize()
                if isinstance(val, float):
                    partes.append((f"  {label:<22}: ", "normal"))
                    partes.append((f"{val:.10f}\n", "valor"))
                elif isinstance(val, list) and all(isinstance(v, float) for v in val):
                    partes.append((f"  {label:<22}:\n", "normal"))
                    for i, v in enumerate(val):
                        partes.append((f"    x{i+1} = {v:.10f}\n", "valor"))
                else:
                    partes.append((f"  {label:<22}: ", "normal"))
                    partes.append((f"{val}\n", "valor"))

        if "advertencia" in resultado:
            partes.append(("\n⚠  " + resultado["advertencia"] + "\n", "advertencia"))

        # Tabla de iteraciones
        if "resultados" in resultado and resultado["resultados"]:
            res = resultado["resultados"]
            txt._ultimo_dataframe = res
            tabla_df = self._tabla_como_dataframe(res)
            partes.append(("\n" + "─" * 60 + "\n", "normal"))
            partes.append(("  DataFrame de iteraciones\n\n", "cabecera"))
            partes.append((tabla_df + "\n", "normal"))

        self._escribir(txt, partes)


    # ═══════════════════════════════════════════════════════════════════════
    #                       PANEL DE CONFIGURACIÓN IA
    # ═══════════════════════════════════════════════════════════════════════

    def _panel_config_ia(self, frame):  # noqa: C901
        self._titulo(frame, "⚙  Configuración de IA",
                     "Conecta la app a un modelo de lenguaje para sugerencias de sintaxis")

        PROVEEDORES = {
            "Groq (gratuito)": {
                "url":   "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama-3.3-70b-versatile",
            },
            "OpenAI": {
                "url":   "https://api.openai.com/v1/chat/completions",
                "model": "gpt-4o-mini",
            },
            "OpenRouter (gratuito)": {
                "url":   "https://openrouter.ai/api/v1/chat/completions",
                "model": "mistralai/mistral-7b-instruct:free",
            },
            "Personalizado": {
                "url":   "",
                "model": "",
            },
        }

        # ── Valores actuales (de env ya cargado) ─────────────────────────
        api_key_actual = os.getenv("IA_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        url_actual     = os.getenv("IA_API_URL") or os.getenv("OPENAI_API_URL") or ""
        model_actual   = os.getenv("IA_MODEL")   or os.getenv("OPENAI_MODEL")   or ""

        # ── Proveedor ────────────────────────────────────────────────────
        row_prov = tk.Frame(frame, bg=T["BG"])
        row_prov.pack(anchor="w", padx=30, pady=6)
        tk.Label(row_prov, text="Proveedor:", font=("Segoe UI", 9),
                 bg=T["BG"], fg=T["SUBTEXT"], width=26, anchor="w").pack(side="left")
        var_prov = tk.StringVar(value="Groq (gratuito)")
        combo_prov = ttk.Combobox(row_prov, textvariable=var_prov,
                                  values=list(PROVEEDORES.keys()),
                                  state="readonly", font=("Segoe UI", 10), width=28)
        combo_prov.pack(side="left")

        # ── API Key ──────────────────────────────────────────────────────
        row_key = tk.Frame(frame, bg=T["BG"])
        row_key.pack(anchor="w", padx=30, pady=3)
        tk.Label(row_key, text="API Key:", font=("Segoe UI", 9),
                 bg=T["BG"], fg=T["SUBTEXT"], width=26, anchor="w").pack(side="left")
        var_key = tk.StringVar(value=api_key_actual)
        entry_key = tk.Entry(row_key, textvariable=var_key, font=("Consolas", 10),
                             bg=T["CARD_BG"], fg=T["TEXT"], insertbackground=T["TEXT"],
                             relief="flat", bd=6, width=36, show="•")
        entry_key.pack(side="left")

        btn_eye = tk.Button(row_key, text="👁", font=("Segoe UI", 9),
                            bg=T["CARD_BG"], fg=T["SUBTEXT"], bd=0, cursor="hand2",
                            relief="flat", padx=4)
        btn_eye.pack(side="left", padx=(4, 0))
        def _toggle_key():
            entry_key.config(show="" if entry_key.cget("show") == "•" else "•")
        btn_eye.config(command=_toggle_key)

        # ── Modelo ───────────────────────────────────────────────────────
        var_model = tk.StringVar(value=model_actual or "llama-3.3-70b-versatile")
        row_model = tk.Frame(frame, bg=T["BG"])
        row_model.pack(anchor="w", padx=30, pady=3)
        tk.Label(row_model, text="Modelo:", font=("Segoe UI", 9),
                 bg=T["BG"], fg=T["SUBTEXT"], width=26, anchor="w").pack(side="left")
        entry_model = tk.Entry(row_model, textvariable=var_model,
                               font=("Consolas", 10), bg=T["CARD_BG"], fg=T["TEXT"],
                               insertbackground=T["TEXT"], relief="flat", bd=6, width=36)
        entry_model.pack(side="left")

        # ── URL de la API (avanzado) ──────────────────────────────────────
        var_url = tk.StringVar(value=url_actual or "https://api.groq.com/openai/v1/chat/completions")
        row_url = tk.Frame(frame, bg=T["BG"])
        row_url.pack(anchor="w", padx=30, pady=3)
        tk.Label(row_url, text="URL de la API:", font=("Segoe UI", 9),
                 bg=T["BG"], fg=T["SUBTEXT"], width=26, anchor="w").pack(side="left")
        entry_url = tk.Entry(row_url, textvariable=var_url,
                             font=("Consolas", 9), bg=T["CARD_BG"], fg=T["TEXT"],
                             insertbackground=T["TEXT"], relief="flat", bd=6, width=50)
        entry_url.pack(side="left")

        # Cuando cambia el proveedor, auto-rellena modelo y URL
        def _on_prov_change(*_):
            prov = var_prov.get()
            datos = PROVEEDORES.get(prov, {})
            if datos.get("url"):
                var_url.set(datos["url"])
            if datos.get("model"):
                var_model.set(datos["model"])
        combo_prov.bind("<<ComboboxSelected>>", _on_prov_change)

        # ── Área de estado ───────────────────────────────────────────────
        tk.Frame(frame, bg=T["SURFACE"], height=1).pack(fill="x", padx=30, pady=(14, 6))

        lbl_estado = tk.Label(frame, text="", font=("Segoe UI", 9),
                              bg=T["BG"], fg=T["SUBTEXT"], anchor="w", wraplength=540, justify="left")
        lbl_estado.pack(anchor="w", padx=30)

        # ── Botones ──────────────────────────────────────────────────────
        row_btns = tk.Frame(frame, bg=T["BG"])
        row_btns.pack(anchor="w", padx=30, pady=(10, 6))

        def _guardar():
            key   = var_key.get().strip()
            model = var_model.get().strip()
            url   = var_url.get().strip()
            if not key:
                lbl_estado.config(text="⚠  Ingresa una API Key válida.", fg=T["YELLOW"])
                return
            if not url:
                lbl_estado.config(text="⚠  La URL de la API no puede estar vacía.", fg=T["YELLOW"])
                return
            if not model:
                lbl_estado.config(text="⚠  Especifica un nombre de modelo.", fg=T["YELLOW"])
                return
            _guardar_env({"IA_API_KEY": key, "IA_API_URL": url, "IA_MODEL": model})
            self._cache_ia.clear()   # limpia caché para usar nueva config
            lbl_estado.config(
                text=f"✔  Configuración guardada en .env  —  Modelo: {model}",
                fg=T["GREEN"]
            )

        def _probar():
            key = var_key.get().strip()
            url = var_url.get().strip()
            model = var_model.get().strip()
            if not key:
                lbl_estado.config(text="⚠  Ingresa una API Key antes de probar.", fg=T["YELLOW"])
                return
            lbl_estado.config(text="… Probando conexión con la IA …", fg=T["SUBTEXT"])
            frame.update_idletasks()
            # Guarda temporalmente para que consultar_ia_sintaxis las use
            os.environ["IA_API_KEY"]  = key
            os.environ["IA_API_URL"]  = url
            os.environ["IA_MODEL"]    = model
            resultado, err = consultar_ia_sintaxis("2x+1", "sintaxis de prueba")
            if resultado:
                lbl_estado.config(
                    text=f"✔  Conexión exitosa.  Respuesta del modelo: {resultado.get('suggestion', 'ok')}",
                    fg=T["GREEN"]
                )
            else:
                lbl_estado.config(text=f"✘  {err}", fg=T["RED"])

        tk.Button(
            row_btns, text="  💾  Guardar  ", font=("Segoe UI", 10, "bold"),
            bg=T["ACCENT"], fg=T["BG"], relief="flat", cursor="hand2",
            activebackground=T["BTN_HOVER"], activeforeground=T["BG"],
            padx=14, pady=7, command=_guardar
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            row_btns, text="  🔌  Probar conexión  ", font=("Segoe UI", 10, "bold"),
            bg=T["ACCENT2"], fg=T["BG"], relief="flat", cursor="hand2",
            activebackground=T["BTN_HOVER"], activeforeground=T["BG"],
            padx=14, pady=7, command=_probar
        ).pack(side="left")

        # ── Nota informativa ─────────────────────────────────────────────
        tk.Frame(frame, bg=T["SURFACE"], height=1).pack(fill="x", padx=30, pady=(14, 4))
        nota = (
            "ℹ  La configuración se guarda en el archivo .env de este proyecto.\n"
            "   Groq ofrece una API gratuita en: console.groq.com  →  Crea cuenta → API Keys → Create API Key"
        )
        tk.Label(frame, text=nota, font=("Segoe UI", 8), bg=T["BG"],
                 fg=T["SUBTEXT"], anchor="w", justify="left", wraplength=580).pack(anchor="w", padx=30, pady=4)

    # ═══════════════════════════════════════════════════════════════════════
    #                         PANELES DE MÉTODOS
    # ═══════════════════════════════════════════════════════════════════════

    # ── BISECCIÓN ────────────────────────────────────────────────────────────
    def _panel_biseccion(self):
        self._cambiar_panel(self.__panel_biseccion, "Bisección")

    def __panel_biseccion(self, frame):
        self._titulo(frame, "Método de Bisección",
                     "Encuentra raíces en un intervalo [a, b]")
        v_fx  = self._campo(frame, "f(x) =", self._default_metodo("biseccion", "fx", "x**3 - x - 2"))
        v_a   = self._campo(frame, "Límite inferior  a =", self._default_metodo("biseccion", "a", "1"))
        v_b   = self._campo(frame, "Límite superior  b =", self._default_metodo("biseccion", "b", "2"))
        v_tol = self._campo(frame, "Tolerancia =", self._default_metodo("biseccion", "tol", "1e-6"))
        v_it  = self._campo(frame, "Máx. iteraciones =", self._default_metodo("biseccion", "it", "100"))

        def calcular():
            try:
                f   = eval_func(v_fx.get())
                a   = eval_num(v_a.get())
                b   = eval_num(v_b.get())
                tol = float(v_tol.get())
                it  = int(v_it.get())
                resultado = mn.biseccion(f, a, b, tol, it)
                self._guardar_calculo("biseccion", {
                    "fx": v_fx.get(), "a": v_a.get(), "b": v_b.get(),
                    "tol": v_tol.get(), "it": v_it.get()
                }, resultado)
                self._mostrar_resultado(
                    txt,
                    resultado,
                    contexto={"metodo": "biseccion", "expresion": v_fx.get(), "a": a, "b": b},
                )
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_a=v_a, var_b=v_b)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── NEWTON-RAPHSON ────────────────────────────────────────────────────────
    def _panel_newton(self):
        self._cambiar_panel(self.__panel_newton, "Newton-Raphson")

    def __panel_newton(self, frame):
        self._titulo(frame, "Método de Newton-Raphson",
                     "Requiere f(x) y su derivada f'(x)")
        v_fx  = self._campo(frame, "f(x) =", self._default_metodo("newton", "fx", "x**3 - x - 2"))
        v_dfx = self._campo(frame, "f'(x) =", self._default_metodo("newton", "dfx", "3*x**2 - 1"))
        v_x0  = self._campo(frame, "Aproximación  x₀ =", self._default_metodo("newton", "x0", "1.5"))
        v_tol = self._campo(frame, "Tolerancia =", self._default_metodo("newton", "tol", "1e-6"))
        v_it  = self._campo(frame, "Máx. iteraciones =", self._default_metodo("newton", "it", "100"))

        def calcular():
            try:
                f   = eval_func(v_fx.get())
                df  = eval_func(v_dfx.get())
                x0  = eval_num(v_x0.get())
                tol = float(v_tol.get())
                it  = int(v_it.get())
                resultado = mn.newton_raphson(f, df, x0, tol, it)
                self._guardar_calculo("newton", {
                    "fx": v_fx.get(), "dfx": v_dfx.get(), "x0": v_x0.get(),
                    "tol": v_tol.get(), "it": v_it.get()
                }, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_x0=v_x0)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── SECANTE ───────────────────────────────────────────────────────────────
    def _panel_secante(self):
        self._cambiar_panel(self.__panel_secante, "Secante")

    def __panel_secante(self, frame):
        self._titulo(frame, "Método de la Secante",
                     "Dos aproximaciones iniciales x₀ y x₁")
        v_fx  = self._campo(frame, "f(x) =", self._default_metodo("secante", "fx", "x**3 - x - 2"))
        v_x0  = self._campo(frame, "x₀ =", self._default_metodo("secante", "x0", "1"))
        v_x1  = self._campo(frame, "x₁ =", self._default_metodo("secante", "x1", "2"))
        v_tol = self._campo(frame, "Tolerancia =", self._default_metodo("secante", "tol", "1e-6"))
        v_it  = self._campo(frame, "Máx. iteraciones =", self._default_metodo("secante", "it", "100"))

        def calcular():
            try:
                f   = eval_func(v_fx.get())
                x0  = eval_num(v_x0.get())
                x1  = eval_num(v_x1.get())
                tol = float(v_tol.get())
                it  = int(v_it.get())
                resultado = mn.secante(f, x0, x1, tol, it)
                self._guardar_calculo("secante", {
                    "fx": v_fx.get(), "x0": v_x0.get(), "x1": v_x1.get(),
                    "tol": v_tol.get(), "it": v_it.get()
                }, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_x0=v_x0, var_x1=v_x1)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── FALSA POSICIÓN ────────────────────────────────────────────────────────
    def _panel_falsa_posicion(self):
        self._cambiar_panel(self.__panel_falsa_posicion, "Falsa Posición")

    def __panel_falsa_posicion(self, frame):
        self._titulo(frame, "Método de Falsa Posición",
                     "Regula Falsi — intervalo [a, b] con cambio de signo")
        v_fx  = self._campo(frame, "f(x) =", self._default_metodo("falsa_posicion", "fx", "x**3 - x - 2"))
        v_a   = self._campo(frame, "Límite inferior  a =", self._default_metodo("falsa_posicion", "a", "1"))
        v_b   = self._campo(frame, "Límite superior  b =", self._default_metodo("falsa_posicion", "b", "2"))
        v_tol = self._campo(frame, "Tolerancia =", self._default_metodo("falsa_posicion", "tol", "1e-6"))
        v_it  = self._campo(frame, "Máx. iteraciones =", self._default_metodo("falsa_posicion", "it", "100"))

        def calcular():
            try:
                f   = eval_func(v_fx.get())
                a   = eval_num(v_a.get())
                b   = eval_num(v_b.get())
                tol = float(v_tol.get())
                it  = int(v_it.get())
                resultado = mn.falsa_posicion(f, a, b, tol, it)
                self._guardar_calculo("falsa_posicion", {
                    "fx": v_fx.get(), "a": v_a.get(), "b": v_b.get(),
                    "tol": v_tol.get(), "it": v_it.get()
                }, resultado)
                self._mostrar_resultado(
                    txt,
                    resultado,
                    contexto={"metodo": "falsa_posicion", "expresion": v_fx.get(), "a": a, "b": b},
                )
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_a=v_a, var_b=v_b)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── LAGRANGE ──────────────────────────────────────────────────────────────
    def _panel_lagrange(self):
        self._cambiar_panel(self.__panel_lagrange, "Lagrange")

    def __panel_lagrange(self, frame):
        self._titulo(frame, "Interpolación de Lagrange",
                     "Ingresa los puntos separados por comas: x0,y0 ; x1,y1 ; ...")
        v_pts = self._campo(frame, "Puntos (xi,yi) =", self._default_metodo("lagrange", "pts", "0,1 ; 1,2.718 ; 2,7.389"), ancho=45)
        v_xi  = self._campo(frame, "Interpolar en x =", self._default_metodo("lagrange", "xi", "1.5"))

        def calcular():
            try:
                partes = v_pts.get().split(";")
                puntos = []
                for p in partes:
                    xy = p.strip().split(",")
                    puntos.append((eval_num(xy[0].strip()), eval_num(xy[1].strip())))
                xi = eval_num(v_xi.get())
                resultado = mn.lagrange(puntos, xi)
                self._guardar_calculo("lagrange", {"pts": v_pts.get(), "xi": v_xi.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e)

        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── NEWTON DIVIDIDAS ──────────────────────────────────────────────────────
    def _panel_newton_interp(self):
        self._cambiar_panel(self.__panel_newton_interp, "Newton Divididas")

    def __panel_newton_interp(self, frame):
        self._titulo(frame, "Interpolación de Newton (Dif. Divididas)",
                     "Ingresa los puntos separados por punto y coma: x0,y0 ; x1,y1 ; ...")
        v_pts = self._campo(frame, "Puntos (xi,yi) =", self._default_metodo("newton_divididas", "pts", "0,1 ; 1,2.718 ; 2,7.389"), ancho=45)
        v_xi  = self._campo(frame, "Interpolar en x =", self._default_metodo("newton_divididas", "xi", "1.5"))

        def calcular():
            try:
                partes = v_pts.get().split(";")
                puntos = []
                for p in partes:
                    xy = p.strip().split(",")
                    puntos.append((eval_num(xy[0].strip()), eval_num(xy[1].strip())))
                xi = eval_num(v_xi.get())
                resultado = mn.diferencias_divididas(puntos, xi)
                self._guardar_calculo("newton_divididas", {"pts": v_pts.get(), "xi": v_xi.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e)

        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── TRAPECIO ─────────────────────────────────────────────────────────────
    def _panel_trapecio(self):
        self._cambiar_panel(self.__panel_trapecio, "Trapecio")

    def __panel_trapecio(self, frame):
        self._titulo(frame, "Regla del Trapecio",
                     "Puedes usar: sin(x), cos(x), exp(x), pi, e, sqrt(x), log(x), ...")
        v_fx = self._campo(frame, "f(x) =", self._default_metodo("trapecio", "fx", "sin(x)"))
        v_a  = self._campo(frame, "Límite inferior  a =", self._default_metodo("trapecio", "a", "0"))
        v_b  = self._campo(frame, "Límite superior  b =", self._default_metodo("trapecio", "b", "pi"))
        v_n  = self._campo(frame, "Subintervalos  n =", self._default_metodo("trapecio", "n", "100"))

        def calcular():
            try:
                f = eval_func(v_fx.get())
                a = eval_num(v_a.get())
                b = eval_num(v_b.get())
                n = int(v_n.get())
                resultado = mn.trapecio(f, a, b, n)
                self._guardar_calculo("trapecio", {"fx": v_fx.get(), "a": v_a.get(), "b": v_b.get(), "n": v_n.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_a=v_a, var_b=v_b)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── SIMPSON 1/3 ───────────────────────────────────────────────────────────
    def _panel_simpson13(self):
        self._cambiar_panel(self.__panel_simpson13, "Simpson 1/3")

    def __panel_simpson13(self, frame):
        self._titulo(frame, "Regla de Simpson 1/3",
                     "n debe ser par (se ajusta automáticamente)")
        v_fx = self._campo(frame, "f(x) =", self._default_metodo("simpson13", "fx", "sin(x)"))
        v_a  = self._campo(frame, "Límite inferior  a =", self._default_metodo("simpson13", "a", "0"))
        v_b  = self._campo(frame, "Límite superior  b =", self._default_metodo("simpson13", "b", "pi"))
        v_n  = self._campo(frame, "Subintervalos  n =", self._default_metodo("simpson13", "n", "100"))

        def calcular():
            try:
                f = eval_func(v_fx.get())
                a = eval_num(v_a.get())
                b = eval_num(v_b.get())
                n = int(v_n.get())
                resultado = mn.simpson_1_3(f, a, b, n)
                self._guardar_calculo("simpson13", {"fx": v_fx.get(), "a": v_a.get(), "b": v_b.get(), "n": v_n.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_a=v_a, var_b=v_b)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── SIMPSON 3/8 ───────────────────────────────────────────────────────────
    def _panel_simpson38(self):
        self._cambiar_panel(self.__panel_simpson38, "Simpson 3/8")

    def __panel_simpson38(self, frame):
        self._titulo(frame, "Regla de Simpson 3/8",
                     "n debe ser múltiplo de 3 (se ajusta automáticamente)")
        v_fx = self._campo(frame, "f(x) =", self._default_metodo("simpson38", "fx", "sin(x)"))
        v_a  = self._campo(frame, "Límite inferior  a =", self._default_metodo("simpson38", "a", "0"))
        v_b  = self._campo(frame, "Límite superior  b =", self._default_metodo("simpson38", "b", "pi"))
        v_n  = self._campo(frame, "Subintervalos  n =", self._default_metodo("simpson38", "n", "99"))

        def calcular():
            try:
                f = eval_func(v_fx.get())
                a = eval_num(v_a.get())
                b = eval_num(v_b.get())
                n = int(v_n.get())
                resultado = mn.simpson_3_8(f, a, b, n)
                self._guardar_calculo("simpson38", {"fx": v_fx.get(), "a": v_a.get(), "b": v_b.get(), "n": v_n.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_a=v_a, var_b=v_b)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── ELIMINACIÓN GAUSSIANA ─────────────────────────────────────────────────
    def _panel_gauss(self):
        self._cambiar_panel(self.__panel_gauss, "Gauss Eliminación")

    def __panel_gauss(self, frame):
        self._titulo(frame, "Eliminación Gaussiana",
                     "Ingresa cada fila  separada por ';'  y coefs separados por comas.\n"
                     "Ej 3x3:  2,1,-1 ; -3,-1,2 ; -2,1,2   y  b: 8,-11,-3")
        v_A = self._campo(frame, "Matriz A (filas) =", self._default_metodo("gauss", "A", "2,1,-1 ; -3,-1,2 ; -2,1,2"), ancho=45)
        v_b = self._campo(frame, "Vector b =", self._default_metodo("gauss", "b", "8,-11,-3"), ancho=45)

        def calcular():
            try:
                A = [[eval_num(x) for x in fila.split(",")]
                     for fila in v_A.get().split(";")]
                b = [eval_num(x) for x in v_b.get().split(",")]
                resultado = mn.eliminacion_gaussiana(A, b)
                self._guardar_calculo("gauss", {"A": v_A.get(), "b": v_b.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e)

        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── GAUSS-SEIDEL ──────────────────────────────────────────────────────────
    def _panel_gauss_seidel(self):
        self._cambiar_panel(self.__panel_gauss_seidel, "Gauss-Seidel")

    def __panel_gauss_seidel(self, frame):
        self._titulo(frame, "Método de Gauss-Seidel",
                     "Misma sintaxis que Gauss. x₀ puede dejarse vacío (se usa 0).")
        v_A  = self._campo(frame, "Matriz A (filas) =", self._default_metodo("gauss_seidel", "A", "4,-1,0 ; -1,4,-1 ; 0,-1,4"), ancho=45)
        v_b  = self._campo(frame, "Vector b =", self._default_metodo("gauss_seidel", "b", "1,5,1"), ancho=45)
        v_x0 = self._campo(frame, "x₀ inicial (opcional) =", self._default_metodo("gauss_seidel", "x0", "0,0,0"), ancho=45)
        v_tol = self._campo(frame, "Tolerancia =", self._default_metodo("gauss_seidel", "tol", "1e-6"))
        v_it  = self._campo(frame, "Máx. iteraciones =", self._default_metodo("gauss_seidel", "it", "100"))

        def calcular():
            try:
                A  = [[eval_num(x) for x in fila.split(",")]
                      for fila in v_A.get().split(";")]
                b  = [eval_num(x) for x in v_b.get().split(",")]
                x0_str = v_x0.get().strip()
                x0 = [eval_num(x) for x in x0_str.split(",")] if x0_str else None
                tol = float(v_tol.get())
                it  = int(v_it.get())
                resultado = mn.gauss_seidel(A, b, x0, tol, it)
                self._guardar_calculo("gauss_seidel", {
                    "A": v_A.get(), "b": v_b.get(), "x0": v_x0.get(),
                    "tol": v_tol.get(), "it": v_it.get()
                }, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e)

        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── DIFERENCIAS ───────────────────────────────────────────────────────────
    def _panel_dif_prog(self):
        self._cambiar_panel(self.__panel_dif_prog, "Dif. Progresiva")

    def __panel_dif_prog(self, frame):
        self._titulo(frame, "Diferencia Progresiva",
                     "f'(x) ≈ [f(x+h) - f(x)] / h")
        v_fx = self._campo(frame, "f(x) =", self._default_metodo("dif_prog", "fx", "sin(x)"))
        v_x  = self._campo(frame, "Punto  x =", self._default_metodo("dif_prog", "x", "pi/4"))
        v_h  = self._campo(frame, "Paso  h =", self._default_metodo("dif_prog", "h", "1e-5"))

        def calcular():
            try:
                f = eval_func(v_fx.get())
                x = eval_num(v_x.get())
                h = float(v_h.get())
                resultado = mn.diferencia_progresiva(f, x, h)
                self._guardar_calculo("dif_prog", {"fx": v_fx.get(), "x": v_x.get(), "h": v_h.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_x0=v_x)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    def _panel_dif_reg(self):
        self._cambiar_panel(self.__panel_dif_reg, "Dif. Regresiva")

    def __panel_dif_reg(self, frame):
        self._titulo(frame, "Diferencia Regresiva",
                     "f'(x) ≈ [f(x) - f(x-h)] / h")
        v_fx = self._campo(frame, "f(x) =", self._default_metodo("dif_reg", "fx", "sin(x)"))
        v_x  = self._campo(frame, "Punto  x =", self._default_metodo("dif_reg", "x", "pi/4"))
        v_h  = self._campo(frame, "Paso  h =", self._default_metodo("dif_reg", "h", "1e-5"))

        def calcular():
            try:
                f = eval_func(v_fx.get())
                x = eval_num(v_x.get())
                h = float(v_h.get())
                resultado = mn.diferencia_regresiva(f, x, h)
                self._guardar_calculo("dif_reg", {"fx": v_fx.get(), "x": v_x.get(), "h": v_h.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_x0=v_x)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    def _panel_dif_central(self):
        self._cambiar_panel(self.__panel_dif_central, "Dif. Central")

    def __panel_dif_central(self, frame):
        self._titulo(frame, "Diferencia Central",
                     "f'(x) ≈ [f(x+h) - f(x-h)] / 2h  (más precisa)")
        v_fx = self._campo(frame, "f(x) =", self._default_metodo("dif_central", "fx", "sin(x)"))
        v_x  = self._campo(frame, "Punto  x =", self._default_metodo("dif_central", "x", "pi/4"))
        v_h  = self._campo(frame, "Paso  h =", self._default_metodo("dif_central", "h", "1e-5"))

        def calcular():
            try:
                f = eval_func(v_fx.get())
                x = eval_num(v_x.get())
                h = float(v_h.get())
                resultado = mn.diferencia_central(f, x, h)
                self._guardar_calculo("dif_central", {"fx": v_fx.get(), "x": v_x.get(), "h": v_h.get()}, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_fx.get(), variables=("x",))

        self._boton_graficar(frame, v_fx, var_x0=v_x)
        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── EULER ─────────────────────────────────────────────────────────────────
    def _panel_euler(self):
        self._cambiar_panel(self.__panel_euler, "Euler")

    def __panel_euler(self, frame):
        self._titulo(frame, "Método de Euler",
                     "Resuelve  dy/dx = f(x, y)  con condición inicial y(x₀) = y₀")
        v_f  = self._campo(frame, "f(x, y) =", self._default_metodo("euler", "fxy", "x + y"))
        v_x0 = self._campo(frame, "x₀ =", self._default_metodo("euler", "x0", "0"))
        v_y0 = self._campo(frame, "y₀ =", self._default_metodo("euler", "y0", "1"))
        v_xf = self._campo(frame, "x final  xf =", self._default_metodo("euler", "xf", "1"))
        v_h  = self._campo(frame, "Paso  h =", self._default_metodo("euler", "h", "0.1"))

        def calcular():
            try:
                f  = eval_func2(v_f.get())
                x0 = eval_num(v_x0.get())
                y0 = eval_num(v_y0.get())
                xf = eval_num(v_xf.get())
                h  = float(v_h.get())
                resultado = mn.euler(f, x0, y0, xf, h)
                self._guardar_calculo("euler", {
                    "fxy": v_f.get(), "x0": v_x0.get(), "y0": v_y0.get(),
                    "xf": v_xf.get(), "h": v_h.get()
                }, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_f.get(), variables=("x", "y"))

        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)

    # ── RUNGE-KUTTA 4 ─────────────────────────────────────────────────────────
    def _panel_rk4(self):
        self._cambiar_panel(self.__panel_rk4, "Runge-Kutta 4")

    def __panel_rk4(self, frame):
        self._titulo(frame, "Runge-Kutta Orden 4",
                     "Resuelve  dy/dx = f(x, y)  con condición inicial y(x₀) = y₀")
        v_f  = self._campo(frame, "f(x, y) =", self._default_metodo("rk4", "fxy", "x + y"))
        v_x0 = self._campo(frame, "x₀ =", self._default_metodo("rk4", "x0", "0"))
        v_y0 = self._campo(frame, "y₀ =", self._default_metodo("rk4", "y0", "1"))
        v_xf = self._campo(frame, "x final  xf =", self._default_metodo("rk4", "xf", "1"))
        v_h  = self._campo(frame, "Paso  h =", self._default_metodo("rk4", "h", "0.1"))

        def calcular():
            try:
                f  = eval_func2(v_f.get())
                x0 = eval_num(v_x0.get())
                y0 = eval_num(v_y0.get())
                xf = eval_num(v_xf.get())
                h  = float(v_h.get())
                resultado = mn.runge_kutta_4(f, x0, y0, xf, h)
                self._guardar_calculo("rk4", {
                    "fxy": v_f.get(), "x0": v_x0.get(), "y0": v_y0.get(),
                    "xf": v_xf.get(), "h": v_h.get()
                }, resultado)
                self._mostrar_resultado(txt, resultado)
            except Exception as e:
                self._mostrar_error(txt, e, expresion=v_f.get(), variables=("x", "y"))

        self._boton_calcular(frame, calcular)
        txt = self._area_resultado(frame)


# ─────────────────────────── PUNTO DE ENTRADA ────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
