# ADR-001: ThdoraApiClient como Singleton con httpx compartido

**Fecha**: 2026-03-15  
**Estado**: Aceptado  
**Autores**: @alvarofernandezmota-tech

## Contexto

El bot PTB instancia múltiples handlers, cada uno importa `ThdoraApiClient`. Sin control, cada instancia abriría su propio `httpx.AsyncClient` con su propio pool de conexiones, causando:
- Demasiados sockets abiertos simultáneamente
- No se reutilizan conexiones keep-alive a la API
- Difícil cerrar limpiamente en `_post_shutdown`

## Decisión

`ThdoraApiClient` almacena el `httpx.AsyncClient` a nivel de **clase** (`_client: ClassVar`), no de instancia. Cualquier instancia `ThdoraApiClient()` comparte el mismo cliente HTTP subyacente.

Se puede usar directamente (`api = ThdoraApiClient()`) o como singleton explícito (`await ThdoraApiClient.get_instance()`). Ambas formas comparten el mismo `_client`.

## Consecuencias

**Positivas:**
- Un solo pool de conexiones para todo el bot
- Reutilización de conexiones keep-alive → menor latencia
- `ThdoraApiClient.close()` cierra limpiamente desde `_post_shutdown`

**Negativas:**
- Estado compartido entre tests → necesita `ThdoraApiClient._client = AsyncMock()` en fixtures
- No apto para multi-tenant sin modificaciones

## Alternativas rechazadas

- **DI (inyección de dependencias)**: mayor complejidad, innecesaria para bot single-process
- **httpx.Client global**: no async, bloquea el event loop
