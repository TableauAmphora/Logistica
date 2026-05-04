with servicio_transporte as (
	select 
		st.id as servicio_id, 
		st.nombre as "nombre_servicio",
		t.nombre as nombre_transportista
	from 
		dwh.dim_servicios_transportistas st left join 
		dwh.dim_transportistas t on t.id = st.transportista_id
), localidades as (
	select 
		g4.nombre as localidad,
		dwh.limpiar_localidad(g4.nombre) as localidad_standar,
		g4.codigo, 
		g4.lat,
		g4.lon
	from 
		dwh.dim_geografia_nivel4 g4 left join 
		dwh.dim_geografia_nivel3 g3 on g3.id = g4.nivel3_id
), promesas as (
	select 
		st.servicio_wms, 
		st.id as servicio_id, 
		g4.nombre as localidad,
		dwh.limpiar_localidad(g4.nombre) as localidad_standar,
		g4.codigo, 
		pst.fecha_desde, 
		coalesce(pst.fecha_hasta, current_timestamp + interval '30 days') as fecha_hasta,
		st.nombre as "nombre_servicio",
		t.nombre as nombre_transportista, 
		g4.lat,
		g4.lon, 
		pst.nro_dias 
	from 
		dwh.dim2_promesas_servicios_transportistas pst left join
        dwh.dim_servicios_transportistas st on st.id = pst.servicio_transporte_id left join 
		dwh.dim_transportistas t on t.id = st.transportista_id left join 
		dwh.dim_geografia_nivel4 g4 on g4.id = pst.geo4_destino_id   left join 
		dwh.dim_geografia_nivel3 g3 on g3.id = g4.nivel3_id
), wms as (
    select 
        *, 
		CASE 
			WHEN servicio_ote = 'BIGT3' THEN 5
			WHEN servicio_ote = 'CHEX'  THEN 6
			WHEN servicio_ote = 'XTEN'  THEN 9
			WHEN servicio_ote = 'XTRE'  THEN 7
			WHEN cod_servicio = '3' THEN 6  
		    WHEN cod_servicio = 'PY' THEN 2
			WHEN cod_servicio = '24' THEN 3
		END as wms_servicio_dwh, 
        dwh.limpiar_localidad(localidad) as localidad_standar_wms
    from   
        origen.hechos_logistica_wms_rm wms
)
--select * from servicio_transporte;
select 
    wms.*, 
    p.nro_dias as dias_promesa,
    l.localidad_standar as localidad_standar_dwh,
	st.nombre_servicio, 
	st.nombre_transportista
from 
    wms left join 
	servicio_transporte st on st.servicio_id = wms.wms_servicio_dwh left join 
	localidades l on l.localidad_standar = wms.localidad_standar_wms left join
    promesas p on p.servicio_id = st.servicio_id and p.localidad_standar = l.localidad_standar  and wms.fecha_compra between p.fecha_desde and p.fecha_hasta