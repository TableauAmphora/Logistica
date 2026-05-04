from config.config import sql_logistica_wms
from config.conexiones import get_consulta, get_engine, cargar_log, ejecutar_query
from datetime import datetime 




def actualizar_logistica_wms_rm(flujo_id= 35, sql = sql_logistica_wms):
    try: 
        estado = 'OK'
        mensaje = None 
        inicio_log = datetime.now()
        try:             
            sql = open(sql_logistica_wms, "r", encoding="utf-8").read()
            df = get_consulta('dwh',sql) 
        except Exception as e: 
            mensaje = f"Error al obtener datos de logistica desde origen. \n {e}"
            raise Exception(mensaje) 
        try:             
            print(df.shape)
            df.to_sql("logistica_wms_rm", get_engine('dwh'), if_exists = 'replace', index = False, schema = 'reportes') 
        except Exception as e: 
            mensaje = f"Error al cargar datos de logistica desde origen a reportes. \n {e}"
            raise Exception(mensaje) 
        try: 
            sql_permisos = """ GRANT USAGE ON SCHEMA reportes TO rol_tableau;

                                GRANT SELECT
                                ON ALL TABLES IN SCHEMA reportes
                                TO rol_tableau;

                                ALTER DEFAULT PRIVILEGES
                                IN SCHEMA reportes
                                GRANT SELECT ON TABLES TO rol_tableau;
    	    """
            ejecutar_query('dwh', sql_permisos)
        except Exception as e: 
            mensaje = f"Error al otorgar permisos al usuario de tableau. \n {e}"
            raise Exception(mensaje) 
    except Exception as e: 
        estado = 'FAIL'
        mensaje = str(e)
    finally: 
        fin_log = datetime.now()
        log_id = cargar_log(flujo_id, inicio_log, fin_log,estado=estado, mensaje=mensaje, exit = False)
        return estado, mensaje, log_id



if __name__ == '__main__':
    e,m,log = actualizar_logistica_wms_rm()
    print(e,m,log)







