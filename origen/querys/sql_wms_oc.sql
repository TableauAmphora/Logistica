-- Extrae sap_documento (orden de compra) para upsert en dwh.dim_ordenes_compra_wms.
-- Filtro tipo IN ('FRV','OVT') validado en Etapa 0: STI es traslado interno de stock (1:1
-- contra OWTQ en SAP), no una venta, se excluye a proposito.
-- pedido_id se resuelve via tiendaprioridad (unico camino real: sap_documento -> tiendaprioridad
-- -> pedido). Incremental por fechaactualizacion (fallback a fecha si es NULL).
select
    sd.idsapdoc,
    tp.pedido_id,
    sd.referencia,
    sd.tipo,
    sd.centrocosto,
    sd.origenreferencia,
    sd.estado as estado_actual,
    sd.fecha,
    sd.fechaactualizacion as fecha_actualizacion_origen
from sap_documento sd
left join tiendaprioridad tp on tp.idsapdoc = sd.idsapdoc
where sd.tipo in ('FRV', 'OVT')
  and sd.referencia is not null
  and coalesce(sd.fechaactualizacion, sd.fechacreacion) >= %s
