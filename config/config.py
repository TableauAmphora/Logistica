import os
from pathlib import Path

#credenciales 
ruta_credenciales = os.path.join(Path(__file__).resolve().parent, "credenciales.env")


# Definir la raíz del proyecto
raiz = Path(__file__).resolve().parent.parent 


# capas del proyecto 

origen = 'origen' 
ods = 'ods'
warehouse = 'dwh' 
reportes = 'reportes'
control = 'control'

# Rutas a carpetas de querys. 

ruta_querys_origen =  os.path.join(raiz, "origen",  "querys")
ruta_querys_ods =  os.path.join(raiz, "ods",  "querys")
ruta_querys_dwh =  os.path.join(raiz, "dwh",  "querys")
ruta_querys_reportes = os.path.join(raiz, "reportes",  "querys")


############# SQLs 

# origen 
sql_wms_rm = os.path.join(ruta_querys_origen, "sql_wms_rm.sql") 



# ods
sql_stock_sap_reservas_chile_ods =  os.path.join(ruta_querys_ods, "sql_stock_sap_reservas_chile.sql")

# warehouse 

sql_stock_sap_reservas_chile_dwh =  os.path.join(ruta_querys_dwh, "sql_stock_sap_reservas.sql")
sql_stock_sap_chile_dwh =   os.path.join(ruta_querys_dwh, "sql_stock_sap.sql")
sql_precios_dwh = os.path.join(ruta_querys_dwh, "sql_precios.sql")
sql_ofertas_dwh = os.path.join(ruta_querys_dwh, "sql_ofertas.sql")
sql_precios_vigentes_dwh =  os.path.join(ruta_querys_dwh, "sql_precios_vigentes_dwh.sql")
sql_ofertas_vigentes_dwh =  os.path.join(ruta_querys_dwh, "sql_ofertas_vigentes_dwh.sql")

sql_relacion_bodegas_detalle_id = os.path.join(ruta_querys_dwh, "sql_relacion_bodega_detalle.sql")
sql_relacion_bodegas_id = os.path.join(ruta_querys_dwh, "sql_relacion_bodegas.sql")
sql_relacion_producto_id = os.path.join(ruta_querys_dwh, "sql_relacion_producto.sql")
sql_relacion_lista_id = os.path.join(ruta_querys_dwh, "sql_relacion_listas_precios.sql")
sql_relacion_ofertas_id = os.path.join(ruta_querys_dwh, "sql_relacion_ofertas.sql")



# reportes 

sql_logistica_wms = os.path.join(ruta_querys_reportes, "sql_logistica_wms.sql") 
sql_promesas = os.path.join(ruta_querys_reportes, "sql_promesas.sql")



#ds 

