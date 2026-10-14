from config.config import sql_logistica_wms
from config.conexiones import get_consulta, get_engine, cargar_log, ejecutar_query
from datetime import datetime 




# DESACTIVADO 2026-10-14: bdsap se retira y este flujo solo escribia ahi. Se deja como
# respaldo; para reactivarlo poner ACTIVO = True (y verificar que bdsap este disponible).
ACTIVO = False

def actualizar_logistica_wms_rm(flujo_id= 35, sql = sql_logistica_wms):
    if not ACTIVO:
        return 'SKIP', 'Desactivado: bdsap se retira (ver ACTIVO)', None
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
            # Ya no se escribe en dwh: el destino es bdsap (puente temporal
            # para el Tableau viejo, mientras se resuelve el tema de VPN de
            # acceso a dwh). No hay ninguna app de reporteria que lea esta
            # tabla desde dwh (solo Tableau), asi que no hace falta dual
            # write como en compras/planilla_maestra_sap. El GRANT a
            # rol_tableau sobre dwh ya no aplica -- Tableau va a conectarse
            # directo a bdsap con sus propias credenciales.
            print(df.shape)
            ejecutar_query('bdsap', "CREATE SCHEMA IF NOT EXISTS reportes")
            df.to_sql("logistica_wms_rm", get_engine('bdsap'), if_exists = 'replace', index = False, schema = 'reportes')
        except Exception as e:
            mensaje = f"Error al cargar datos de logistica desde origen a bdsap. \n {e}"
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







