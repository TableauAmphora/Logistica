-- Extrae TODO el historico de eventos de orden_transporte_estado en la ventana incremental
-- (a diferencia de pedido/caja, esta tabla SI trae historial real -- multiples filas por
-- id_caja con distinto fecha_estado -- asi que no hace falta comparar contra el ultimo
-- conocido, se cargan todos los eventos nuevos directo).
-- Solo existen filas para "canales propios" (sap_documento.centrocosto IN ('502','602','702','802'));
-- las cajas de marketplace legitimamente no aparecen aca (confirmado en Etapa 0).
--
-- Filtro por fecha_actualizacion (no fecha_estado): fecha_actualizacion es cuando wms tocó
-- la fila por ultima vez (captura tambien correcciones tardias a un evento ya cargado antes,
-- que fecha_estado no reflejaria); fecha_estado sigue siendo la fecha real del evento, se
-- guarda tal cual en dwh.hechos_logistica_estados.
select
    id_caja,
    orden_transporte,
    orden_transporte_padre,
    transportista,
    servicio,
    estado,
    fecha_estado,
    fecha_entrega
from orden_transporte_estado
where fecha_actualizacion >= %s
