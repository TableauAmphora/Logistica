from config.config import sql_wms_rm
from config.conexiones import get_consulta, get_engine, cargar_log
from datetime import datetime
from sqlalchemy import text

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
            engine = get_engine('dwh')
            # TRUNCATE + append en vez de to_sql(if_exists='replace'): "replace" hace
            # DROP TABLE + CREATE TABLE, que desde que reportes.logistica_wms/
            # reportes.logistica_estados quedaron como vistas sobre esta tabla (V241/V242)
            # falla con "DependentObjectsStillExist" (bloqueo real en produccion desde
            # 2026-10-17, 4 corridas FAIL seguidas -- la tabla quedo congelada con datos
            # del 2026-10-16). TRUNCATE conserva la tabla y las vistas dependientes,
            # mismo resultado final (reemplazo completo de los datos).
            with engine.begin() as conexion_truncate:
                conexion_truncate.execute(text("TRUNCATE TABLE origen.hechos_logistica_wms_rm"))
            df.to_sql("hechos_logistica_wms_rm", engine, if_exists = 'append', index = False, schema = 'origen')
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







