-- Extrae hechos_proceso (actividad operativa: picking/empaque/devoluciones/inventario) para
-- upsert en dwh.hechos_logistica_actividades. Confirmado con datos reales que esta tabla NO
-- tiene columna de caja -- el unico FK real es id_pedido.
select
    id,
    id_pedido,
    fecha,
    fecha_siguiente,
    tiempo,
    usuario,
    nombre as nombre_colaborador,
    cantidad,
    grupo,
    actividad,
    canal,
    area,
    id_inventario,
    nombre_proceso
from hechos_proceso
where fecha >= %s
