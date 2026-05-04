# actualizamos stock 

from origen.hechos_query_wms_rm import actualizar_hechos_wms_rm
from reportes.logistica_wms_rm import actualizar_logistica_wms_rm

from datetime import datetime, timedelta


# desde = datetime.now() - 
# hasta = datetime.now() + timedelta(days = 30) 

try: 
    actualizar_hechos_wms_rm() 
    actualizar_logistica_wms_rm()
except: 
    pass 










