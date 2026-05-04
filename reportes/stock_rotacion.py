from config.config import sql_rotacion_reportes 
from config.conexiones import ejecutar_query, cargar_log
from datetime import datetime 

def actualizar_rotacion(flujo_id = 19, sql_rot = sql_rotacion_reportes):
    try:
        try:
            inicio_log = datetime.now()
            mensaje = None
            estado = 'OK'
            sql_rotacion = open(sql_rot, "r", encoding="utf-8").read()
            ejecutar_query('dwh', sql_rotacion) 
        
        except Exception as e: 
            mensaje = f"Problemas al cargar datos en reportes.stock_rotacion \n {e}"
            raise Exception(mensaje)
        
    except Exception as e:
            estado = 'FAIL'
            mensaje = str(e)

    finally: 
        fin_log = datetime.now()
        log_id = cargar_log(flujo=flujo_id, fecha_inicio= inicio_log, fecha_fin= fin_log, estado=estado, mensaje=mensaje, exit=False)
        return estado, mensaje, log_id

if __name__ == '__main__':
    e,m,log = actualizar_rotacion()
    print(e,m,log)









