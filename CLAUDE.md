# Logistica — notas para trabajar en este repo

## Idioma

Responder siempre en español, incluyendo mensajes de commit, resúmenes y explicaciones. Esto aplica a priori, es decir, por defecto desde el primer mensaje, sin esperar a detectar en qué idioma escribe el usuario.

## Prohibido: modificaciones estructurales en wms y dwh

Tienes **estrictamente prohibido hacer modificaciones estructurales** (crear/alterar/eliminar tablas, columnas, schemas, índices, etc.) en las bases **wms** y **dwh**. Si detectas que un flujo o tarea requiere un cambio estructural en alguna de estas dos bases, **no lo ejecutes**: solo informa al usuario qué cambio se necesita y por qué, para que lo aplique él directamente.

## wms es de solo lectura

La base de datos **wms** es de **solo lectura**: tienes **estrictamente prohibido escribirle o modificarla de cualquier forma** (INSERT, UPDATE, DELETE, además de los cambios estructurales ya prohibidos arriba). Todo flujo que toque wms debe limitarse a `SELECT`. Cualquier escritura de datos (cargas, correcciones, sincronizaciones) va siempre hacia **dwh**, nunca hacia wms.

## Timestamps de logs en UTC

`inicio_log`/`fin_log` (y cualquier columna `timestamp with time zone` que setee un flujo) **siempre** deben usar `datetime.now(timezone.utc)`, nunca `datetime.now()` naive. Mezclar hora local y UTC en `control.flujos_logs` rompe la comparación de horarios y duraciones entre flujos (el DWH guarda UTC; un naive de las 01:20 locales queda como 01:20 UTC y al convertir a hora chilena aparece a las 22:20 del día anterior).
