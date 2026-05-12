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

#origen

sql_wms_rm =  os.path.join(ruta_querys_origen, "sql_wms_rm.sql") 


# reportes 

sql_hechos_logisticos = os.path.join(ruta_querys_reportes, "sql_hechos_logisticos.sql") 
sql_logistica_wms = os.path.join(ruta_querys_reportes, "sql_logistica_wms.sql") 
sql_promesas = os.path.join(ruta_querys_reportes, "sql_promesas.sql") 

#ds 

