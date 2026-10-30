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
		g3.codigo as codigo_comuna_dwh, 
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
	st.nombre_transportista,
	-- Dias habiles por tramo, via dwh.hechos_calendario.laborable_cd (dwh.dias_habiles(),
	-- ver DataWareHouse V237/V240) -- reemplaza la lista de feriados que el calculated
	-- field de Tableau trae hardcodeada a mano (Calculation_972777572665954305,
	-- Calculation_5087378754339553319, Calculation_1872934546453196801): cambiar esos 3
	-- calculated fields para que referencien directo estas columnas en vez de recalcular.
	-- Tramo entrega usa COALESCE(fecha_courrier, CURRENT_DATE) para que una OC todavia no
	-- entregada muestre dias corridos hasta hoy (igual criterio "running" que el calc
	-- field original), no NULL -- salvo que fecha_despacho tambien sea NULL (OC no
	-- despachada todavia), en cuyo caso dwh.dias_habiles() devuelve NULL igual.
	dwh.dias_habiles(wms.fecha_compra::date, wms.fecha_pedido::date) as dias_habiles_carga,
	dwh.dias_habiles(wms.fecha_pedido::date, wms.fecha_despacho::date) as dias_habiles_proceso,
	dwh.dias_habiles(wms.fecha_despacho::date, COALESCE(wms.fecha_courrier, CURRENT_DATE)::date) as dias_habiles_entrega
from
    wms left join
	servicio_transporte st on st.servicio_id = wms.wms_servicio_dwh left join
	localidades l on l.localidad_standar = wms.localidad_standar_wms and wms.cod_dpa_comuna = l.codigo_comuna_dwh left join
    promesas p on p.servicio_id = st.servicio_id and p.localidad_standar = l.localidad_standar  and wms.fecha_compra between p.fecha_desde and p.fecha_hasta