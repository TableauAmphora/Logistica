from config.conexiones import get_consulta, get_engine, ejecutar_query, cargar_log
from config.config import sql_stock_sap_reservas_chile_ods
from datetime import datetime
# import xml.etree.ElementTree as ET



def actualizar_reservas_sap_ods(flujo_id = 7, sql = sql_stock_sap_reservas_chile_ods):
    try: 
        inicio_log = datetime.now()
        mensaje = None 
        estado = 'OK'  
        # obtenemos reservas 
        try:  
            sql_reservas = open(sql, "r", encoding="utf-8").read()
            reservas = get_consulta('dwh', query = sql_reservas) 
            n = len(reservas)
            print("Hemos Obtenido las reservas desde origen")

        except Exception as e: 
            mensaje = f"Problemas al obtener los datos desde el origen \n {e}"
            raise Exception(mensaje)

        # eliminamos datos antiguos
        try:
            ejecutar_query('dwh', """ TRUNCATE TABLE ods.hechos_stock_sap_reservas; """)
        except Exception as e: 
            mensaje = f"Problemas al borrar datos antiguos en la salida ods.hechos_stock_sap_reservas \n {e}"
            raise Exception(mensaje)

        # cargamos nuevos datos.
        try:
            reservas.to_sql('hechos_stock_sap_reservas', get_engine('dwh'), schema= 'ods', if_exists='append', index = False)
        except Exception as e: 
            mensaje = f"Problemas al cargar los datos a ods.hechos_stock_sap_reservas \n {e}"
            raise Exception(mensaje)

    except Exception as e:
        estado = 'FAIL' 
        mensaje = str(e)
        
    finally: 
        fin_log = datetime.now()
        log_id = cargar_log(flujo=flujo_id, fecha_inicio= inicio_log, fecha_fin= fin_log, estado=estado, mensaje=mensaje, exit=True) 
        return estado, mensaje, log_id 




if __name__ == '__main__':
    e,m,log = actualizar_reservas_sap_ods()
    print(e,m,log)















