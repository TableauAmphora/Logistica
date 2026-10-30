-- Extrae pedido (oleada de picking) para upsert en dwh.dim_pedidos_wms.
-- Incremental por pedido.fecha (unica fecha disponible; pedido no tiene fecha_actualizacion
-- propia en wms -- ver Etapa 0 del plan de migracion, no se puede detectar cambios de
-- atributos no-estado sin un backfill periodico completo, igual limitacion que
-- productos_sap_interandina.py con las tablas de catalogo de SAP).
select
    id,
    nombre,
    fecha,
    picking,
    case when picking = 'HOJA_RUTA_UNICA' then 'MULTIPRODUCTO' else 'MONOPRODUCTO' end as tipo_pedido,
    fechaproceso,
    fechadespacho,
    estado as estado_actual,
    origen,
    canal_codigo,
    cantidadcajasasignadas as cantidad_cajas_asignadas,
    cantidadproductosporcaja as cantidad_productos_por_caja,
    ordentransportepadre,
    fechacreacionotpadre,
    fechacierreotpadre
from pedido
where fecha >= %s
