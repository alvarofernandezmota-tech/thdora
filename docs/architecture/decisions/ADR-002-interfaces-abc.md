# ADR-002: Usar ABC para interfaces

**Fecha:** 2026-03-19  
**Estado:** Aceptado

## Contexto

Necesitamos poder cambiar la implementación de almacenamiento
sin modificar el código que usa el gestor.

## Decisión

Definir `AbstractLifeManager` usando `abc.ABC` y `@abstractmethod`.

## Justificación

- ✅ Python fuerza implementar todos los métodos (error en instanciación)
- ✅ El IDE autocompleta correctamente desde la interfaz
- ✅ Facilita el testing con mocks
- ✅ Patrón estándar Python para interfaces

## Alternativas descartadas

- `Protocol` (typing): más moderno pero menos explícito para aprendizaje
- Sin interfaces: acoplamiento directo, dificulta cambiar implementación
