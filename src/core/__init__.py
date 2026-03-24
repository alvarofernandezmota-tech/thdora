"""
Módulo core de THDORA.

Contiene:
- interfaces/  → Contratos abstractos (ABC) que definen el contrato de cada servicio
- impl/        → Implementaciones concretas de esas interfaces
- bot/         → Bot CLI interactivo

Arquitectura: Dependency Inversion — el código de alto nivel depende
de abstracciones (interfaces), no de implementaciones concretas.
"""
