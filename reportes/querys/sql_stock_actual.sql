DROP TABLE IF EXISTS reportes.stock_actual; 
CREATE TABLE IF NOT EXISTS reportes.stock_actual AS
--TRUNCATE TABLE reportes.stock_actual; 
--INSERT INTO reportes.stock_actual  
with ofertas as (
select 
	o.producto_id, o.bodega_id, 
	min(o.precio) as precio	
from dwh.hechos_ofertas o 
where o.fecha_hasta is null  -- ofertas vigentes
group by o.producto_id, o.bodega_id
)
select 
	e.nombre as empresa, 
	b.tipo as tipo_bodega, 
	su.codigo || ' - ' || su.nombre as sucursal,
	b.codigo || ' - ' || b.nombre as bodega,
	bd.codigo || ' - ' || bd.nombre as bodega_detalle,
	bd.seleccion, 
	p.sku, 
	p.descripcion_detalle, 
	p.descripcion,
	p.sku || ' - ' || p.descripcion_detalle as sku_producto, 
	p.marca, 
	p.estilo, 
	p.linea, 
	p.estilo || ' - ' || p.linea as estilo_linea, 
	p.proveedor, 
	p.perfil, 
	p.material, 
	p.imagen, 
	p.seccion, 
	p.categoria, 
	p.subcategoria, 
	p.categoria_comex, 
	p.tendencia, 
	p.talla, 
	p.tamaño, 
	st.codigo as temporada_detalle, 
	st.estado as estado_temporada, 
	st.orden as orden_temporada_detalle, 
	t.codigo as temporada, 
	t.orden as orden_temporada, 
	case when col.codigo = col.nombre then col.codigo else col.codigo || ' - ' || col.nombre end as color_detalle, 
	col.nombre as color, 
	fam.codigo || ' - ' || fam.nombre as familia_detalle, 
	fam.grupo as familia, 
	s.estado, --as estado_stock, 
	bd.tipo_stock, 
	s.fuente as fuente_stock, 
	s.cantidad as stock,
	c.precio as costo,
	pl.precio as precio_lista,
	coalesce(pi_inter.precio, pi_retail.precio) as precio_inicial, 
	o.precio as precio_mejor_oferta, 
	s.fecha_actualizacion_origen
from 
	dwh.hechos_stock s left join  
	dwh.dim_empresas e on s.empresa_id = e.id left join 
	dwh.dim_bodegas_detalle bd on bd.id = s.bodega_detalle_id left join 
	dwh.dim_bodegas b on b.id = bd.bodega_id left join 
	dwh.dim_sucursales su on su.id = b.sucursal_id left join 
	dwh.dim_productos p on p.id = s.producto_id left join 
	dwh.dim_subtemporadas st on st.id = p.temporada_id left join
	dwh.dim_temporadas t on st.temporada_id = t.id left join 
	dwh.dim_colores col on col.id = p.color_id left join 
	dwh.dim_familias fam on fam.id = p.subfamilia_id left join 
	dwh.hechos_costos c on c.producto_id = s.producto_id and c.bodega_id = b.id and c.fecha_hasta is null left join --costos vigentes
	ofertas o on o.producto_id = s.producto_id and o.bodega_id = b.id left join 
	dwh.dim_centros_costos cc on cc.id = bd.centro_costo_id left join 
	dwh.hechos_precios pl on pl.lista_id = cc.lista_precio_id and pl.producto_id = s.producto_id and pl.fecha_hasta is null left join 
	dwh.hechos_precios pi_inter on pi_inter.lista_id = 4 and pi_inter.producto_id = s.producto_id and pi_inter.fecha_hasta is null left join -- iniciales interandina
	dwh.hechos_precios pi_retail on pi_retail.lista_id = 6 and pi_retail.producto_id = s.producto_id and pi_retail.fecha_hasta is null; -- iniciales retailsud  6???











