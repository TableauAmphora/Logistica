select 
    hp.fecha,
    hp.fecha_siguiente,
    hp.tiempo as intervalo,
    hp.usuario,
    hp.cantidad,
    hp.grupo as grupo_producto,
    hp.actividad,
    hp.canal,
    hp.nombre as colaborador,
    hp.area,
    hp.id_pedido,
    hp.id_inventario,
    hp.nombre_proceso,
    p.nombre
from 
    public.hechos_proceso hp left join 
    public.pedido p on p.id = hp.id_pedido
where 
    hp.fecha between %s and %s