"""Actualiza el repo (git pull) en el servidor y reinstala dependencias solo si requirements.txt cambió.

Pensado para llamarse al inicio de main.py, que es lo que ejecuta el programador
de tareas de Windows.
"""
import subprocess
import sys
from datetime import datetime, timezone

from config.config import raiz as RUTA_REPO
from config.conexiones import cargar_log

FLUJO_ID_ACTUALIZAR_REPO = 97

NOMBRE_REQUIREMENTS = "requirements.txt"
RUTA_LOG = RUTA_REPO / "actualizar_repo.log"


def _log(mensaje):
    linea = f"{datetime.now()} - {mensaje}"
    print(linea)
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def _git(*args):
    resultado = subprocess.run(["git", *args], cwd=RUTA_REPO, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falló: {resultado.stderr.strip()}")
    return resultado.stdout.strip()


def actualizar_repo():
    inicio_log = datetime.now(timezone.utc)
    filas = None
    estado, mensaje = "OK", None

    try:
        commit_antes = _git("rev-parse", "HEAD")
        _log(f"Actualizando repo (commit actual: {commit_antes[:8]})...")

        salida_pull = _git("pull", "--ff-only")
        _log(salida_pull)

        commit_despues = _git("rev-parse", "HEAD")
        if commit_despues == commit_antes:
            mensaje = "Sin cambios nuevos."
            _log(mensaje)
        else:
            archivos_cambiados = _git("diff", "--name-only", commit_antes, commit_despues).splitlines()
            filas = len(archivos_cambiados)
            _log(f"Repo actualizado a {commit_despues[:8]} ({filas} archivo(s) cambiado(s)).")

            if NOMBRE_REQUIREMENTS in archivos_cambiados:
                _log(f"{NOMBRE_REQUIREMENTS} cambió, instalando dependencias...")
                resultado = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(RUTA_REPO / NOMBRE_REQUIREMENTS)],
                    cwd=RUTA_REPO, capture_output=True, text=True,
                )
                if resultado.stdout:
                    _log(resultado.stdout.strip())
                if resultado.returncode != 0:
                    raise RuntimeError(f"pip install -r requirements.txt falló: {resultado.stderr.strip()}")
                _log("Dependencias instaladas.")
                mensaje = f"Actualizado a {commit_despues[:8]} ({filas} archivo(s) cambiado(s)), dependencias reinstaladas."
            else:
                _log(f"{NOMBRE_REQUIREMENTS} sin cambios, no se reinstalan dependencias.")
                mensaje = f"Actualizado a {commit_despues[:8]} ({filas} archivo(s) cambiado(s))."

    except Exception as e:
        estado, mensaje = "FAIL", str(e)
        _log(f"ERROR: {e}")
    finally:
        cargar_log(
            FLUJO_ID_ACTUALIZAR_REPO, inicio_log, datetime.now(timezone.utc),
            filas_procesadas=filas, estado=estado, mensaje=mensaje, exit=False,
        )

    if estado == "FAIL":
        raise RuntimeError(mensaje)


if __name__ == "__main__":
    actualizar_repo()
