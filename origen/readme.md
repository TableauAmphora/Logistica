# Logistica en Schema Origen 

A continuación vamos a describir los distintos flujos de informacion desde las distintas fuentes de la organización. 





## Cambiando el retail: Seguimiento de ordenes de compra. 


 * **wms**:  Se Utiliza query dada por Roberto Montenegro para obtener toda la información desde el wms. La query captura informacion de la venta, del pedido, de la caja y de la orden de transporte.  

 * **Promesas de Entrega Transportistas**: Se agrega información gestionada por Fernando Valencia con los ejecutivos de cada Transportista (ChileExpress, BlueExpress y Correos de Chile) de forma anual. Se carga la informacion en las siguientes tablas del schema **origen** (mediante snapshots de cada archivo): 
    - dim2_promesas_chx: Promesas enviadas por chile express 
    - dim2_promesas_bex: Promesas enviadas por blue express 
    - dim2_promesas_cch: Promesas de chile express

    las promesas luego se consolidan en dwh.dim2_promesas_servicios_transportistas 

* todo se consolida en reportes.logistica_wms_rm 


## Costos logísticos

Reporte realizado mediante un notebook en conjunto con Rodrigo Araya y posteriormente modificadas con Roberto Montenegro. 

La salida de este documento es un archivo excel. 