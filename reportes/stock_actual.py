from config.config import sql_stock_actual_reportes 
from config.conexiones import ejecutar_query, cargar_log
from datetime import datetime 




def actualizar_reporte_stock_actual(flujo_id = 16, sql = sql_stock_actual_reportes):
    try: 
        estado = 'OK'
        mensaje = None 
        inicio_log = datetime.now()
        try:             
            sql_stock = open(sql_stock_actual_reportes, "r", encoding="utf-8").read()
            ejecutar_query('dwh', sql_stock) 
        except Exception as e: 
            mensaje = f"Error al renovar datos para el reporte de stock actual."
            raise Exception(mensaje) 
    except Exception as e: 
        estado = 'FAIL'
        mensaje = str(e)
    finally: 
        fin_log = datetime.now()
        log_id = cargar_log(flujo_id, inicio_log, fin_log,estado=estado, mensaje=mensaje, exit = False)
        return estado, mensaje, log_id



if __name__ == '__main__':
    e,m,log = actualizar_reporte_stock_actual()
    print(e,m,log)







