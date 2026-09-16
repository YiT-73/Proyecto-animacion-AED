"""Compila la demostración C++ y genera su animación con un solo comando."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


RAIZ = Path(__file__).resolve().parent
CALIDADES = {"baja": ("l", "480p15"), "media": ("m", "720p30"), "alta": ("h", "1080p60")}


def ejecutar(comando, *, raiz=RAIZ, entorno=None):
    """Usa argumentos separados para admitir rutas con espacios en ambos sistemas."""
    comando = [str(parte) for parte in comando]
    print("+ " + subprocess.list2cmdline(comando), flush=True)
    subprocess.run(comando, cwd=raiz, env=entorno, check=True)


def preparar_python(raiz, sin_instalar=False):
    carpeta = raiz / "venv"
    python = carpeta / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        if sin_instalar:
            raise RuntimeError("No existe un entorno utilizable en venv. Ejecuta sin --sin-instalar.")
        if carpeta.exists():
            raise RuntimeError("venv existe pero no contiene un Python válido para este sistema. "
                               "Renombra esa carpeta y vuelve a ejecutar la pipeline.")
        print("Creando el entorno virtual venv...", flush=True)
        venv.EnvBuilder(with_pip=True).create(carpeta)

    # Comprobar las versiones y la importación permite reutilizar el entorno sin red.
    requisitos = [linea.strip() for linea in (raiz / "requirements.txt").read_text(encoding="utf-8").splitlines()
                  if linea.strip() and not linea.lstrip().startswith("#")]
    comprobacion = (
        "import sys; from importlib.metadata import version; "
        "assert sys.version_info >= (3, 11); "
        "assert all(version(r.split('==')[0]) == r.split('==')[1] for r in sys.argv[1:]); "
        "import manim"
    )
    resultado = subprocess.run([str(python), "-c", comprobacion, *requisitos],
                               cwd=raiz, capture_output=True, text=True)
    if resultado.returncode:
        if sin_instalar:
            raise RuntimeError("El entorno no satisface requirements.txt o Manim no puede importarse. "
                               "Ejecuta sin --sin-instalar para instalar las dependencias.\n"
                               + resultado.stderr.strip())
        ejecutar([python, "-m", "pip", "install", "--upgrade", "pip"], raiz=raiz)
        ejecutar([python, "-m", "pip", "install", "-r", raiz / "requirements.txt"], raiz=raiz)
        ejecutar([python, "-c", comprobacion, *requisitos], raiz=raiz)
    return python


def ejecutar_pipeline(opciones, raiz=RAIZ):
    if sys.version_info < (3, 11):
        raise RuntimeError("Se necesita Python 3.11 o posterior. Consulta la instalación en README.md.")
    compilador = shutil.which(opciones.compilador)
    if compilador is None:
        raise RuntimeError(f"No se encontró {opciones.compilador}. Instala g++ y agrégalo al PATH, "
                           "o usa --compilador con la ruta al ejecutable.")
    compilador = str(Path(compilador).absolute())
    ffmpeg = shutil.which("ffmpeg") if opciones.mpeg else None
    if opciones.mpeg and ffmpeg is None:
        raise RuntimeError("La opción --mpeg necesita ffmpeg en el PATH. Consulta README.md.")

    if ffmpeg is not None:
        ffmpeg = str(Path(ffmpeg).absolute())

    python = preparar_python(raiz, opciones.sin_instalar)
    build = raiz / "build"
    build.mkdir(exist_ok=True)
    ejecutable = build / ("tabla_hash.exe" if os.name == "nt" else "tabla_hash")
    entorno = os.environ.copy()
    # MinGW necesita encontrar sus DLL incluso si se pasó una ruta con --compilador.
    entorno["PATH"] = str(Path(compilador).parent) + os.pathsep + entorno.get("PATH", "")
    entorno["PYTHONUTF8"] = "1"
    entorno["PYTHONDONTWRITEBYTECODE"] = "1"

    print("Compilando C++ y regenerando eventos.txt...", flush=True)
    ejecutar([compilador, "-std=c++17", "-O2", raiz / "tabla_hash.cpp", "-o", ejecutable],
             raiz=raiz, entorno=entorno)
    ejecutar([ejecutable], raiz=raiz, entorno=entorno)

    calidad, carpeta = CALIDADES[opciones.calidad]
    media = build / "media"
    video = media / "videos" / "animacion" / carpeta / "HashAnimation.mp4"
    print("Renderizando la animación...", flush=True)
    ejecutar([python, "-m", "manim", "render", "--renderer", "cairo", "--format", "mp4",
              "-q", calidad, "--media_dir", media, "--progress_bar", "none",
              raiz / "animacion.py", "HashAnimation"], raiz=raiz, entorno=entorno)
    if not video.is_file() or video.stat().st_size == 0:
        raise RuntimeError(f"Manim terminó pero no produjo el video esperado: {video}")

    if opciones.mpeg:
        mpeg = build / "HashAnimation.mpeg"
        ejecutar([ffmpeg, "-y", "-i", video, "-an", "-c:v", "mpeg2video", "-q:v", "2",
                  "-pix_fmt", "yuv420p", "-r", "30", "-f", "mpeg", mpeg],
                 raiz=raiz, entorno=entorno)
        print(f"Video MPEG-2: {mpeg}", flush=True)
    print(f"Video MP4: {video}", flush=True)
    return video


def crear_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calidad", choices=CALIDADES, default="alta",
                        help="baja: 480p15; media: 720p30; alta: 1080p60 (predeterminada)")
    parser.add_argument("--compilador", default=os.environ.get("CXX", "g++"),
                        help="nombre o ruta del compilador GCC/Clang (predeterminado: CXX o g++)")
    parser.add_argument("--sin-instalar", action="store_true",
                        help="reutilizar las dependencias instaladas sin descargar paquetes")
    parser.add_argument("--mpeg", action="store_true", help="exportar también MPEG-2 con FFmpeg")
    return parser


def main(argv=None):
    opciones = crear_parser().parse_args(argv)
    try:
        ejecutar_pipeline(opciones)
    except subprocess.CalledProcessError as error:
        print(f"\nPipeline detenida: un comando falló con código {error.returncode}. "
              "Revisa el error mostrado arriba.", file=sys.stderr)
        return 1
    except (OSError, RuntimeError) as error:
        print(f"\nPipeline detenida: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nPipeline interrumpida.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
