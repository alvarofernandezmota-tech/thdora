"""
src/core/ocr
============
Módulo de extracción de números desde imágenes.

Futuro: ImageAgent del CEO OS.

Exporta las dos clases principales para que el resto del ecosistema
pueda importar directamente desde `src.core.ocr`.
"""

from .reader import ImageReader
from .operations import ImageOperations

__all__ = ["ImageReader", "ImageOperations"]
