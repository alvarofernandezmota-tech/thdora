# ADR-002: user_id obligatorio en cada llamada a la API

**Fecha**: 2026-04-10  
**Estado**: Aceptado  
**Autores**: @alvarofernandezmota-tech

## Contexto

El bot originalmente pasaba el `user_id` en algunos endpoints y no en otros. Esto causaba que la API devolviera datos de todos los usuarios o fallara silenciosamente. Los bugs B12-B25 son todos consecuencia de esta inconsistencia.

## Decisión

Todo método de `ThdoraApiClient` que accede a datos de usuario **requiere `user_id: int`** como parámetro explícito. El método interno `_request()` llama a `_validate_user_id()` que lanza `ValueError` si `user_id <= 0`.

El `user_id` siempre se obtiene de:
- `update.effective_user.id` (en handlers de comando)
- `query.from_user.id` (en callbacks)
- `context.user_data["X_user_id"]` (en pasos intermedios de ConversationHandler)

Nunca de variables globales, configuración o estado de la BD.

## Consecuencias

**Positivas:**
- Aislamiento total de datos por usuario
- Error detectado en Python antes de llegar a la red si `user_id=0`
- Fácil añadir multi-user en el futuro (ya está preparado)

**Negativas:**
- Más verboso: hay que propagar `user_id` por todos los pasos del ConversationHandler
- Tests deben incluir `user_id` válido en todos los mocks

## Alternativas rechazadas

- **JWT / sesiones**: innecesario para bot privado; añade complejidad sin beneficio real
- **user_id en header HTTP**: menos visible y más difícil de trazar en logs
