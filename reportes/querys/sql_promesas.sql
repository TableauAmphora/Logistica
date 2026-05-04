select 
		g1.nombre as región, 
		g2.nombre as provincia,
		g3.nombre as comuna, 
		g4.nombre as localidad,
		pst.geo4_destino_id as localidad_id,
		pst.fecha_desde, 
		coalesce(pst.fecha_hasta, current_timestamp + interval '30 days') as fecha_hasta,
		t.codigo || ' - ' || st.nombre as "servicio",
		t.nombre as transportista, 
		g4.lat,
		g4.lon, 
		pst.nro_dias 
	from 
		dwh.dim2_promesas_servicios_transportistas pst left join
        	dwh.dim_servicios_transportistas st on st.id = pst.servicio_transporte_id left join 
		dwh.dim_transportistas t on t.id = st.transportista_id left join 
		dwh.dim_geografia_nivel4 g4 on g4.id = pst.geo4_destino_id   left join 
		dwh.dim_geografia_nivel3 g3 on g3.id = g4.nivel3_id left join 
		dwh.dim_geografia_nivel2 g2 on g2.id = g3.nivel2_id left join 
		dwh.dim_geografia_nivel1 g1 on g1.id = g2.nivel1_id

