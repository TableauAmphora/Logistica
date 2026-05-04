## Stock  en Schema Origen 

Aqui realizaremos una descripcion de los distintos flujos que se ejecutan relacionados a stock. generalmente desde los ERP de cada empresa hacia el schema origen de nuestro data ware house. 




## Stock Propio 

- Chile: 
 Se carga el stock propio de todas las bodegas, incluyendo tiendas, outlets, falabella, ripley y fulfillment. ademas se incluye stock central de segunda y tercera. Adicionalmente el stock de 1RA curauma (CUR) que posteriormente se descarta utilizando el stock obtenido en conjunto con las reservas.  

 La query se construyo en conjunto con rmontenegro@amphora.cl, aunque se han realizado algunas modificaciones menores.   

 - Perú: 
La info de obtiene mediante query al RMS (sql server) creada por fgonzalez@amphora.cl y sin ninguna verificación real por parte de los encargados de perú. 

- Argentina: 



## Reservas en Bodega Central. 

- Chile: Se extraen desde SAP, utilizando query de saldos otorgada por maballay@amphora.cl. Aqui se incluye rewservas de los distintos canales y tambien el stock de primera en curauma (CUR). 

- Perú: Desconozco si existe el simil. 

- Argentina: sin acceso a sus bbdd.  






## Stock Externo. 


- Origen de datos:
La información se obtiene de forma manual desde los distintos portales seller/B2B de cada cliente.
- Recepción:
Los archivos son enviados por correo electrónico a fgonzalez@amphora.cl. Actualmente los encargados de esta tarea son: 
    1. Falabella Amphora (Responsable: jvillena@amphora.cl): 
        - Asunto del correo: (pendiente de definir)
        - Archivos recibidos:
            - cods_relacion → incluye la relación entre códigos externos e internos.
            - Se cargan en: dwh.relacion_skus
            - ventas diarias → incluye ventas sell out.
            - Se cargan en: origen.hechos_ventas_falabella
            - analisis semanal → incluye stock actual en Falabella.
            - Se cargan en: origen.hechos_stock_falabella
    
    2. Falabella Scalpers:
        Responsable: fgonzalez@amphora.cl
        Asunto: 'ventas sell out falabella scalpers' 
        Archivos:   
           - obs. aqui codigo_falabella == codigo_scalpers, salvo situaciones puntuales que ya han sido cargadas en dwh.relacion_skus. Nuevas situaciones deben verse con fsone@scalpers.cl o bdib@amphora.cl.  
           - ventas = 'ventas diarias': incluye ventas sell out. 
           - stock = 'analisis semanal': incluye stock semanal. 
    3. Perú :
        - Responsable: fgonzalez@amphora.cl 
        - aun no se incluye nada de stock (solo ventas.) 


- Centralización:
    - Estos flujos se encuentran en el repositorio central, ya que siempre se reciben en conjunto con los datos de ventas.
    - Al involucrar más de un área de gestión (ejemplo: stock y ventas), se integran aquí para mantener un único punto de ingestión.



## Costos. 



## Ofertas.


## Precios. 


## 1RA -> 2DA



## Robos 


## Inventarios 




