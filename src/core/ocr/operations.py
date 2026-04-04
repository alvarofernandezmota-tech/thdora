"""
src/core/ocr/operations.py
==========================
Operaciones sobre números extraídos de imágenes.

Diseñado para usarse junto con ImageReader:

    reader = ImageReader()
    ops    = ImageOperations()

    a = reader.extraer_numero("imagen_a.png")  # 42.0
    b = reader.extraer_numero("imagen_b.png")  # 18.0
    print(ops.aplicar("Suma", a, b))           # "42.0 + 18.0 = 60.0"
"""


class ImageOperations:
    """
    Operaciones disponibles sobre dos números extraídos de imágenes.
    Extensible: añade métodos y regístralos en OPERACIONES.
    """

    OPERACIONES: list[str] = [
        "Suma",
        "Resta",
        "Multiplicación",
        "División",
        "Comparar",
        "Concatenar",
        "Máximo",
        "Mínimo",
        "Promedio",
    ]

    def aplicar(self, operacion: str, a: float, b: float) -> str:
        """Aplica la operación indicada y devuelve el resultado formateado."""
        metodos = {
            "Suma":           self.sumar,
            "Resta":          self.restar,
            "Multiplicación": self.multiplicar,
            "División":       self.dividir,
            "Comparar":       self.comparar,
            "Concatenar":     self.concatenar,
            "Máximo":         self.maximo,
            "Mínimo":         self.minimo,
            "Promedio":       self.promedio,
        }
        if operacion not in metodos:
            raise ValueError(
                f"Operación desconocida: '{operacion}'. "
                f"Disponibles: {self.OPERACIONES}"
            )
        return metodos[operacion](a, b)

    def sumar(self, a: float, b: float) -> str:
        return f"{a} + {b} = {a + b}"

    def restar(self, a: float, b: float) -> str:
        return f"{a} - {b} = {a - b}"

    def multiplicar(self, a: float, b: float) -> str:
        return f"{a} × {b} = {a * b}"

    def dividir(self, a: float, b: float) -> str:
        if b == 0:
            return "Error: división entre 0 no permitida"
        return f"{a} ÷ {b} = {round(a / b, 4)}"

    def comparar(self, a: float, b: float) -> str:
        if a > b:    return f"{a} > {b}  →  A es mayor"
        elif a < b:  return f"{a} < {b}  →  B es mayor"
        else:        return f"{a} = {b}  →  Son iguales"

    def concatenar(self, a: float, b: float) -> str:
        sa = str(int(a)) if a == int(a) else str(a)
        sb = str(int(b)) if b == int(b) else str(b)
        return f"Concatenación: {sa + sb}"

    def maximo(self, a: float, b: float) -> str:
        return f"Máximo entre {a} y {b}: {max(a, b)}"

    def minimo(self, a: float, b: float) -> str:
        return f"Mínimo entre {a} y {b}: {min(a, b)}"

    def promedio(self, a: float, b: float) -> str:
        return f"Promedio de {a} y {b}: {(a + b) / 2}"
