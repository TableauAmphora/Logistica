# actualizamos stock 

from origen.hechos_query_wms_rm import actualizar_hechos_wms_rm
from reportes.logistica_wms_rm import actualizar_logistica_wms_rm
from config.conexiones import actualizar_libro, get_token_tableau

from datetime import datetime, timedelta


# desde = datetime.now() - 
# hasta = datetime.now() + timedelta(days = 30) 

try: 
    actualizar_hechos_wms_rm() 
    actualizar_logistica_wms_rm()
except: 
    pass 


try: 
    wb_id = 'fd748331-2c91-47b9-9f6f-f341b7b00d40' # cambiando el retail 
    token, site_id = get_token_tableau()
    actualizar_libro(wb_id, token, site_id )
except: 
    pass 








