-- Extrae historial de observaciones de estado a nivel de OC (v_orcom_observacion / shop_orcom),
-- con fecha_observacion real -- a diferencia de sap_documento.estado (sql_wms_oc.sql), que no
-- trae timestamp propio de cambio. Fuente separada 'orcom' (ver V203), no se mezcla con 'oc'.
select
    tp.idsapdoc,
    orcom.estado_orcom,
    orcom.observacion,
    orcom.fecha_observacion,
    orcom.usuario
from v_orcom_observacion orcom
join tiendaprioridad tp on tp.id = orcom.tiendaprioridad_id
where orcom.fecha_observacion >= %s
