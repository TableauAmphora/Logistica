#importamos las librerias que necesitaremos mas adelante

import pandas as pd 
import numpy as np 
from config.conexiones import get_consulta, ejecutar_query, get_engine 
from config.config import sql_hechos_logisticos
from datetime import datetime, timezone, timedelta
import time 
import math 

pd.set_option('display.max_rows',None) 
pd.set_option('display.max_columns', None)   


## parametros fijos

tiempo_muerto = 20
ahora =  datetime.now(timezone.utc)  
fecha_hasta =(ahora - timedelta( days = ahora.day)  ) 


fecha_desde = (fecha_hasta - timedelta(days = fecha_hasta.day - 1)).strftime('%Y-%m-%d')
fecha_hasta = fecha_hasta.strftime('%Y-%m-%d')

def get_datos(flujo_id = 1, query_hechos = sql_hechos_logisticos,  desde = fecha_desde, hasta = fecha_hasta): 
    sql_hechos = open(query_hechos, "r", encoding="utf-8").read()
    hechos = get_consulta('wms', query = sql_hechos, params=(desde, hasta))
    

    return hechos
              




if __name__ == '__main__':
    hechos = get_datos()
    print(hechos.sample(), "\n\n", hechos.columns)
    
