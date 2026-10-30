"""
Loader incremental del dominio logistico (pedido/caja/ot/oc/orcom) desde wms hacia
origen/dwh, reemplazando el full-replace de hechos_query_wms_rm.py.

Version 1 -- pensada para correr con un rango de fechas chico (parametros fecha_desde/
fecha_hasta) para dimensionar volumen real antes de definir la ventana incremental
definitiva. hechos_logistica_actividades (picking/packing) queda fuera de este loader
por ahora -- pendiente de diseño.

wms es estrictamente de solo lectura: este script solo hace SELECT contra wms.
"""
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import psycopg2.extras

sys.path.insert(0, r"C:\Users\Usuario\Desktop\Proyectos\Logistica")
import config
from config import conexiones as cx

FLUJO_ID = 34
TZ_WMS = ZoneInfo("America/Santiago")


def _localizar(serie):
    """wms guarda timestamps naive en hora de Chile -- los localiza y pasa a UTC
    antes de insertar en columnas timestamptz, para no depender del timezone de sesion
    de la conexion dwh."""
    return serie.dt.tz_localize(TZ_WMS, ambiguous=True, nonexistent="shift_forward").dt.tz_convert(timezone.utc)


def _resolver_estado(cur, cache, fuente, codigo, transportista="", descripcion_estado=""):
    if codigo is None:
        return None
    transportista = transportista or ""
    descripcion_estado = descripcion_estado or ""
    key = (fuente, codigo, transportista, descripcion_estado)
    if key in cache:
        return cache[key]
    cur.execute(
        """SELECT id FROM dwh.dim_estados_logisticos
           WHERE fuente=%s AND codigo=%s AND transportista=%s AND descripcion_estado=%s""",
        key,
    )
    row = cur.fetchone()
    if row:
        cache[key] = row[0]
        return row[0]
    cur.execute(
        """INSERT INTO dwh.dim_estados_logisticos (fuente, codigo, nombre, origen, transportista, descripcion_estado)
           VALUES (%s, %s, %s, 'wms', %s, %s)
           RETURNING id""",
        (fuente, codigo, codigo, transportista, descripcion_estado),
    )
    new_id = cur.fetchone()[0]
    cache[key] = new_id
    return new_id


def _extraer_pedidos(fecha_desde, fecha_hasta, ids_extra=None):
    """ids_extra: pedido_id referenciados por OC/caja dentro de la ventana pero cuya
    propia pedido.fecha cae fuera de ella (la oleada se creo antes) -- sin esto, el FK
    de dim_ordenes_compra_wms/dim_cajas_wms a dim_pedidos_wms puede fallar."""
    ids_extra = list(ids_extra) if ids_extra else []
    q = """
        SELECT id, nombre, estado, fecha, canal_codigo, origen,
               fechaproceso, fechadespacho, ordentransportepadre,
               CASE WHEN picking = 'HOJA_RUTA_UNICA' THEN 'MULTIPRODUCTO' ELSE 'MONOPRODUCTO' END AS tipo_pedido
        FROM pedido
        WHERE (fecha >= %s AND fecha < %s) OR id = ANY(%s)
    """
    return config.get_consulta("wms", q, params=(fecha_desde, fecha_hasta, ids_extra))


def _extraer_ordenes_compra(fecha_desde, fecha_hasta):
    """region/comuna: via tiendaprioridad.direccion_id -> direccion (solo canales
    propios tienen direccion propia en wms, igual patron que orden_transporte_estado --
    ver V242). retiro_tienda: wms.v_retiro_tienda (vista viva), NO mgt_orcom (tabla
    abandonada desde 2024-08-20) -- v_retiro_tienda solo trae filas para OCs que SI son
    retiro en tienda, de ahi el LEFT JOIN (NULL = no es retiro en tienda). v_retiro_tienda
    trae 1 fila por CAJA, no por OC (validado: ~1.5% de id_sap_doc repetidos en una
    ventana de 90 dias) -- DISTINCT ON id_sap_doc antes de unir, para no multiplicar
    filas de sap_documento."""
    q = """
        SELECT sd.idsapdoc, sd.origen AS empresa_origen, sd.folio AS venta_folio,
               tp.pedido_id, sd.estado, sd.fecha, sd.centrocosto, sd.cantproductos,
               sd.fechaactualizacion,
               d.region, d.comuna,
               vrt.cod_local_retiro AS retiro_tienda_codigo,
               vrt.nombre_local_retiro AS retiro_tienda_nombre
        FROM sap_documento sd
        JOIN tiendaprioridad tp ON tp.idsapdoc = sd.idsapdoc
        LEFT JOIN direccion d ON d.id = tp.direccion_id
        LEFT JOIN (
            SELECT DISTINCT ON (id_sap_doc) id_sap_doc, cod_local_retiro, nombre_local_retiro
            FROM v_retiro_tienda
            ORDER BY id_sap_doc, id_caja
        ) vrt ON vrt.id_sap_doc = sd.idsapdoc
        WHERE sd.tipo = 'FRV' AND sd.fecha >= %s AND sd.fecha < %s
    """
    return config.get_consulta("wms", q, params=(fecha_desde, fecha_hasta))


def _extraer_cajas(fecha_desde, fecha_hasta):
    """cajadespacho.fechaestado no tiene indice -> filtrar directo ahi es un seq scan
    completo de la tabla (medido: ~9s en frio para 2 semanas, vs ~1.5s en caliente).
    En cambio cajadespachohistorico (que de todas formas se consulta aparte) cubre el
    100% de los casos -- se usan sus ids (fetch chico) y se trae cajadespacho por id
    (PK indexada), bastante mas rapido y sin depender del cache."""
    q_ids = "SELECT DISTINCT cajadespacho_id FROM cajadespachohistorico WHERE fecha >= %s AND fecha < %s"
    ids = config.get_consulta("wms", q_ids, params=(fecha_desde, fecha_hasta))["cajadespacho_id"].tolist()
    return _extraer_cajas_por_id(ids)


def _extraer_cajas_por_id(ids):
    """cajadespacho.id referenciados por orden_transporte_estado/cajadespachohistorico
    dentro de la ventana pero cuya propia cajadespacho.fechaestado cae fuera de ella --
    fetch puro por id, sin condicion de fecha (si se le agregara un OR con la ventana
    duplicaria todo el set original al concatenar)."""
    if not ids:
        return pd.DataFrame(columns=["id", "pedido_id", "idsapdoc", "estado", "fechaestado", "ordentransporte", "tienda_codigo"])
    q = """
        SELECT cd.id, cd.pedido_id, tp.idsapdoc, cd.estado, cd.fechaestado,
               cd.ordentransporte, cd.tienda_codigo
        FROM cajadespacho cd
        LEFT JOIN tiendaprioridad tp ON tp.id = cd.tiendaprioridad_id
        WHERE cd.id = ANY(%s)
    """
    return config.get_consulta("wms", q, params=(list(ids),))


def _extraer_ot(fecha_desde, fecha_hasta):
    q = """
        SELECT id_caja, orden_transporte, orden_transporte_padre, transportista,
               servicio, estado, descripcion_estado, fecha_estado
        FROM orden_transporte_estado
        WHERE fecha_actualizacion >= %s AND fecha_actualizacion < %s
        AND orden_transporte IS NOT NULL
    """
    return config.get_consulta("wms", q, params=(fecha_desde, fecha_hasta))


def _extraer_pedidohistorico(fecha_desde, fecha_hasta):
    q = """
        SELECT pedido_id, estado, fecha
        FROM pedidohistorico
        WHERE fecha >= %s AND fecha < %s
    """
    return config.get_consulta("wms", q, params=(fecha_desde, fecha_hasta))


def _extraer_cajadespachohistorico(fecha_desde, fecha_hasta):
    q = """
        SELECT cajadespacho_id, estado, fecha
        FROM cajadespachohistorico
        WHERE fecha >= %s AND fecha < %s
    """
    return config.get_consulta("wms", q, params=(fecha_desde, fecha_hasta))


def _extraer_orcom(fecha_desde, fecha_hasta):
    q = """
        SELECT tp.idsapdoc, sd.origen AS empresa_origen, sd.folio AS venta_folio,
               orcom.estado_orcom, orcom.fecha_observacion
        FROM v_orcom_observacion orcom
        JOIN tiendaprioridad tp ON tp.id = orcom.tiendaprioridad_id
        JOIN sap_documento sd ON sd.idsapdoc = tp.idsapdoc
        WHERE orcom.fecha_observacion >= %s AND orcom.fecha_observacion < %s
    """
    return config.get_consulta("wms", q, params=(fecha_desde, fecha_hasta))


def _upsert_pedidos(cur, df):
    if df.empty:
        return
    df = df.copy()
    df["fecha"] = _localizar(df["fecha"])
    rows = list(df.itertuples(index=False))
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO origen.dim_pedidos_wms
               (id, nombre, estado, fecha, canal_codigo, origen, fechaproceso, fechadespacho, ordentransportepadre, tipo_pedido)
           VALUES %s
           ON CONFLICT (id) DO UPDATE SET
               nombre = EXCLUDED.nombre, estado = EXCLUDED.estado, fecha = EXCLUDED.fecha,
               canal_codigo = EXCLUDED.canal_codigo, origen = EXCLUDED.origen,
               fechaproceso = EXCLUDED.fechaproceso, fechadespacho = EXCLUDED.fechadespacho,
               ordentransportepadre = EXCLUDED.ordentransportepadre,
               tipo_pedido = EXCLUDED.tipo_pedido,
               fecha_actualizacion = CURRENT_TIMESTAMP""",
        rows,
        page_size=2000,
    )
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO dwh.dim_pedidos (id, canal_codigo, fecha) VALUES %s
           ON CONFLICT (id) DO UPDATE SET canal_codigo = EXCLUDED.canal_codigo, fecha = EXCLUDED.fecha""",
        [(r.id, r.canal_codigo, r.fecha) for r in rows],
        page_size=2000,
    )


def _upsert_ordenes_compra(cur, df):
    if df.empty:
        return []
    df = df.copy()
    df["fechaactualizacion"] = _localizar(df["fechaactualizacion"])

    idsapdocs = list(df["idsapdoc"].unique())
    cur.execute("SELECT idsapdoc, estado FROM origen.dim_ordenes_compra_wms WHERE idsapdoc = ANY(%s)", (idsapdocs,))
    estados_previos = dict(cur.fetchall())

    rows = list(df.itertuples(index=False))
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO origen.dim_ordenes_compra_wms
               (idsapdoc, empresa_origen, venta_folio, pedido_id, estado, fecha, centrocosto, cantproductos,
                region, comuna, retiro_tienda_codigo, retiro_tienda_nombre)
           VALUES %s
           ON CONFLICT (idsapdoc) DO UPDATE SET
               venta_folio = EXCLUDED.venta_folio, pedido_id = EXCLUDED.pedido_id,
               estado = EXCLUDED.estado, centrocosto = EXCLUDED.centrocosto,
               cantproductos = EXCLUDED.cantproductos,
               region = EXCLUDED.region, comuna = EXCLUDED.comuna,
               retiro_tienda_codigo = EXCLUDED.retiro_tienda_codigo,
               retiro_tienda_nombre = EXCLUDED.retiro_tienda_nombre,
               fecha_actualizacion = CURRENT_TIMESTAMP""",
        [
            (
                r.idsapdoc, r.empresa_origen, r.venta_folio, r.pedido_id, r.estado, r.fecha, r.centrocosto, r.cantproductos,
                r.region, r.comuna, r.retiro_tienda_codigo, r.retiro_tienda_nombre,
            )
            for r in rows
        ],
        page_size=2000,
    )

    eventos = []
    for r in rows:
        estado_previo = estados_previos.get(r.idsapdoc)
        if estado_previo != r.estado and pd.notna(r.fechaactualizacion):
            eventos.append((r.empresa_origen, r.venta_folio, r.estado, r.fechaactualizacion))
    return eventos


def _upsert_cajas(cur, df):
    if df.empty:
        return
    df = df.copy()
    df["fechaestado"] = _localizar(df["fechaestado"])

    idsapdocs = list(df["idsapdoc"].dropna().unique())
    mapa_oc = {}
    if idsapdocs:
        cur.execute("SELECT idsapdoc, id FROM origen.dim_ordenes_compra_wms WHERE idsapdoc = ANY(%s)", (idsapdocs,))
        mapa_oc = dict(cur.fetchall())

    rows = []
    for r in df.itertuples(index=False):
        orden_compra_id = mapa_oc.get(r.idsapdoc) if r.idsapdoc else None
        pedido_id = int(r.pedido_id) if pd.notna(r.pedido_id) else None
        rows.append((r.id, pedido_id, orden_compra_id, r.estado, r.fechaestado, r.ordentransporte, r.tienda_codigo))
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO origen.dim_cajas_wms
               (id, pedido_id, orden_compra_id, estado, fechaestado, ordentransporte, tienda_codigo)
           VALUES %s
           ON CONFLICT (id) DO UPDATE SET
               pedido_id = EXCLUDED.pedido_id, orden_compra_id = EXCLUDED.orden_compra_id,
               estado = EXCLUDED.estado, fechaestado = EXCLUDED.fechaestado,
               ordentransporte = EXCLUDED.ordentransporte, tienda_codigo = EXCLUDED.tienda_codigo,
               fecha_actualizacion = CURRENT_TIMESTAMP""",
        rows,
        page_size=2000,
    )
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO dwh.dim_cajas (id, pedido_id) VALUES %s
           ON CONFLICT (id) DO UPDATE SET pedido_id = EXCLUDED.pedido_id""",
        [(r[0], r[1]) for r in rows],
        page_size=2000,
    )


def _upsert_ordenes_transporte(cur, df):
    if df.empty:
        return
    df = df.copy()
    df["fecha_estado"] = _localizar(df["fecha_estado"])

    codigos = set(df["orden_transporte"].astype(str)) | set(df["orden_transporte_padre"].dropna().astype(int).astype(str))
    psycopg2.extras.execute_values(
        cur,
        "INSERT INTO origen.dim_ordenes_transporte (codigo) VALUES %s ON CONFLICT (codigo) DO NOTHING",
        [(c,) for c in codigos],
        page_size=2000,
    )

    # una caja puede haber tenido una OT distinta antes (reasignacion de guia) -- se
    # libera esa asignacion vieja en bloque para no chocar con el UNIQUE(caja_id) al
    # reasignarla mas abajo
    caja_ids_batch = [int(x) for x in df["id_caja"].dropna().unique()]
    if caja_ids_batch:
        cur.execute(
            "UPDATE origen.dim_ordenes_transporte SET caja_id=NULL WHERE caja_id = ANY(%s)",
            (caja_ids_batch,),
        )

    # si dos codigos distintos de OT aparecen en la misma ventana apuntando a la misma
    # caja (reasignacion de guia ocurrida dentro de la ventana), un UPDATE masivo
    # intentaria pisar esa caja_id dos veces en el mismo statement -- se resuelve
    # quedandose solo con el mas reciente (por fecha_estado) por codigo, y despues
    # por caja_id (al resto se le pone caja_id=NULL, igual que se hizo con los
    # registros viejos de otras corridas mas arriba)
    df_latest = df.sort_values("fecha_estado").drop_duplicates(subset="orden_transporte", keep="last").copy()
    df_latest["id_caja_resuelto"] = df_latest["id_caja"].apply(lambda x: int(x) if pd.notna(x) else None)
    vistos_caja = set()
    for idx in df_latest.sort_values("fecha_estado", ascending=False).index:
        cid = df_latest.at[idx, "id_caja_resuelto"]
        if cid is None:
            continue
        if cid in vistos_caja:
            df_latest.at[idx, "id_caja_resuelto"] = None
        else:
            vistos_caja.add(cid)

    filas_update = [
        (str(r.orden_transporte), r.transportista, r.servicio,
         int(r.id_caja_resuelto) if pd.notna(r.id_caja_resuelto) else None)
        for r in df_latest.itertuples(index=False)
    ]
    psycopg2.extras.execute_values(
        cur,
        """UPDATE origen.dim_ordenes_transporte AS t
           SET transportista = v.transportista, servicio = v.servicio, caja_id = v.caja_id,
               fecha_actualizacion = CURRENT_TIMESTAMP
           FROM (VALUES %s) AS v(codigo, transportista, servicio, caja_id)
           WHERE t.codigo = v.codigo""",
        filas_update,
        page_size=2000,
    )

    # padre_id: mapeo codigo->id en un solo SELECT, luego UPDATE en bloque
    cur.execute("SELECT codigo, id FROM origen.dim_ordenes_transporte WHERE codigo = ANY(%s)", (list(codigos),))
    mapa_id = dict(cur.fetchall())

    filas_padre = []
    vistos = set()
    for r in df.itertuples(index=False):
        codigo = str(r.orden_transporte)
        if codigo in vistos or pd.isna(r.orden_transporte_padre):
            continue
        vistos.add(codigo)
        padre_id = mapa_id.get(str(int(r.orden_transporte_padre)))
        if padre_id is not None:
            filas_padre.append((codigo, padre_id))
    if filas_padre:
        psycopg2.extras.execute_values(
            cur,
            """UPDATE origen.dim_ordenes_transporte AS t
               SET padre_id = v.padre_id
               FROM (VALUES %s) AS v(codigo, padre_id)
               WHERE t.codigo = v.codigo""",
            filas_padre,
            page_size=2000,
        )

    # mismo caso que en origen: la caja_id puede haber quedado asignada a otra OT en
    # dwh desde una corrida anterior -- se libera antes de upsertear, si no choca con
    # el UNIQUE(caja_id) de dwh.dim_ordenes_transporte (V221)
    if caja_ids_batch:
        cur.execute(
            "UPDATE dwh.dim_ordenes_transporte SET caja_id=NULL WHERE caja_id = ANY(%s)",
            (caja_ids_batch,),
        )

    cur.execute(
        """INSERT INTO dwh.dim_ordenes_transporte (id, padre_id, caja_id, transportista)
           SELECT id, padre_id, caja_id, transportista FROM origen.dim_ordenes_transporte
           WHERE codigo = ANY(%s)
           ON CONFLICT (id) DO UPDATE SET
               padre_id = EXCLUDED.padre_id, caja_id = EXCLUDED.caja_id, transportista = EXCLUDED.transportista""",
        (list(codigos),),
    )


def _insertar_eventos(cur, eventos):
    """eventos: lista de dicts con fuente, pedido_id, caja_id, orden_transporte_id,
    venta_nro_oc, venta_empresa_origen, estado_id, fecha_estado"""
    if not eventos:
        return 0
    rows = [
        (
            e["fuente"], e.get("pedido_id"), e.get("caja_id"), e.get("orden_transporte_id"),
            e.get("venta_nro_oc"), e.get("venta_empresa_origen"), e["estado_id"], e["fecha_estado"],
        )
        for e in eventos
    ]
    psycopg2.extras.execute_values(
        cur,
        """INSERT INTO dwh.hechos_logistica_estados
               (fuente, pedido_id, caja_id, orden_transporte_id, venta_nro_oc, venta_empresa_origen, estado_id, fecha_estado)
           VALUES %s
           ON CONFLICT DO NOTHING""",
        rows,
        page_size=2000,
    )
    return len(rows)


def cargar(fecha_desde, fecha_hasta, modo="manual"):
    inicio = datetime.now(timezone.utc)
    conexion = cx.get_conexion("dwh")
    cur = conexion.cursor()
    resumen = {}

    # precarga el catalogo completo de estados en memoria -- evita un SELECT por cada
    # combinacion (fuente,codigo,transportista,descripcion) nueva que aparezca
    cur.execute("SELECT fuente, codigo, transportista, descripcion_estado, id FROM dwh.dim_estados_logisticos")
    cache_estados = {(f, c, t, d): i for f, c, t, d, i in cur.fetchall()}

    try:
        df_oc = _extraer_ordenes_compra(fecha_desde, fecha_hasta)
        df_cajas = _extraer_cajas(fecha_desde, fecha_hasta)
        df_ot = _extraer_ot(fecha_desde, fecha_hasta)
        df_ped_hist = _extraer_pedidohistorico(fecha_desde, fecha_hasta)
        df_caja_hist = _extraer_cajadespachohistorico(fecha_desde, fecha_hasta)

        # cajas referenciadas por OT/cajadespachohistorico cuya propia fechaestado cae
        # fuera de la ventana (el evento de historial puede ser reciente aunque la caja
        # en si se haya creado hace rato)
        ids_caja_extra = set()
        if not df_ot.empty:
            ids_caja_extra |= set(df_ot["id_caja"].dropna().astype(int))
        if not df_caja_hist.empty:
            ids_caja_extra |= set(df_caja_hist["cajadespacho_id"].dropna().astype(int))
        if not df_cajas.empty:
            ids_caja_extra -= set(df_cajas["id"].astype(int))
        if ids_caja_extra:
            df_cajas = pd.concat([df_cajas, _extraer_cajas_por_id(ids_caja_extra)], ignore_index=True)

        # pedidos referenciados por OC/caja/pedidohistorico cuya propia fecha cae fuera
        # de la ventana
        ids_pedido_extra = set()
        if not df_oc.empty:
            ids_pedido_extra |= set(df_oc["pedido_id"].dropna().astype(int))
        if not df_cajas.empty:
            ids_pedido_extra |= set(df_cajas["pedido_id"].dropna().astype(int))
        if not df_ped_hist.empty:
            ids_pedido_extra |= set(df_ped_hist["pedido_id"].dropna().astype(int))

        df_pedidos = _extraer_pedidos(fecha_desde, fecha_hasta, ids_pedido_extra)
        _upsert_pedidos(cur, df_pedidos)
        resumen["pedidos"] = len(df_pedidos)

        eventos_oc = _upsert_ordenes_compra(cur, df_oc)
        resumen["ordenes_compra"] = len(df_oc)

        _upsert_cajas(cur, df_cajas)
        resumen["cajas"] = len(df_cajas)

        _upsert_ordenes_transporte(cur, df_ot)
        resumen["ordenes_transporte"] = len(df_ot)

        eventos = []

        if not df_ped_hist.empty:
            df_ped_hist["fecha"] = _localizar(df_ped_hist["fecha"])
            for r in df_ped_hist.itertuples(index=False):
                if pd.isna(r.fecha):
                    continue
                estado_id = _resolver_estado(cur, cache_estados, "pedido", r.estado)
                eventos.append({"fuente": "pedido", "pedido_id": r.pedido_id, "estado_id": estado_id, "fecha_estado": r.fecha})

        if not df_caja_hist.empty:
            df_caja_hist["fecha"] = _localizar(df_caja_hist["fecha"])
            for r in df_caja_hist.itertuples(index=False):
                if pd.isna(r.fecha):
                    continue
                estado_id = _resolver_estado(cur, cache_estados, "caja", r.estado)
                eventos.append({"fuente": "caja", "caja_id": r.cajadespacho_id, "estado_id": estado_id, "fecha_estado": r.fecha})

        df_ot_eventos = df_ot.copy()
        mapa_ot_ids = {}
        if not df_ot_eventos.empty:
            df_ot_eventos["fecha_estado"] = _localizar(df_ot_eventos["fecha_estado"])
            codigos_ot = list(df_ot_eventos["orden_transporte"].astype(str).unique())
            cur.execute("SELECT codigo, id FROM origen.dim_ordenes_transporte WHERE codigo = ANY(%s)", (codigos_ot,))
            mapa_ot_ids = dict(cur.fetchall())
        for r in df_ot_eventos.itertuples(index=False):
            if r.estado is None or pd.isna(r.fecha_estado):
                continue
            estado_id = _resolver_estado(cur, cache_estados, "ot", r.estado, r.transportista or "", r.descripcion_estado or "")
            ot_id = mapa_ot_ids.get(str(r.orden_transporte))
            eventos.append({"fuente": "ot", "orden_transporte_id": ot_id, "estado_id": estado_id, "fecha_estado": r.fecha_estado})

        for empresa_origen, venta_folio, estado, fecha in eventos_oc:
            estado_id = _resolver_estado(cur, cache_estados, "oc", estado)
            eventos.append({"fuente": "oc", "venta_nro_oc": venta_folio, "venta_empresa_origen": empresa_origen, "estado_id": estado_id, "fecha_estado": fecha})

        df_orcom = _extraer_orcom(fecha_desde, fecha_hasta)
        if not df_orcom.empty:
            df_orcom["fecha_observacion"] = _localizar(df_orcom["fecha_observacion"])
            for r in df_orcom.itertuples(index=False):
                estado_id = _resolver_estado(cur, cache_estados, "orcom", r.estado_orcom)
                eventos.append({"fuente": "orcom", "venta_nro_oc": r.venta_folio, "venta_empresa_origen": r.empresa_origen, "estado_id": estado_id, "fecha_estado": r.fecha_observacion})

        resumen["eventos_insertados"] = _insertar_eventos(cur, eventos)

        conexion.commit()
        fin = datetime.now(timezone.utc)
        cx.cargar_log(FLUJO_ID, inicio, fin, filas_procesadas=sum(resumen.values()), estado="OK",
                      mensaje=str(resumen), exit=False)
    except Exception as e:
        conexion.rollback()
        fin = datetime.now(timezone.utc)
        cx.cargar_log(FLUJO_ID, inicio, fin, estado="FAIL", mensaje=str(e), exit=False)
        raise
    finally:
        cur.close()
        conexion.close()

    return resumen


if __name__ == "__main__":
    # rango chico a proposito, para dimensionar volumen real antes de definir la ventana incremental
    fecha_desde = "2026-10-01"
    fecha_hasta = "2026-10-08"
    resumen = cargar(fecha_desde, fecha_hasta)
    print(f"\nResumen de carga {fecha_desde} -> {fecha_hasta}:")
    for k, v in resumen.items():
        print(f"  {k}: {v}")
