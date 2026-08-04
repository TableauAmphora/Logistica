from config.config import sql_wms_rm 
from config.conexiones import get_consulta, get_engine, cargar_log
from datetime import datetime 

def actualizar_hechos_wms_rm(flujo_id= 34, sql = sql_wms_rm):
    try: 
        estado = 'OK'
        mensaje = None 
        inicio_log = datetime.now()
        try:             
            sql = open(sql_wms_rm, "r", encoding="utf-8").read()
            df = get_consulta('wms',sql) 
        except Exception as e: 
            mensaje = f"Error al obtener datos de logistica desde wms. \n {e}"
            raise Exception(mensaje) 
        try:             
            print(df.shape)
            df.to_sql("hechos_logistica_wms_rm", get_engine('dwh'), if_exists = 'replace', index = False, schema = 'origen') 
        except Exception as e:
            mensaje = f"Error al cargar datos de logistica desde wms. \n {e}"
            raise Exception(mensaje)
    except Exception as e: 
        estado = 'FAIL'
        mensaje = str(e)
    finally: 
        fin_log = datetime.now()
        log_id = cargar_log(flujo_id, inicio_log, fin_log,estado=estado, mensaje=mensaje, exit = False)
        return estado, mensaje, log_id

if __name__ == '__main__':
    e,m,log = actualizar_hechos_wms_rm()
    print(e,m,log)







