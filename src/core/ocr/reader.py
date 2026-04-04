"""
src/core/ocr/reader.py
======================
Carga, preprocesa y extrae números de imágenes via OCR.

Dependencias (añadir a requirements.txt cuando se active):
    pillow>=10.0.0
    opencv-python>=4.8.0
    pytesseract>=0.3.10

Tesseract debe estar instalado en el sistema:
    macOS:  brew install tesseract
    Linux:  sudo apt install tesseract-ocr
    Windows: https://github.com/UB-Mannheim/tesseract/wiki
"""

import re
from pathlib import Path

FORMATOS_SOPORTADOS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}


class ImageReader:
    """
    Pipeline: ruta → carga → preprocesado → OCR → lista de floats.

    Uso:
        reader = ImageReader()
        numeros = reader.extraer_numeros("ticket.png")  # [42.0, 7.5]
        primero = reader.extraer_numero("precio.jpg")   # 42.0
    """

    def extraer_numeros(self, ruta: str) -> list[float]:
        """
        Extrae TODOS los números de una imagen.
        Devuelve lista de floats (puede haber más de uno).
        """
        # Import lazy: solo falla si el módulo se usa, no al importar thdora
        try:
            import cv2
            import pytesseract
            import numpy as np
            from PIL import Image
        except ImportError as e:
            raise ImportError(
                f"Dependencia OCR no instalada: {e}. "
                "Ejecuta: pip install pillow opencv-python pytesseract"
            ) from e

        ruta_path = Path(ruta)
        if ruta_path.suffix.lower() not in FORMATOS_SOPORTADOS:
            raise ValueError(
                f"Formato no soportado: {ruta_path.suffix}. "
                f"Formatos válidos: {FORMATOS_SOPORTADOS}"
            )

        img_array = np.array(Image.open(ruta).convert("RGB"))
        procesada = self._preprocesar(img_array, cv2)
        config = "--psm 6 -c tessedit_char_whitelist=0123456789.,-"
        texto = pytesseract.image_to_string(procesada, config=config)
        encontrados = re.findall(r"[\d]+(?:[.,][\d]+)?", texto.replace(",", "."))

        if not encontrados:
            raise ValueError(f"No se encontró ningún número en: {ruta}")

        return [float(n) for n in encontrados]

    def extraer_numero(self, ruta: str) -> float:
        """Extrae el primer número de una imagen."""
        return self.extraer_numeros(ruta)[0]

    @staticmethod
    def _preprocesar(img_array, cv2):
        """Convierte a escala de grises y aplica umbral adaptativo."""
        gris = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        h, w = gris.shape
        if w < 300:
            escala = 300 / w
            gris = cv2.resize(
                gris, None, fx=escala, fy=escala,
                interpolation=cv2.INTER_CUBIC
            )
        return cv2.adaptiveThreshold(
            gris, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
