select
    sd.fecha as fecha_compra,
    sd.hora as hora_compra,
    sd.centrocosto,
    sd.referencia as nro_oc,
    sd.origenreferencia as canal,
    sd.fechaactualizacion,
    sd.origen as empresa,
    sd.estado as estado_magento,
    sd.tipo as tipo_doc,
    sd.rutcliente,
    sd.numero as num_doc,
    d.comuna as localidad, 
    COALESCE(com.nombre, d.comuna) as comuna,
    COALESCE(reg.nombre, d.region) as region,
    d.cod_servicio,
    d.cod_dpa_comuna,
    d.cod_cobertura,
    ped.nombre as pedido,
    ped.id as id_pedido,
    ped.fecha as fecha_pedido,
    case when ped.picking = 'HOJA_RUTA_UNICA' THEN 'MULTIPRODUCTO'
    ELSE 'MONOPRODUCTO' END as tipo_pedido,
    ped.fechaproceso,
    ped.fechadespacho as f_despacho_pedido,
    case when cd.estado ilike '%despachad%' then cd.fechaestado else tp.fechadespacho + tp.horadespacho end as fecha_despacho, 
    ped.estado as estado_pedido,
    ped.origen,
    ch.nombre as canal_wms,
    cd.id as idd,
    cd.estado as estado_caja,
    cd.fechaestado as fecha_caja,
    cd.ordentransporte,
    cdt.codigo as codigo_caja,
    cdt.descripcion as nombre_caja,
    ((cdt.largo * cdt.ancho * cdt.alto )/1000000)::real as volumen,
    orcom.estado_orcom,
    orcom.observacion,
    peso.peso,
    tp.transporte,
    tp.nombrealternativo as nro_oc_reenvio,
    ote.estado as estado_courrier,
    ote.transportista as transporte_ote,
    ote.descripcion_estado as descripcion_courrier,
    ote.fecha_estado as fecha_courrier,
    ote.fecha_entrega,
    ote.servicio as servicio_ote,  
    'Pedido Original' as Carga,
    sd.cantproductos,
    tcr.estado,
    tcr.fecha_estado as fecha_estado_retiro,
    tp.tiendadespacho_codigo as retiro_tienda
FROM 
    sap_documento sd
    LEFT JOIN tiendaprioridad tp ON tp.idsapdoc = sd.idsapdoc
    LEFT JOIN direccion d ON d.id = tp.direccion_id
    LEFT JOIN pedido ped ON ped.id = tp.pedido_id
    LEFT JOIN canal ch ON ch.codigo = ped.canal_codigo
    LEFT JOIN dpa_comuna com on com.codigo = d.cod_dpa_comuna
    LEFT JOIN dpa_region reg on reg.codigo = com.dpa_region_codigo
    LEFT JOIN cajadespacho cd ON tp.id = cd.tiendaprioridad_id
    LEFT JOIN cajadespachotipo cdt ON cd.cajadespachotipo_codigo = cdt.codigo
    LEFT JOIN v_orcom_observacion orcom ON tp.id = orcom.tiendaprioridad_id
    LEFT JOIN v_peso_caja peso ON cd.id = peso.id_diario
    LEFT JOIN tienda_caja_registro tcr ON sd.referencia = tcr.referencia
    LEFT JOIN (select t1.* 
                FROM public.orden_transporte_estado t1
                    JOIN (select id_caja, max(fecha_estado) as maxestado 
                          FROM orden_transporte_estado 
                          group by id_caja) as t2 on t1.id_caja = t2.id_caja and t1.fecha_estado = t2.maxestado 
                where t1.fecha_estado >= '2025-09-01'
              ) ote ON cd.id = ote.id_caja
WHERE 
    sd.referencia IS NOT NULL AND 
    sd.tipo in ('FRV','OVT') and 
    ped.fecha >= current_date - interval '90 days'




