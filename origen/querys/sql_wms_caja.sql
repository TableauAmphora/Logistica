-- Extrae cajadespacho para upsert en dwh.dim_cajas_wms. Incremental por fechaestado (si una
-- caja cambia de estado, fechaestado se actualiza -- confirmado que es el timestamp real del
-- ultimo cambio, no solo de creacion).
-- pedido_id es columna directa de cajadespacho (no hace falta pasar por tiendaprioridad).
-- orden_transporte_id NO se resuelve aca -- se completa en el loader Python despues de cargar
-- dwh.dim_ordenes_transporte (ver sql_wms_ot.sql y comentario en V193 de la migracion).
select
    id,
    caja_id as caja_id_negocio,
    pedido_id,
    tiendaprioridad_id,
    tienda_codigo,
    cajadespachotipo_codigo,
    transportedespacho_id,
    estado as estado_actual,
    fechaestado as fecha_estado_actual
from cajadespacho
where fechaestado >= %s
