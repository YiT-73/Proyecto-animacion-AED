# Tabla hash con encadenamiento: animación con Manim

Proyecto 1 de **CS2023 — Algoritmos y Estructuras de Datos**. El programa implementa
una tabla hash en C++ y utiliza Manim Community para mostrar sus operaciones paso
a paso: inserciones, colisiones, rehash, búsqueda y eliminación.

**Integrantes:** 
- Yitzhak Abraham Namihas Millan
- Carla Viviana Molina Álvarez

Repositorio: [Proyecto-animacion-AED](https://github.com/YiT-73/Proyecto-animacion-AED).

## Antes de la primera ejecución

Si acaba de descargar el proyecto, sigue este orden:

1. Instala **Python 3.11 o posterior** y un **compilador C++17** siguiendo la guía
   de [Linux](#instalación-en-linux) o [Windows](#instalación-en-windows).
2. Descarga el repositorio y entra a la carpeta que contiene `pipeline.py`.
3. Comprueba que Python y el compilador respondan a los comandos `--version`
   indicados en la guía de tu sistema.
4. Ejecuta la [pipeline](#inicio-rápido-toda-la-pipeline-con-un-comando).

La instalación del sistema se realiza una sola vez. **La pipeline prepara el
entorno de Python e instala Manim, pero no instala Python ni el compilador C++.**
En Windows puedes elegir WinLibs o MSYS2; basta con una de esas alternativas.
FFmpeg solo es necesario si vas a utilizar la opción `--mpeg`.

## Estructura de datos y demostración

La tabla es un arreglo de buckets. Cada bucket apunta a una lista simplemente
enlazada que almacena las claves que colisionan. Los nodos nuevos se insertan al
inicio de su cadena; si una clave ya existe, se actualiza su valor. La búsqueda
recorre la cadena correspondiente y la eliminación actualiza sus enlaces.

Antes de insertar una clave nueva se calcula el factor proyectado:

```text
factor = (cantidad_de_elementos + 1) / (capacidad * k)
```

Si supera `maxFillFactor`, se duplica la capacidad y se reubican todos los nodos.
En la demostración se usan capacidad inicial `5`, `k = 3` y límite `0.5`.
`k` normaliza este factor; no impone un límite estricto al largo de las cadenas.
Con una distribución adecuada, búsqueda, inserción y eliminación tienen costo
esperado O(1), e inserción O(1) amortizado al incluir los rehash. Una cadena con
todas las claves puede llevar esas operaciones a O(n). El rehash recorre los
buckets y los elementos; el almacenamiento ocupa O(capacidad + n).

El código contiene tres políticas: división, multiplicación y hashing universal.
El `main()` actual demuestra **división**, usando `std::hash(clave) % capacidad`.
Inserta `2, 3, 6, 8, 10, 11, 15, 19, 20, 22, 25, 30`, busca `19` y lo elimina.
La tabla final tiene 10 buckets y 11 elementos.

Antes de la demo, la animación explica la función hash y las colisiones con
encadenamiento. Incluye una gráfica ilustrativa de O(1) esperado frente a O(n)
en el peor caso, la expresión O(1 + α) con α = n / m y el costo del rehash.
La escena completa dura al menos 60 segundos, incluso con un registro más corto.

La demostración coloca los buckets en vertical y las cadenas hacia la derecha,
muestra la redistribución del rehash, resalta el recorrido de las búsquedas
exitosas y retira los nodos eliminados. Es un video; no incluye una interfaz
interactiva para introducir operaciones durante la reproducción.

## Software requerido

| Herramienta | Requisito y función |
| --- | --- |
| Python | 3.11 o posterior, con `venv` y `pip` |
| Manim Community | `0.21.0`, fijado en `requirements.txt` |
| Compilador C++ | GCC (`g++`) o Clang (`clang++`) con soporte C++17; en Windows se utiliza MinGW-w64 |
| Cairo, Pango y pkg-config | Dependencias de compilación de los paquetes gráficos en Linux |
| Git | Para clonar el repositorio; también puedes descargarlo como ZIP |
| FFmpeg | Opcional, requerido por `--mpeg` para crear un archivo MPEG-2 |

`requirements.txt` contiene las dependencias directas de Python; `pip` resuelve
las transitivas. No es un archivo de bloqueo de todas sus versiones y no instala
el compilador ni las bibliotecas del sistema. La primera instalación necesita
acceso a Internet. La escena actual usa `Text` y figuras, por lo que no requiere
LaTeX. Véanse las [instrucciones de Manim](https://docs.manim.community/en/stable/installation/uv.html).

## Instalación en Linux

Instala una vez los paquetes correspondientes a tu distribución. Los comandos
`sudo` siguientes instalan herramientas del sistema; la pipeline se ejecuta como
usuario normal. Las dependencias de Cairo se basan en la
[guía de Pycairo](https://pycairo.readthedocs.io/en/latest/getting_started.html).

### Ubuntu, Debian y Linux Mint

Para Ubuntu 24.04 o posterior, Debian 12 o posterior y Linux Mint 22 o posterior:

```bash
sudo apt update
sudo apt install -y build-essential python3 python3-dev python3-venv python3-pip pkg-config libcairo2-dev libpango1.0-dev git
```

En otras versiones o derivadas, comprueba que `python3 --version` sea al menos
3.11. Las versiones que traen Python 3.10 no sirven para el Manim fijado aquí.

### Fedora

```bash
sudo dnf install gcc-c++ python3 python3-devel python3-pip pkgconf-pkg-config cairo-devel pango-devel git
```

### Arch Linux, EndeavourOS y Manjaro

```bash
sudo pacman -Syu --needed base-devel python python-pip pkgconf cairo pango git
```

Este comando también actualiza el sistema conforme al modelo de actualización
de estas distribuciones. Usa el entorno virtual del proyecto para los paquetes
Python; véase la [documentación de Python en Arch](https://wiki.archlinux.org/title/Python).

### openSUSE Tumbleweed y Leap 16

Se selecciona Python 3.13 explícitamente para mantener alineado el intérprete con
sus cabeceras y `pip`:

```bash
sudo zypper install gcc-c++ python313 python313-devel python313-pip pkg-config cairo-devel pango-devel git
python3.13 --version
```

En los comandos siguientes usa `python3.13` en lugar de `python3`. Si tu edición
no ofrece esos paquetes, consulta sus repositorios para una versión de Python
3.11 o posterior junto con los paquetes `-devel` y `-pip` correspondientes.

### Descargar y comprobar las herramientas

Si ya tienes el repositorio, entra a su carpeta y omite la clonación.

```bash
git clone https://github.com/YiT-73/Proyecto-animacion-AED.git
cd Proyecto-animacion-AED
python3 --version
g++ --version
```

Si ambos comandos muestran una versión y Python es 3.11 o posterior, continúa
con la [ejecución de la pipeline](#inicio-rápido-toda-la-pipeline-con-un-comando).

## Instalación en Windows

Guía para **Windows 10/11 de 64 bits (x86_64)**, usando PowerShell y Python nativo
de Windows. Instala Python y elige **una** de las dos formas de obtener `g++`.

### 1. Instalar Python

Descarga Python de 64 bits, versión 3.11 o posterior, desde
[Python para Windows](https://www.python.org/downloads/windows/), con `pip` y el
lanzador `py`. Abre una terminal de PowerShell nueva y comprueba:

```powershell
py -3 --version
```

Debe mostrar Python 3.11 o posterior.

### 2A. Obtener el compilador con WinLibs (sin MSYS2)

[WinLibs](https://winlibs.com/) distribuye GCC y MinGW-w64 en un archivo comprimido.
Esta alternativa permite ejecutar la pipeline sin configurar el `PATH`.

1. En la sección de descargas de WinLibs, elige una versión estable **Win64
   (x86_64), UCRT, ZIP** de GCC con MinGW-w64.
2. Descomprime **todo el archivo** en una carpeta, por ejemplo `C:\winlibs`.
   Conserva sus subcarpetas y bibliotecas, no copies solamente `g++.exe`.
3. Localiza `g++.exe` dentro de `mingw64\bin`. Si la ruta resultante es
   `C:\winlibs\mingw64\bin\g++.exe`, comprueba desde PowerShell:

   ```powershell
   & "C:\winlibs\mingw64\bin\g++.exe" --version
   ```

   El símbolo `&` permite ejecutar una ruta entre comillas en PowerShell.
   Si descomprimiste el archivo en otra ubicación, ajusta la ruta.

Al ejecutar la pipeline usarás `--compilador` con esa misma ruta. Si elegiste
WinLibs, pasa al paso 3; no necesitas instalar MSYS2.

### 2B. Obtener el compilador con MSYS2 (alternativa)

Instala [MSYS2](https://www.msys2.org/). Abre **MSYS2 UCRT64** desde el menú Inicio
y ejecuta:

```bash
pacman -Syu
```

Si solicita cerrar la terminal, ciérrala, abre de nuevo **MSYS2 UCRT64** y repite
la actualización. Después instala el compilador:

```bash
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

Esta es la instalación de GCC descrita por
[MinGW-w64](https://www.mingw-w64.org/getting-started/msys2/).

Abre **PowerShell**. Para una instalación estándar de MSYS2, agrega el compilador
al `PATH` de esta sesión y comprueba que funcione:

```powershell
$env:Path = "C:\msys64\ucrt64\bin;" + $env:Path
g++ --version
```

Si instalaste MSYS2 en otra ubicación, ajusta esa ruta. Para conservarla entre
terminales, busca **Editar las variables de entorno de esta cuenta** en Inicio,
edita `Path` y añade `C:\msys64\ucrt64\bin`. Después abre una terminal nueva;
si usas la terminal integrada de VS Code, reinicia VS Code.

También puedes pasar la ruta de MSYS2 con `--compilador`, igual que con WinLibs.

### 3. Descargar el proyecto

Si ya tienes el repositorio, entra a su carpeta y omite la descarga.
Puedes usar **Code → Download ZIP** en
[GitHub](https://github.com/YiT-73/Proyecto-animacion-AED) y descomprimirlo, o instalar
[Git para Windows](https://git-scm.com/downloads/win) y clonar desde PowerShell:

```powershell
git clone https://github.com/YiT-73/Proyecto-animacion-AED.git
cd Proyecto-animacion-AED
```

Si descargaste un ZIP, abre PowerShell en la carpeta descomprimida que contiene
`pipeline.py`. Ya puedes seguir con la ejecución indicada abajo.

Manim se instala dentro de `venv` mediante el Python de Windows. No hay que
activar `Activate.ps1` ni cambiar la política de ejecución de PowerShell. No
reutilices una carpeta `venv` creada en Linux: renómbrala y deja que la pipeline
cree un entorno para Windows.

## Inicio rápido: toda la pipeline con un comando

Después de completar la instalación y comprobar las versiones, ejecuta desde
la carpeta que contiene `pipeline.py`:

**Linux:**

```bash
python3 pipeline.py
```

**Windows con WinLibs, PowerShell** (ajusta la ruta a tu instalación):

```powershell
py -3 pipeline.py --compilador "C:\winlibs\mingw64\bin\g++.exe"
```

**Windows con `g++` en el `PATH`, PowerShell:**

```powershell
py -3 pipeline.py
```

El comando crea `venv` si hace falta, instala `requirements.txt` cuando las
dependencias no están disponibles, compila `tabla_hash.cpp`, ejecuta la
demostración para regenerar `eventos.txt` y renderiza el video en **1080p a 60 FPS**.
No es necesario activar el entorno virtual. Las siguientes ejecuciones reutilizan
las dependencias instaladas y la caché de renderización.

El resultado queda en:

```text
build/media/videos/animacion/1080p60/HashAnimation.mp4
```

La pipeline se detiene si falla alguna etapa. Cada ejecución reemplaza el registro
de eventos y la salida de video correspondiente. También puede invocarse desde
otro directorio indicando la ruta completa a `pipeline.py`: trabaja siempre en
la carpeta del proyecto.

## Opciones de la pipeline

Los ejemplos usan Linux; en Windows sustituye `python3` por `py -3`. Si utilizas
WinLibs u otro compilador fuera del `PATH`, añade también `--compilador` con su
ruta, como en el ejemplo anterior.

```bash
# Vista previa rápida: 480p y 15 FPS.
python3 pipeline.py --calidad baja

# Calidad intermedia: 720p y 30 FPS.
python3 pipeline.py --calidad media

# Ejecutar sin instalaciones ni descargas, con venv ya preparado.
python3 pipeline.py --sin-instalar

# Utilizar otro compilador compatible con las opciones de GCC.
python3 pipeline.py --compilador clang++

# Consultar todas las opciones.
python3 pipeline.py --help
```

Ejemplo de Windows sin modificar el `PATH`:

```powershell
py -3 pipeline.py --compilador "C:\msys64\ucrt64\bin\g++.exe"
```

También se acepta la variable `CXX` como nombre o ruta de compilador, sin flags.
Las opciones se pueden combinar.

### Exportar un archivo `.mpeg`

La salida habitual es MP4. Para disponer también de un archivo con extensión
`.mpeg` y códec MPEG-2, instala FFmpeg y comprueba `ffmpeg -version`.

| Sistema | Instalación de FFmpeg |
| --- | --- |
| Ubuntu / Debian / Mint | `sudo apt install ffmpeg` |
| Fedora | `sudo dnf install ffmpeg-free` |
| Arch y derivadas | `sudo pacman -S --needed ffmpeg` |
| Windows, PowerShell | `winget install --id Gyan.FFmpeg -e` y abrir otra terminal |

Para otras distribuciones, utiliza su paquete de FFmpeg. También puedes consultar
las [descargas de FFmpeg](https://ffmpeg.org/download.html); el identificador de
Windows figura en el [catálogo de WinGet](https://github.com/microsoft/winget-pkgs/tree/master/manifests/g/Gyan/FFmpeg).

```bash
python3 pipeline.py --mpeg
```

Se generan el MP4 habitual y `build/HashAnimation.mpeg`. El MPEG-2 conserva la
resolución seleccionada y se exporta a 30 FPS; el MP4 conserva los FPS de la calidad
elegida. La opción no cambia la duración ni añade créditos.

## Ejecución manual por etapas

Estos comandos son una alternativa a la pipeline y se ejecutan desde la raíz del
repositorio.

**Linux:**

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
g++ -std=c++17 tabla_hash.cpp -o hash
./hash
venv/bin/python -m manim -qh animacion.py HashAnimation
```

**Windows, PowerShell**, con `g++` en el `PATH`:

```powershell
py -3 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
g++ -std=c++17 tabla_hash.cpp -o hash.exe
.\hash.exe
.\venv\Scripts\python.exe -m manim -qh animacion.py HashAnimation
```

La ejecución manual de Manim guarda el video en
`media/videos/animacion/1080p60/HashAnimation.mp4`, mientras que la pipeline guarda
sus resultados dentro de `build/`. En ambos casos `-ql`, `-qm` y `-qh` seleccionan
480p, 720p y 1080p, respectivamente.

Para renderizar solo los eventos actuales desde el IDE también puedes ejecutar
`animacion.py` con el intérprete de `venv`; ese modo usa calidad 720p y **no**
recompila C++ ni regenera los eventos.

## Archivos y personalización

| Archivo | Función |
| --- | --- |
| `tabla_hash.cpp` | Tabla hash, políticas hash y demostración en `main()` |
| `eventos.txt` | Registro generado por la demostración de C++ |
| `animacion.py` | Lectura, validación y animación del registro |
| `pipeline.py` | Preparación del entorno, compilación y renderización |
| `requirements.txt` | Dependencias directas de Python |
| `build/` | Ejecutable, videos y cachés generados por la pipeline |

El registro utiliza `INIT capacidad` para iniciar cada tabla; `INSERT`, `SEARCH`
y `REMOVE` incluyen clave e índice, o `NOT FOUND` en operaciones fallidas.
`REHASH antigua nueva` va seguido de un `MOVE clave índice` por nodo y de
`REHASH_END`. Los destinos se calculan en C++, por lo que también pueden describir
las políticas de multiplicación y hashing universal. La animación actual espera
claves enteras y tablas demostradas de forma secuencial.

## Solución de problemas

| Problema | Solución |
| --- | --- |
| No se encuentra `g++` | Instala el compilador o usa `--compilador`; en Windows revisa la ruta UCRT64 |
| Falta `venv` / `ensurepip` en Debian o Ubuntu | Instala `python3-venv` para la versión de Python utilizada |
| Falla la instalación de Cairo o ManimPango | Instala las cabeceras de Cairo, Pango y Python, además de pkg-config, según la guía de tu distribución |
| `No module named manim` | Ejecuta la pipeline sin `--sin-instalar` o utiliza el Python de `venv` |
| `venv` pertenece a otro sistema o a un Python eliminado | Renombra la carpeta y vuelve a ejecutar la pipeline para crearla de nuevo |
| Registro antiguo, mezclado o rehash incompleto | Regenera los eventos con la pipeline; el ejecutable anterior puede producir un formato antiguo |
| No se encuentra `ffmpeg` al usar `--mpeg` | Instala FFmpeg, comprueba el `PATH` y abre otra terminal si acabas de instalarlo |

La pipeline se verifica localmente en Linux. La guía de Windows sigue las
instalaciones oficiales indicadas, pero no se ha ejecutado en un equipo Windows
durante esta preparación.
