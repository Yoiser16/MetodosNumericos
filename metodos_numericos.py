"""
CONSOLA DE MÉTODOS NUMÉRICOS
==============================
Implementación de los principales métodos numéricos para resolución de problemas matemáticos.
Autor: Estudiante de Métodos Numéricos
"""

import math
import os
from typing import Callable, List, Tuple, Union


class MetodosNumericos:
    """Clase que contiene todos los métodos numéricos del curso"""

    # ====================== MÉTODOS PARA ENCONTRAR RAÍCES ======================

    @staticmethod
    def biseccion(f: Callable, a: float, b: float, tol: float = 1e-6, max_iter: int = 100) -> dict:
        """
        Método de Bisección para encontrar raíces
        
        Args:
            f: Función algebraica
            a, b: Intervalo [a, b]
            tol: Tolerancia
            max_iter: Máximo de iteraciones
            
        Returns:
            Diccionario con resultados
        """
        resultados = []
        iteracion = 0

        if a == b:
            return {
                "error": (
                    "Los límites del intervalo no pueden ser iguales (a = b). "
                    "Ingresa dos valores distintos; por ejemplo: a=1 y b=2."
                )
            }

        if a > b:
            return {
                "error": (
                    "El límite inferior a no puede ser mayor al superior b. "
                    "Intercambia los valores de a y b."
                )
            }

        fa = f(a)
        fb = f(b)

        if fa * fb > 0:
            return {
                "error": (
                    "No hay cambio de signo en el intervalo: "
                    f"f(a)={fa:.6g}, f(b)={fb:.6g}. "
                    "Elige un intervalo donde uno sea positivo y el otro negativo."
                )
            }
        
        while iteracion < max_iter:
            c = (a + b) / 2
            error = abs(b - a) / 2
            resultados.append({
                "iteracion": iteracion + 1,
                "a": round(a, 8),
                "b": round(b, 8),
                "c": round(c, 8),
                "f(c)": round(f(c), 8),
                "error": round(error, 8)
            })
            
            if error < tol or abs(f(c)) < tol:
                return {
                    "raiz": c,
                    "iteraciones": iteracion + 1,
                    "error_final": error,
                    "resultados": resultados
                }
            
            if f(a) * f(c) < 0:
                b = c
            else:
                a = c
            
            iteracion += 1
        
        return {
            "raiz": (a + b) / 2,
            "iteraciones": max_iter,
            "error_final": abs(b - a) / 2,
            "resultados": resultados,
            "advertencia": "Se alcanzó máximo de iteraciones"
        }

    @staticmethod
    def newton_raphson(f: Callable, df: Callable, x0: float, tol: float = 1e-6, max_iter: int = 100) -> dict:
        """
        Método de Newton-Raphson
        
        Args:
            f: Función
            df: Derivada de la función
            x0: Aproximación inicial
            tol: Tolerancia
            max_iter: Máximo de iteraciones
            
        Returns:
            Diccionario con resultados
        """
        resultados = []
        x = x0
        
        for iteracion in range(max_iter):
            fx = f(x)
            dfx = df(x)
            
            if abs(dfx) < 1e-10:
                return {"error": "Derivada muy cerca de cero"}
            
            x_nuevo = x - fx / dfx
            error = abs(x_nuevo - x)
            
            resultados.append({
                "iteracion": iteracion + 1,
                "x": round(x, 8),
                "f(x)": round(fx, 8),
                "f'(x)": round(dfx, 8),
                "x_nuevo": round(x_nuevo, 8),
                "error": round(error, 8)
            })
            
            if error < tol:
                return {
                    "raiz": x_nuevo,
                    "iteraciones": iteracion + 1,
                    "error_final": error,
                    "resultados": resultados
                }
            
            x = x_nuevo
        
        return {
            "raiz": x,
            "iteraciones": max_iter,
            "error_final": error,
            "resultados": resultados,
            "advertencia": "Se alcanzó máximo de iteraciones"
        }

    @staticmethod
    def secante(f: Callable, x0: float, x1: float, tol: float = 1e-6, max_iter: int = 100) -> dict:
        """
        Método de la Secante
        
        Args:
            f: Función
            x0, x1: Dos aproximaciones iniciales
            tol: Tolerancia
            max_iter: Máximo de iteraciones
            
        Returns:
            Diccionario con resultados
        """
        resultados = []
        
        for iteracion in range(max_iter):
            f0 = f(x0)
            f1 = f(x1)
            
            if abs(f1 - f0) < 1e-10:
                return {"error": "Denominador muy cerca de cero"}
            
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            error = abs(x2 - x1)
            
            resultados.append({
                "iteracion": iteracion + 1,
                "x0": round(x0, 8),
                "x1": round(x1, 8),
                "x2": round(x2, 8),
                "f(x1)": round(f1, 8),
                "error": round(error, 8)
            })
            
            if error < tol:
                return {
                    "raiz": x2,
                    "iteraciones": iteracion + 1,
                    "error_final": error,
                    "resultados": resultados
                }
            
            x0, x1 = x1, x2
        
        return {
            "raiz": x2,
            "iteraciones": max_iter,
            "error_final": error,
            "resultados": resultados,
            "advertencia": "Se alcanzó máximo de iteraciones"
        }

    @staticmethod
    def falsa_posicion(f: Callable, a: float, b: float, tol: float = 1e-6, max_iter: int = 100) -> dict:
        """
        Método de Falsa Posición (Regula Falsi)
        
        Args:
            f: Función
            a, b: Intervalo [a, b]
            tol: Tolerancia
            max_iter: Máximo de iteraciones
            
        Returns:
            Diccionario con resultados
        """
        resultados = []

        if a == b:
            return {
                "error": (
                    "Los límites del intervalo no pueden ser iguales (a = b). "
                    "Ingresa dos valores distintos; por ejemplo: a=1 y b=2."
                )
            }

        if a > b:
            return {
                "error": (
                    "El límite inferior a no puede ser mayor al superior b. "
                    "Intercambia los valores de a y b."
                )
            }

        fa = f(a)
        fb = f(b)

        if fa * fb > 0:
            return {
                "error": (
                    "No hay cambio de signo en el intervalo: "
                    f"f(a)={fa:.6g}, f(b)={fb:.6g}. "
                    "Elige un intervalo donde uno sea positivo y el otro negativo."
                )
            }
        
        for iteracion in range(max_iter):
            fa = f(a)
            fb = f(b)
            
            c = a - fa * (b - a) / (fb - fa)
            fc = f(c)
            error = abs(b - a)
            
            resultados.append({
                "iteracion": iteracion + 1,
                "a": round(a, 8),
                "b": round(b, 8),
                "c": round(c, 8),
                "f(c)": round(fc, 8),
                "error": round(error, 8)
            })
            
            if error < tol or abs(fc) < tol:
                return {
                    "raiz": c,
                    "iteraciones": iteracion + 1,
                    "error_final": error,
                    "resultados": resultados
                }
            
            if fa * fc < 0:
                b = c
            else:
                a = c
        
        return {
            "raiz": c,
            "iteraciones": max_iter,
            "error_final": error,
            "resultados": resultados,
            "advertencia": "Se alcanzó máximo de iteraciones"
        }

    # ====================== MÉTODOS DE INTERPOLACIÓN ======================

    @staticmethod
    def lagrange(puntos: List[Tuple[float, float]], x: float) -> dict:
        """
        Interpolación de Lagrange
        
        Args:
            puntos: Lista de tuplas (x_i, y_i)
            x: Punto donde se desea interpolar
            
        Returns:
            Valor interpolado
        """
        n = len(puntos)
        resultado = 0
        
        for i in range(n):
            termino = puntos[i][1]
            for j in range(n):
                if i != j:
                    termino *= (x - puntos[j][0]) / (puntos[i][0] - puntos[j][0])
            resultado += termino
        
        return {
            "valor_interpolado": resultado,
            "numero_puntos": n,
            "punto_x": x
        }

    @staticmethod
    def diferencias_divididas(puntos: List[Tuple[float, float]], x: float) -> dict:
        """
        Interpolación de Newton con Diferencias Divididas
        
        Args:
            puntos: Lista de tuplas (x_i, y_i)
            x: Punto donde se desea interpolar
            
        Returns:
            Valor interpolado
        """
        n = len(puntos)
        tabla = [[0 for _ in range(n)] for _ in range(n)]
        
        # Primera columna: valores y
        for i in range(n):
            tabla[i][0] = puntos[i][1]
        
        # Construir tabla de diferencias divididas
        for j in range(1, n):
            for i in range(n - j):
                tabla[i][j] = (tabla[i + 1][j - 1] - tabla[i][j - 1]) / (
                    puntos[i + j][0] - puntos[i][0]
                )
        
        # Evaluar el polinomio
        resultado = tabla[0][0]
        producto = 1
        
        for i in range(1, n):
            producto *= (x - puntos[i - 1][0])
            resultado += tabla[0][i] * producto
        
        return {
            "valor_interpolado": resultado,
            "numero_puntos": n,
            "punto_x": x
        }

    # ====================== MÉTODOS DE INTEGRACIÓN NUMÉRICA ======================

    @staticmethod
    def trapecio(f: Callable, a: float, b: float, n: int = 100) -> dict:
        """
        Regla del Trapecio
        
        Args:
            f: Función a integrar
            a, b: Límites de integración
            n: Número de subintervalos
            
        Returns:
            Valor de la integral
        """
        if a > b:
            return {
                "error": (
                    "El límite inferior a no puede ser mayor al superior b. "
                    "Intercambia los valores de a y b."
                )
            }

        if a == b:
            return {
                "error": (
                    "Los límites de integración no pueden ser iguales (a = b). "
                    "Ingresa un intervalo con longitud mayor que cero."
                )
            }

        h = (b - a) / n
        suma = (f(a) + f(b)) / 2
        
        for i in range(1, n):
            suma += f(a + i * h)
        
        integral = h * suma
        
        return {
            "integral": integral,
            "metodo": "Regla del Trapecio",
            "subintervalos": n,
            "ancho_intervalo": h
        }

    @staticmethod
    def simpson_1_3(f: Callable, a: float, b: float, n: int = 100) -> dict:
        """
        Regla de Simpson 1/3
        
        Args:
            f: Función a integrar
            a, b: Límites de integración
            n: Número de subintervalos (debe ser par)
            
        Returns:
            Valor de la integral
        """
        if a > b:
            return {
                "error": (
                    "El límite inferior a no puede ser mayor al superior b. "
                    "Intercambia los valores de a y b."
                )
            }

        if a == b:
            return {
                "error": (
                    "Los límites de integración no pueden ser iguales (a = b). "
                    "Ingresa un intervalo con longitud mayor que cero."
                )
            }

        if n % 2 != 0:
            n += 1
        
        h = (b - a) / n
        suma_pares = 0
        suma_impares = 0
        
        for i in range(1, n, 2):
            suma_impares += f(a + i * h)
        
        for i in range(2, n - 1, 2):
            suma_pares += f(a + i * h)
        
        integral = (h / 3) * (f(a) + 4 * suma_impares + 2 * suma_pares + f(b))
        
        return {
            "integral": integral,
            "metodo": "Regla de Simpson 1/3",
            "subintervalos": n,
            "ancho_intervalo": h
        }

    @staticmethod
    def simpson_3_8(f: Callable, a: float, b: float, n: int = 99) -> dict:
        """
        Regla de Simpson 3/8
        
        Args:
            f: Función a integrar
            a, b: Límites de integración
            n: Número de subintervalos (debe ser múltiplo de 3)
            
        Returns:
            Valor de la integral
        """
        if a > b:
            return {
                "error": (
                    "El límite inferior a no puede ser mayor al superior b. "
                    "Intercambia los valores de a y b."
                )
            }

        if a == b:
            return {
                "error": (
                    "Los límites de integración no pueden ser iguales (a = b). "
                    "Ingresa un intervalo con longitud mayor que cero."
                )
            }

        if n % 3 != 0:
            n = ((n // 3) + 1) * 3
        
        h = (b - a) / n
        suma_3k = 0
        suma_otros = 0
        
        for i in range(1, n):
            if i % 3 == 0:
                suma_3k += f(a + i * h)
            else:
                suma_otros += f(a + i * h)
        
        integral = (3 * h / 8) * (f(a) + 3 * suma_otros + 2 * suma_3k + f(b))
        
        return {
            "integral": integral,
            "metodo": "Regla de Simpson 3/8",
            "subintervalos": n,
            "ancho_intervalo": h
        }

    # ====================== MÉTODOS PARA SISTEMAS LINEALES ======================

    @staticmethod
    def eliminacion_gaussiana(A: List[List[float]], b: List[float]) -> dict:
        """
        Eliminación Gaussiana simple
        
        Args:
            A: Matriz de coeficientes
            b: Vector de términos independientes
            
        Returns:
            Vector solución
        """
        n = len(A)
        
        # Crear copia para no modificar original
        A = [fila[:] for fila in A]
        b = b[:]
        
        # Eliminación hacia adelante
        for k in range(n - 1):
            # Buscar pivote
            max_idx = k
            for i in range(k + 1, n):
                if abs(A[i][k]) > abs(A[max_idx][k]):
                    max_idx = i
            
            # Intercambiar filas
            A[k], A[max_idx] = A[max_idx], A[k]
            b[k], b[max_idx] = b[max_idx], b[k]
            
            if abs(A[k][k]) < 1e-10:
                return {"error": "Matriz singular"}
            
            for i in range(k + 1, n):
                factor = A[i][k] / A[k][k]
                for j in range(k, n):
                    A[i][j] -= factor * A[k][j]
                b[i] -= factor * b[k]
        
        # Sustitución hacia atrás
        x = [0] * n
        for i in range(n - 1, -1, -1):
            x[i] = b[i]
            for j in range(i + 1, n):
                x[i] -= A[i][j] * x[j]
            x[i] /= A[i][i]
        
        return {
            "solucion": [round(xi, 8) for xi in x],
            "metodo": "Eliminación Gaussiana",
            "numero_ecuaciones": n
        }

    @staticmethod
    def gauss_seidel(A: List[List[float]], b: List[float], x0: List[float] = None, 
                     tol: float = 1e-6, max_iter: int = 100) -> dict:
        """
        Método de Gauss-Seidel
        
        Args:
            A: Matriz de coeficientes
            b: Vector de términos independientes
            x0: Aproximación inicial
            tol: Tolerancia
            max_iter: Máximo de iteraciones
            
        Returns:
            Vector solución
        """
        n = len(A)
        
        if x0 is None:
            x0 = [0] * n
        
        x = x0[:]
        resultados = []
        
        for iteracion in range(max_iter):
            x_anterior = x[:]
            
            for i in range(n):
                suma = b[i]
                for j in range(n):
                    if i != j:
                        suma -= A[i][j] * x[j]
                x[i] = suma / A[i][i]
            
            error = max(abs(x[i] - x_anterior[i]) for i in range(n))
            
            resultados.append({
                "iteracion": iteracion + 1,
                "solucion": [round(xi, 6) for xi in x],
                "error": round(error, 8)
            })
            
            if error < tol:
                return {
                    "solucion": [round(xi, 8) for xi in x],
                    "iteraciones": iteracion + 1,
                    "error_final": error,
                    "resultados": resultados,
                    "metodo": "Gauss-Seidel"
                }
        
        return {
            "solucion": [round(xi, 8) for xi in x],
            "iteraciones": max_iter,
            "error_final": error,
            "resultados": resultados,
            "advertencia": "Se alcanzó máximo de iteraciones",
            "metodo": "Gauss-Seidel"
        }

    # ====================== MÉTODOS DE DERIVACIÓN NUMÉRICA ======================

    @staticmethod
    def diferencia_progresiva(f: Callable, x: float, h: float = 1e-5) -> dict:
        """
        Derivada por Diferencia Progresiva
        
        Args:
            f: Función
            x: Punto donde se calcula la derivada
            h: Paso
            
        Returns:
            Valor de la derivada
        """
        derivada = (f(x + h) - f(x)) / h
        
        return {
            "derivada": derivada,
            "metodo": "Diferencia Progresiva",
            "punto": x,
            "paso": h
        }

    @staticmethod
    def diferencia_regresiva(f: Callable, x: float, h: float = 1e-5) -> dict:
        """
        Derivada por Diferencia Regresiva
        
        Args:
            f: Función
            x: Punto donde se calcula la derivada
            h: Paso
            
        Returns:
            Valor de la derivada
        """
        derivada = (f(x) - f(x - h)) / h
        
        return {
            "derivada": derivada,
            "metodo": "Diferencia Regresiva",
            "punto": x,
            "paso": h
        }

    @staticmethod
    def diferencia_central(f: Callable, x: float, h: float = 1e-5) -> dict:
        """
        Derivada por Diferencia Central
        
        Args:
            f: Función
            x: Punto donde se calcula la derivada
            h: Paso
            
        Returns:
            Valor de la derivada
        """
        derivada = (f(x + h) - f(x - h)) / (2 * h)
        
        return {
            "derivada": derivada,
            "metodo": "Diferencia Central",
            "punto": x,
            "paso": h
        }

    # ====================== ECUACIONES DIFERENCIALES ======================

    @staticmethod
    def euler(f: Callable, x0: float, y0: float, xf: float, h: float = 0.1) -> dict:
        """
        Método de Euler para EDO dy/dx = f(x, y)
        
        Args:
            f: Función f(x, y)
            x0, y0: Condición inicial
            xf: Valor final de x
            h: Paso
            
        Returns:
            Aproximaciones
        """
        resultados = []
        x = x0
        y = y0
        
        while x <= xf:
            resultados.append({
                "x": round(x, 8),
                "y": round(y, 8)
            })
            
            y = y + h * f(x, y)
            x = x + h
        
        return {
            "resultados": resultados,
            "metodo": "Euler",
            "paso": h,
            "puntos": len(resultados)
        }

    @staticmethod
    def runge_kutta_4(f: Callable, x0: float, y0: float, xf: float, h: float = 0.1) -> dict:
        """
        Método de Runge-Kutta de orden 4 para EDO dy/dx = f(x, y)
        
        Args:
            f: Función f(x, y)
            x0, y0: Condición inicial
            xf: Valor final de x
            h: Paso
            
        Returns:
            Aproximaciones
        """
        resultados = []
        x = x0
        y = y0
        
        while x <= xf:
            resultados.append({
                "x": round(x, 8),
                "y": round(y, 8)
            })
            
            k1 = h * f(x, y)
            k2 = h * f(x + h / 2, y + k1 / 2)
            k3 = h * f(x + h / 2, y + k2 / 2)
            k4 = h * f(x + h, y + k3)
            
            y = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6
            x = x + h
        
        return {
            "resultados": resultados,
            "metodo": "Runge-Kutta Orden 4",
            "paso": h,
            "puntos": len(resultados)
        }


class Consola:
    """Interfaz de consola para los métodos numéricos"""
    
    def __init__(self):
        self.mn = MetodosNumericos()

    def _math_env(self, **kwargs):
        """Entorno para eval: expone sin, cos, tan, pi, e, sqrt, etc. sin prefijo y también math.xxx"""
        env = vars(math).copy()
        env["math"] = math
        env.update(kwargs)
        return env

    def _eval_num(self, texto: str) -> float:
        """Convierte una expresión numérica a float. Acepta: 3.14, pi, math.pi, 2*pi, etc."""
        return float(eval(texto.strip(), self._math_env()))

    def limpiar_pantalla(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def menu_principal(self):
        """Menú principal de la consola"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 15 + "CONSOLA DE MÉTODOS NUMÉRICOS")
            print("=" * 60)
            print("\n1. Métodos para Encontrar Raíces")
            print("2. Interpolación")
            print("3. Integración Numérica")
            print("4. Sistemas de Ecuaciones Lineales")
            print("5. Derivación Numérica")
            print("6. Ecuaciones Diferenciales")
            print("0. Salir")
            print("\n" + "=" * 60)
            
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.menu_raices()
            elif opcion == "2":
                self.menu_interpolacion()
            elif opcion == "3":
                self.menu_integracion()
            elif opcion == "4":
                self.menu_sistemas()
            elif opcion == "5":
                self.menu_derivacion()
            elif opcion == "6":
                self.menu_edo()
            elif opcion == "0":
                print("\n¡Hasta luego!")
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                input("Presiona Enter para continuar...")
    
    def menu_raices(self):
        """Menú para métodos de raíces"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 10 + "MÉTODOS PARA ENCONTRAR RAÍCES")
            print("=" * 60)
            print("\n1. Bisección")
            print("2. Newton-Raphson")
            print("3. Secante")
            print("4. Falsa Posición")
            print("0. Volver al menú principal")
            print("\n" + "=" * 60)
            
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.ejecutar_biseccion()
            elif opcion == "2":
                self.ejecutar_newton()
            elif opcion == "3":
                self.ejecutar_secante()
            elif opcion == "4":
                self.ejecutar_falsa_posicion()
            elif opcion == "0":
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                input("Presiona Enter para continuar...")
    
    def ejecutar_biseccion(self):
        """Ejecuta el método de bisección"""
        self.limpiar_pantalla()
        print("MÉTODO DE BISECCIÓN")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), x**2 - 3*x + 2, cos(x) - x)")
            funcion_str = input("f(x) = ").strip()
            a = self._eval_num(input("Límite inferior (a): "))
            b = self._eval_num(input("Límite superior (b): "))
            tol = float(input("Tolerancia (por defecto 1e-6): ") or "1e-6")
            max_iter = int(input("Máximo de iteraciones (por defecto 100): ") or "100")
            
            f = lambda x: eval(funcion_str, self._math_env(x=x))
            resultado = self.mn.biseccion(f, a, b, tol, max_iter)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_newton(self):
        """Ejecuta el método de Newton-Raphson"""
        self.limpiar_pantalla()
        print("MÉTODO DE NEWTON-RAPHSON")
        print("-" * 60)
        
        try:
            print("Ingresa la función y su derivada en términos de x (ej: sin(x), cos(x), x**2)")
            funcion_str = input("f(x) = ").strip()
            derivada_str = input("f'(x) = ").strip()
            x0 = self._eval_num(input("Aproximación inicial (x0): "))
            tol = float(input("Tolerancia (por defecto 1e-6): ") or "1e-6")
            max_iter = int(input("Máximo de iteraciones (por defecto 100): ") or "100")
            
            f = lambda x: eval(funcion_str, self._math_env(x=x))
            df = lambda x: eval(derivada_str, self._math_env(x=x))
            resultado = self.mn.newton_raphson(f, df, x0, tol, max_iter)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_secante(self):
        """Ejecuta el método de la secante"""
        self.limpiar_pantalla()
        print("MÉTODO DE LA SECANTE")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), cos(x) - x, x**3 - 2)")
            funcion_str = input("f(x) = ").strip()
            x0 = self._eval_num(input("Primera aproximación (x0): "))
            x1 = self._eval_num(input("Segunda aproximación (x1): "))
            tol = float(input("Tolerancia (por defecto 1e-6): ") or "1e-6")
            max_iter = int(input("Máximo de iteraciones (por defecto 100): ") or "100")
            
            f = lambda x: eval(funcion_str, self._math_env(x=x))
            resultado = self.mn.secante(f, x0, x1, tol, max_iter)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_falsa_posicion(self):
        """Ejecuta el método de falsa posición"""
        self.limpiar_pantalla()
        print("MÉTODO DE FALSA POSICIÓN")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), cos(x) - x, x**3 - 2)")
            funcion_str = input("f(x) = ").strip()
            a = self._eval_num(input("Límite inferior (a): "))
            b = self._eval_num(input("Límite superior (b): "))
            tol = float(input("Tolerancia (por defecto 1e-6): ") or "1e-6")
            max_iter = int(input("Máximo de iteraciones (por defecto 100): ") or "100")
            
            f = lambda x: eval(funcion_str, self._math_env(x=x))
            resultado = self.mn.falsa_posicion(f, a, b, tol, max_iter)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def menu_interpolacion(self):
        """Menú para métodos de interpolación"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 15 + "INTERPOLACIÓN")
            print("=" * 60)
            print("\n1. Interpolación de Lagrange")
            print("2. Interpolación de Newton (Diferencias Divididas)")
            print("0. Volver al menú principal")
            print("\n" + "=" * 60)
            
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.ejecutar_lagrange()
            elif opcion == "2":
                self.ejecutar_newton_interp()
            elif opcion == "0":
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                input("Presiona Enter para continuar...")
    
    def ejecutar_lagrange(self):
        """Ejecuta interpolación de Lagrange"""
        self.limpiar_pantalla()
        print("INTERPOLACIÓN DE LAGRANGE")
        print("-" * 60)
        
        try:
            n = int(input("¿Cuántos puntos tienes? "))
            puntos = []
            
            for i in range(n):
                x = float(input(f"x{i}: "))
                y = float(input(f"y{i}: "))
                puntos.append((x, y))
            
            x_interp = float(input("¿En qué punto deseas interpolar? "))
            resultado = self.mn.lagrange(puntos, x_interp)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_newton_interp(self):
        """Ejecuta interpolación de Newton"""
        self.limpiar_pantalla()
        print("INTERPOLACIÓN DE NEWTON (DIFERENCIAS DIVIDIDAS)")
        print("-" * 60)
        
        try:
            n = int(input("¿Cuántos puntos tienes? "))
            puntos = []
            
            for i in range(n):
                x = float(input(f"x{i}: "))
                y = float(input(f"y{i}: "))
                puntos.append((x, y))
            
            x_interp = float(input("¿En qué punto deseas interpolar? "))
            resultado = self.mn.diferencias_divididas(puntos, x_interp)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def menu_integracion(self):
        """Menú para métodos de integración"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 12 + "INTEGRACIÓN NUMÉRICA")
            print("=" * 60)
            print("\n1. Regla del Trapecio")
            print("2. Regla de Simpson 1/3")
            print("3. Regla de Simpson 3/8")
            print("0. Volver al menú principal")
            print("\n" + "=" * 60)
            
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.ejecutar_trapecio()
            elif opcion == "2":
                self.ejecutar_simpson_13()
            elif opcion == "3":
                self.ejecutar_simpson_38()
            elif opcion == "0":
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                input("Presiona Enter para continuar...")
    
    def ejecutar_trapecio(self):
        """Ejecuta la regla del trapecio"""
        self.limpiar_pantalla()
        print("REGLA DEL TRAPECIO")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), x**2, exp(x), cos(x))")
            print("Funciones disponibles: sin, cos, tan, exp, log, sqrt, pi, e, etc.")
            funcion_str = input("f(x) = ").strip()
            a = self._eval_num(input("Límite inferior (a): "))
            b = self._eval_num(input("Límite superior (b): "))
            n = int(input("Número de subintervalos (por defecto 100): ") or "100")
            
            f = lambda x: eval(funcion_str, self._math_env(x=x))
            resultado = self.mn.trapecio(f, a, b, n)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_simpson_13(self):
        """Ejecuta la regla de Simpson 1/3"""
        self.limpiar_pantalla()
        print("REGLA DE SIMPSON 1/3")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), x**2, exp(x), cos(x))")
            funcion_str = input("f(x) = ").strip()
            a = self._eval_num(input("Límite inferior (a): "))
            b = self._eval_num(input("Límite superior (b): "))
            n = int(input("Número de subintervalos (por defecto 100): ") or "100")
            
            f = lambda x: eval(funcion_str, self._math_env(x=x))
            resultado = self.mn.simpson_1_3(f, a, b, n)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_simpson_38(self):
        """Ejecuta la regla de Simpson 3/8"""
        self.limpiar_pantalla()
        print("REGLA DE SIMPSON 3/8")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), x**2, exp(x), cos(x))")
            funcion_str = input("f(x) = ").strip()
            a = self._eval_num(input("Límite inferior (a): "))
            b = self._eval_num(input("Límite superior (b): "))
            n = int(input("Número de subintervalos (por defecto 99): ") or "99")
            
            f = lambda x: eval(funcion_str, self._math_env(x=x))
            resultado = self.mn.simpson_3_8(f, a, b, n)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def menu_sistemas(self):
        """Menú para métodos de sistemas lineales"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 8 + "SISTEMAS DE ECUACIONES LINEALES")
            print("=" * 60)
            print("\n1. Eliminación Gaussiana")
            print("2. Método de Gauss-Seidel")
            print("0. Volver al menú principal")
            print("\n" + "=" * 60)
            
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.ejecutar_gaussiana()
            elif opcion == "2":
                self.ejecutar_gauss_seidel()
            elif opcion == "0":
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                input("Presiona Enter para continuar...")
    
    def ejecutar_gaussiana(self):
        """Ejecuta eliminación gaussiana"""
        self.limpiar_pantalla()
        print("ELIMINACIÓN GAUSSIANA")
        print("-" * 60)
        
        try:
            n = int(input("¿Cuántas ecuaciones tienes? "))
            print("\nIngresa la matriz de coeficientes (Ax = b)")
            
            A = []
            b = []
            
            for i in range(n):
                print(f"\nEcuación {i + 1}:")
                fila = []
                for j in range(n):
                    coef = float(input(f"a[{i+1}][{j+1}] = "))
                    fila.append(coef)
                A.append(fila)
                termino = float(input(f"b[{i+1}] = "))
                b.append(termino)
            
            resultado = self.mn.eliminacion_gaussiana(A, b)
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_gauss_seidel(self):
        """Ejecuta el método de Gauss-Seidel"""
        self.limpiar_pantalla()
        print("MÉTODO DE GAUSS-SEIDEL")
        print("-" * 60)
        
        try:
            n = int(input("¿Cuántas ecuaciones tienes? "))
            print("\nIngresa la matriz de coeficientes (Ax = b)")
            
            A = []
            b = []
            x0 = []
            
            for i in range(n):
                print(f"\nEcuación {i + 1}:")
                fila = []
                for j in range(n):
                    coef = float(input(f"a[{i+1}][{j+1}] = "))
                    fila.append(coef)
                A.append(fila)
                termino = float(input(f"b[{i+1}] = "))
                b.append(termino)
            
            print("\nAproximación inicial (opcional, puedes decir 0 para todas):")
            for i in range(n):
                valor = float(input(f"x0[{i+1}] = ") or "0")
                x0.append(valor)
            
            tol = float(input("Tolerancia (por defecto 1e-6): ") or "1e-6")
            max_iter = int(input("Máximo de iteraciones (por defecto 100): ") or "100")
            
            resultado = self.mn.gauss_seidel(A, b, x0, tol, max_iter)
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def menu_derivacion(self):
        """Menú para métodos de derivación"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 15 + "DERIVACIÓN NUMÉRICA")
            print("=" * 60)
            print("\n1. Diferencia Progresiva")
            print("2. Diferencia Regresiva")
            print("3. Diferencia Central")
            print("0. Volver al menú principal")
            print("\n" + "=" * 60)
            
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.ejecutar_diferencia_progresiva()
            elif opcion == "2":
                self.ejecutar_diferencia_regresiva()
            elif opcion == "3":
                self.ejecutar_diferencia_central()
            elif opcion == "0":
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                input("Presiona Enter para continuar...")
    
    def ejecutar_diferencia_progresiva(self):
        """Ejecuta diferencia progresiva"""
        self.limpiar_pantalla()
        print("DIFERENCIA PROGRESIVA")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), x**2, exp(x), cos(x))")
            funcion_str = input("f(x) = ").strip()
            x = self._eval_num(input("Punto (x): "))
            h = float(input("Paso (h, por defecto 1e-5): ") or "1e-5")
            
            f = lambda t: eval(funcion_str, self._math_env(x=t))
            resultado = self.mn.diferencia_progresiva(f, x, h)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_diferencia_regresiva(self):
        """Ejecuta diferencia regresiva"""
        self.limpiar_pantalla()
        print("DIFERENCIA REGRESIVA")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), x**2, exp(x), cos(x))")
            funcion_str = input("f(x) = ").strip()
            x = self._eval_num(input("Punto (x): "))
            h = float(input("Paso (h, por defecto 1e-5): ") or "1e-5")
            
            f = lambda t: eval(funcion_str, self._math_env(x=t))
            resultado = self.mn.diferencia_regresiva(f, x, h)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_diferencia_central(self):
        """Ejecuta diferencia central"""
        self.limpiar_pantalla()
        print("DIFERENCIA CENTRAL")
        print("-" * 60)
        
        try:
            print("Ingresa la función en términos de x (ej: sin(x), x**2, exp(x), cos(x))")
            funcion_str = input("f(x) = ").strip()
            x = self._eval_num(input("Punto (x): "))
            h = float(input("Paso (h, por defecto 1e-5): ") or "1e-5")
            
            f = lambda t: eval(funcion_str, self._math_env(x=t))
            resultado = self.mn.diferencia_central(f, x, h)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def menu_edo(self):
        """Menú para ecuaciones diferenciales"""
        while True:
            self.limpiar_pantalla()
            print("=" * 60)
            print(" " * 10 + "ECUACIONES DIFERENCIALES ORDINARIAS")
            print("=" * 60)
            print("\n1. Método de Euler")
            print("2. Método de Runge-Kutta (Orden 4)")
            print("0. Volver al menú principal")
            print("\n" + "=" * 60)
            
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "1":
                self.ejecutar_euler()
            elif opcion == "2":
                self.ejecutar_runge_kutta()
            elif opcion == "0":
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                input("Presiona Enter para continuar...")
    
    def ejecutar_euler(self):
        """Ejecuta el método de Euler"""
        self.limpiar_pantalla()
        print("MÉTODO DE EULER")
        print("-" * 60)
        print("Resuelve: dy/dx = f(x, y)")
        print()
        
        try:
            print("Ingresa la función en términos de x e y (ej: x + y, sin(x)*y, x**2 - y)")
            funcion_str = input("f(x, y) = ").strip()
            x0 = self._eval_num(input("x0: "))
            y0 = self._eval_num(input("y0: "))
            xf = self._eval_num(input("Valor final de x (xf): "))
            h = float(input("Paso (h, por defecto 0.1): ") or "0.1")
            
            f = lambda x, y: eval(funcion_str, self._math_env(x=x, y=y))
            resultado = self.mn.euler(f, x0, y0, xf, h)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def ejecutar_runge_kutta(self):
        """Ejecuta el método de Runge-Kutta"""
        self.limpiar_pantalla()
        print("MÉTODO DE RUNGE-KUTTA (ORDEN 4)")
        print("-" * 60)
        print("Resuelve: dy/dx = f(x, y)")
        print()
        
        try:
            print("Ingresa la función en términos de x e y (ej: x + y, sin(x)*y, x**2 - y)")
            funcion_str = input("f(x, y) = ").strip()
            x0 = self._eval_num(input("x0: "))
            y0 = self._eval_num(input("y0: "))
            xf = self._eval_num(input("Valor final de x (xf): "))
            h = float(input("Paso (h, por defecto 0.1): ") or "0.1")
            
            f = lambda x, y: eval(funcion_str, self._math_env(x=x, y=y))
            resultado = self.mn.runge_kutta_4(f, x0, y0, xf, h)
            
            self.mostrar_resultado(resultado)
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def mostrar_resultado(self, resultado: dict):
        """Muestra los resultados de forma ordenada"""
        print("\n" + "=" * 60)
        print("RESULTADOS:")
        print("=" * 60)
        
        if "error" in resultado:
            print(f"❌ Error: {resultado['error']}")
            return
        
        # Mostrar resultados principales
        for clave, valor in resultado.items():
            if clave not in ["resultados"]:
                if isinstance(valor, float):
                    print(f"{clave}: {valor:.8f}")
                else:
                    print(f"{clave}: {valor}")
        
        # Mostrar tabla de resultados si existe
        if "resultados" in resultado:
            print("\n" + "-" * 60)
            print("DETALLE DE ITERACIONES:")
            print("-" * 60)
            
            resultados = resultado["resultados"]
            if resultados:
                # Imprimir encabezados
                primer_item = resultados[0]
                encabezados = list(primer_item.keys())
                
                # Calcular ancho de columnas
                anchos = {col: max(len(str(col)), max(len(str(item.get(col, ""))) for item in resultados)) 
                         for col in encabezados}
                
                # Imprimir encabezados
                encabezado = " | ".join(f"{col:^{anchos[col]}}" for col in encabezados)
                print(encabezado)
                print("-" * len(encabezado))
                
                # Imprimir filas (máximo 20 primeras iteraciones)
                for i, item in enumerate(resultados[:20]):
                    fila = " | ".join(f"{str(item.get(col, '')):^{anchos[col]}}" for col in encabezados)
                    print(fila)
                
                if len(resultados) > 20:
                    print(f"\n... ({len(resultados) - 20} filas más)")


def main():
    """Función principal"""
    consola = Consola()
    consola.menu_principal()


if __name__ == "__main__":
    main()
