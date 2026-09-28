import os
import sys
import glob
import json
import time
import re
import asyncio
import tempfile
import msvcrt
import edge_tts
import pygame

# ==========================================
# CONFIGURACIÓN DE VOZ (TIPO JARVIS)
# ==========================================
VOICE = "es-MX-JorgeNeural"
POLL_INTERVAL = 0.8  # Frecuencia de escaneo en segundos

# Rutas de música para trabajar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "jarvis_music")

TRACKS = {
    "synthwave": os.path.join(MUSIC_DIR, "synthwave_lab.mp3"),
    "lofi": os.path.join(MUSIC_DIR, "lofi_rhodes.wav"),
    "cyber": os.path.join(MUSIC_DIR, "cyber_focus.wav"),
    "ambient": os.path.join(BASE_DIR, "jarvis_ambient.wav")
}

def clean_text_for_speech(text: str) -> str:
    """Limpia markdown, código, URLs y caracteres especiales para que suene fluido y natural en español."""
    if not text:
        return ""
    # Omitir bloques de código grandes
    text = re.sub(r'```[\s\S]*?```', ' [Código omitido] ', text)
    # Reemplazar URLs completas por mención amigable
    text = re.sub(r'https?://\S+', ' el enlace web ', text)
    # Extraer sólo el nombre de archivo en rutas largas de Windows o Linux
    text = re.sub(r'[A-Za-z]:\\[^\s]+?\\([^\s\\]+\.[a-zA-Z0-9]+)', r'\1', text)
    text = re.sub(r'file:///[^\s]+/([^\s/]+\.[a-zA-Z0-9]+)', r'\1', text)
    # Limpiar formato markdown inline
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\|[^\n]+\|', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'[*_~]', '', text)
    text = re.sub(r'[-=]{3,}', '', text)
    text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)
    text = text.replace('¿', '')
    text = re.sub(r'\?+', '.', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def traducir_terminos_tecnicos(texto: str) -> str:
    """Traduce términos y frases en inglés generados por el IDE a un español coloquial y natural."""
    if not texto:
        return ""

    reemplazos = [
        # Frases completas de confirmación
        (r"\bAllow checking git status\b", "¿Permitir verificar el estado del repositorio?"),
        (r"\bAllow inspecting Excel file\b", "¿Permitir inspeccionar el archivo de Excel?"),
        (r"\bAllow inspecting\b", "¿Permitir inspeccionar"),
        (r"\bAllow checking\b", "¿Permitir verificar"),
        (r"\bAllow running\b", "¿Permitir ejecutar"),
        (r"\bAllow\b", "¿Permitir"),

        # Acciones compuestas frecuentes de Antigravity
        (r"\bViewing lines (\d+) to (\d+) of (.+)", r"Leyendo las líneas \1 a \2 de \3"),
        (r"\bViewing lines (\d+) to (\d+)", r"Leyendo las líneas \1 a \2"),
        (r"\bViewing lines\b", "Leyendo las líneas"),
        (r"\bViewing file\b", "Leyendo el archivo"),
        (r"\bReading file\b", "Leyendo el archivo"),
        (r"\bEditing file\b", "Modificando el archivo"),
        (r"\bWriting file\b", "Guardando el archivo"),
        (r"\bRunning command\b", "Ejecutando la instrucción"),
        (r"\bSearching the web\b", "Buscando en la web"),
        (r"\bSearching directory\b", "Buscando en la carpeta"),
        (r"\bSearching in workspace\b", "Buscando en los archivos del proyecto"),
        (r"\bSemantic searching\b", "Búsqueda semántica en el proyecto"),
        (r"\bSemantic search\b", "Búsqueda semántica"),
        (r"\bDirectory analysis\b", "Análisis de la carpeta"),
        (r"\bWeb search\b", "Búsqueda en la web"),
        (r"\bFile edit\b", "Modificación del archivo"),
        (r"\bCommand execution\b", "Ejecución de instrucción en consola"),
        (r"\bTask status\b", "Estado de la tarea"),
        (r"\bStatus check\b", "Revisión de estado"),
        (r"\bListing directory contents\b", "Listando los archivos de la carpeta"),
        (r"\bList directory contents\b", "Listar los archivos de la carpeta"),
        (r"\bDirectory contents\b", "Contenido de la carpeta"),
        (r"\bChecking git status\b", "Verificando el estado del repositorio"),
        (r"\bGit status\b", "Estado del repositorio Git"),
        (r"\bChecking python processes\b", "Verificando procesos de Python"),
        (r"\bChecking command line\b", "Verificando la línea de comandos"),
        (r"\bReviewing setup and config\b", "Revisando la configuración"),
        (r"\bComparing file hashes\b", "Comparando integridad de archivos"),
        (r"\bFile hash differences\b", "Diferencias entre archivos"),
        (r"\bcompleted with exit code 0\b", "completado con éxito"),
        (r"\bexited with code 0\b", "finalizado con éxito"),
        (r"\buser denied permission\b", "permiso denegado por el usuario"),
        (r"\bpermission denied\b", "permiso no concedido"),

        # Gerundios y verbos en inglés
        (r"\bViewing\b", "Leyendo"),
        (r"\bReading\b", "Leyendo"),
        (r"\bChecking\b", "Verificando"),
        (r"\bInspecting\b", "Inspeccionando"),
        (r"\bAnalyzing\b", "Analizando"),
        (r"\bSearching\b", "Buscando"),
        (r"\bEditing\b", "Modificando"),
        (r"\bUpdating\b", "Actualizando"),
        (r"\bWriting\b", "Guardando"),
        (r"\bCreating\b", "Creando"),
        (r"\bDeleting\b", "Eliminando"),
        (r"\bComparing\b", "Comparando"),
        (r"\bDiffing\b", "Comparando"),
        (r"\bTesting\b", "Probando"),
        (r"\bBuilding\b", "Compilando"),
        (r"\bListing\b", "Listando"),
        (r"\bRunning\b", "Ejecutando"),
        (r"\bExecuting\b", "Ejecutando"),
        (r"\bScanning\b", "Escaneando"),
        (r"\bCleaning\b", "Limpiando"),
        (r"\bConverting\b", "Convirtiendo"),
        (r"\bOpening\b", "Abriendo"),
        (r"\bClosing\b", "Cerrando"),
        (r"\bNavigating to\b", "Navegando hacia"),
        (r"\bNavigating\b", "Navegando en"),
        (r"\bProcessing\b", "Procesando"),
        (r"\bStyling\b", "Estilizando"),

        # Sustantivos técnicos comunes
        (r"\bfiles\b", "archivos"),
        (r"\bfile\b", "archivo"),
        (r"\blines\b", "líneas"),
        (r"\bline\b", "línea"),
        (r"\bdirectory\b", "carpeta"),
        (r"\bfolder\b", "carpeta"),
        (r"\bworkspace\b", "proyecto"),
        (r"\bcontents\b", "contenido"),
        (r"\bcontent\b", "contenido"),
        (r"\bcode\b", "código"),
        (r"\bcommand\b", "instrucción"),
        (r"\bcommands\b", "instrucciones"),
        (r"\bstatus\b", "estado"),
        (r"\boutput\b", "resultado"),
        (r"\binput\b", "entrada"),
        (r"\bscript\b", "script"),
        (r"\blogic\b", "lógica"),
        (r"\bloop\b", "bucle"),
        (r"\btranscript\b", "registro de eventos"),
        (r"\btelemetry\b", "telemetría"),
        (r"\bvoice\b", "voz"),
        (r"\bspeech\b", "voz"),
        (r"\bthe web\b", "la web"),
        (r"\bweb\b", "web"),
        (r"\bhashes\b", "firmas de integridad"),
        (r"\bhash\b", "firma"),
        (r"\bdifferences\b", "diferencias"),
        (r"\bdifference\b", "diferencia"),
        (r"\bdatabase\b", "base de datos"),
        (r"\bprocesses\b", "procesos"),
        (r"\bprocess\b", "proceso"),
        (r"\bbranch\b", "rama"),
    ]

    res = texto
    for pat, esp in reemplazos:
        res = re.sub(pat, esp, res, flags=re.IGNORECASE)
    res = re.sub(r'\s{2,}', ' ', res).strip()
    return res

def convertir_a_confirmacion(texto: str) -> str:
    """Convierte una acción en una solicitud formal y clara de confirmación para el Señor Luis cuando el IDE pide permiso."""
    if not texto:
        return "Señor Luis, ¿me confirma por favor la ejecución de este comando?"
    t = traducir_terminos_tecnicos(texto).strip().strip('"\'?.')
    t = re.sub(r'^(allow\s+|permitir\s+|¿permitir\s+)', '', t, flags=re.IGNORECASE).strip()

    gerundios_a_infinitivo = [
        (r'^generando\b', 'generar'),
        (r'^ejecutando\b', 'ejecutar'),
        (r'^verificando\b', 'verificar'),
        (r'^analizando\b', 'analizar'),
        (r'^comprobando\b', 'comprobar'),
        (r'^instalando\b', 'instalar'),
        (r'^abriendo\b', 'abrir'),
        (r'^buscando\b', 'buscar'),
        (r'^limpiando\b', 'limpiar'),
        (r'^creando\b', 'crear'),
        (r'^modificando\b', 'modificar'),
        (r'^editando\b', 'editar'),
        (r'^actualizando\b', 'actualizar'),
        (r'^estilizando\b', 'estilizar'),
        (r'^inspeccionando\b', 'inspeccionar'),
        (r'^revisando\b', 'revisar'),
        (r'^leyendo\b', 'leer'),
        (r'^listando\b', 'listar'),
        (r'^probando\b', 'probar'),
        (r'^guardando\b', 'guardar'),
        (r'^comparando\b', 'comparar'),
    ]
    t_lower = t[0].lower() + t[1:] if len(t) > 1 else t.lower()
    for pattern, inf in gerundios_a_infinitivo:
        if re.search(pattern, t_lower, flags=re.IGNORECASE):
            t_lower = re.sub(pattern, inf, t_lower, flags=re.IGNORECASE)
            break
    return f"Señor Luis, ¿me confirma por favor para {t_lower}?"

def narrar_accion_coloquial(tool_name: str, tool_action: str, tool_summary: str, tool_args: dict = None) -> str:
    """Convierte la acción técnica del modelo y sus argumentos en una frase hablada 100% natural, específica y en español."""
    args = tool_args or {}
    act = (tool_action or "").strip().strip('"\'')
    sum_txt = (tool_summary or "").strip().strip('"\'')
    raw_desc = args.get('Description', '').strip()

    # 1. Extracción y nombre amigable del archivo
    target_path = args.get('TargetFile') or args.get('AbsolutePath') or ''
    target_filename = os.path.basename(target_path) if target_path else ''

    nombres_amigables = {
        "readme.md": "el archivo de documentación README",
        "jarvis_voice.py": "el script de voz de Jarvis",
        "iniciar_jarvis.bat": "el ejecutable de inicio de Jarvis",
        "transcript.jsonl": "el registro de eventos en vivo",
        "inventario_limpio.xlsx": "el archivo de inventario en Excel",
        "inventario_refaccionaria.db": "la base de datos de refacciones",
        "visor_n8n_canvas.html": "el visor interactivo de n8n",
        "package.json": "el archivo de configuración de dependencias",
        "requirements.txt": "el archivo de librerías de Python"
    }

    nombre_hablado = nombres_amigables.get(target_filename.lower(), f"el archivo {target_filename}" if target_filename else "")

    # 2. Petición de confirmación en comandos de consola (run_command)
    if tool_name == "run_command":
        cmd = args.get('CommandLine', '').strip()
        cmd_lower = cmd.lower()
        if "git push" in cmd_lower:
            return "Señor Luis, ¿me confirma por favor para subir los cambios a GitHub?"
        elif "git commit" in cmd_lower:
            return "Señor Luis, ¿me confirma por favor para registrar los cambios en Git?"
        elif any(k in cmd_lower for k in ["git status", "git diff", "git log"]):
            return "Señor Luis, ¿me confirma por favor para verificar el estado del repositorio?"
        elif "pip install" in cmd_lower or "npm install" in cmd_lower:
            return "Señor Luis, ¿me confirma por favor para instalar las dependencias necesarias?"
        elif "python" in cmd_lower:
            match_py = re.search(r'python\s+([^\s]+\.py)', cmd)
            if match_py:
                py_name = os.path.basename(match_py.group(1))
                return f"Señor Luis, ¿me confirma por favor para ejecutar {py_name}?"
            return "Señor Luis, ¿me confirma por favor para ejecutar el script de Python?"
        if act:
            return convertir_a_confirmacion(act)
        elif sum_txt:
            return convertir_a_confirmacion(sum_txt)
        return "Señor Luis, ¿me confirma por favor la ejecución de este comando en terminal?"

    # 3. Consultas interactivas al usuario (ask_question)
    if tool_name == "ask_question":
        return "Señor Luis, le he presentado una consulta en pantalla para conocer sus preferencias."

    # 4. Lectura / consulta de archivos e información (view_file)
    if tool_name == "view_file":
        start_line = args.get('StartLine')
        end_line = args.get('EndLine')

        if nombre_hablado:
            if start_line and end_line:
                return f"Leyendo las líneas {start_line} a {end_line} de {nombre_hablado}, Señor Luis."
            elif start_line:
                return f"Leyendo desde la línea {start_line} de {nombre_hablado}, Señor Luis."
            return f"Leyendo la información de {nombre_hablado}, Señor Luis."

        if act:
            act_trad = traducir_terminos_tecnicos(act)
            return f"{act_trad}, Señor Luis."
        return "Leyendo la información del archivo, Señor Luis."

    # 5. Edición y guardado de archivos (replace_file_content, write_to_file, etc.)
    if tool_name in ["replace_file_content", "write_to_file", "multi_replace_file_content"]:
        # Si la descripción viene en español y es clara
        if raw_desc and len(raw_desc) > 8 and not re.search(r'^[A-Z][a-z]+ing\b', raw_desc):
            desc_limpia = raw_desc.rstrip('.')
            desc_trad = traducir_terminos_tecnicos(desc_limpia)
            return f"{desc_trad}, Señor Luis."
        elif nombre_hablado:
            return f"Actualizando {nombre_hablado}, Señor Luis."
        return "Aplicando cambios en el proyecto, Señor Luis."

    # 6. Lectura de URLs y páginas web
    if tool_name in ["read_url_content", "read_browser_page"]:
        url = args.get('Url') or ''
        if url:
            dominio = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
            return f"Leyendo la información de {dominio}, Señor Luis."
        return "Leyendo la información de la página web, Señor Luis."

    # 7. Navegador web automatizado (browser_subagent)
    if tool_name == "browser_subagent":
        task_sum = args.get('TaskSummary', '') or sum_txt
        if task_sum:
            task_trad = traducir_terminos_tecnicos(task_sum)
            return f"{task_trad}, Señor Luis."
        return "Navegando en la web para consultar la información, Señor Luis."

    # 8. Búsqueda de código y texto
    if tool_name in ["grep_search", "search_web"]:
        q = args.get('Query') or args.get('query') or ''
        if q:
            q_clean = q.strip('"\'')
            if tool_name == "search_web":
                return f"Buscando en la web sobre '{q_clean}', Señor Luis."
            return f"Buscando '{q_clean}' en los archivos del proyecto, Señor Luis."
        return "Buscando la información en el proyecto, Señor Luis."

    # 9. Listado de carpetas
    if tool_name == "list_dir":
        dp = args.get('DirectoryPath', '')
        dir_name = os.path.basename(dp) if dp else "el proyecto"
        return f"Listando los archivos de la carpeta {dir_name}, Señor Luis."

    # 10. Fallback dinámico con traducción robusta
    frase_candidata = act or sum_txt
    if frase_candidata:
        frase = traducir_terminos_tecnicos(frase_candidata)
        return f"{frase}, Señor Luis."

    return "Procesando la información en este momento, Señor Luis."

async def generate_speech(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)

def get_latest_transcript() -> str:
    """Encuentra el archivo de transcript de la conversación activa más reciente."""
    brain_path = os.path.expanduser(r"~\.gemini\antigravity-ide\brain")
    pattern = os.path.join(brain_path, "*", ".system_generated", "logs", "transcript.jsonl")
    files = glob.glob(pattern)
    if not files:
        return ""
    return max(files, key=os.path.getmtime)

class MusicManager:
    def __init__(self):
        self.channel = pygame.mixer.Channel(1)
        self.current_track_name = "synthwave"
        self.sound = None
        self.target_volume = 0.50  # 50% por defecto
        self.duck_volume = 0.10    # 10% cuando Jarvis habla
        self.is_playing = False
        self.is_paused = False
        self.load_track(self.current_track_name)

    def load_track(self, track_name: str):
        if track_name in TRACKS and os.path.exists(TRACKS[track_name]):
            self.current_track_name = track_name
            self.sound = pygame.mixer.Sound(TRACKS[track_name])
            if self.is_playing:
                self.channel.play(self.sound, loops=-1, fade_ms=500)
                self.set_volume(self.target_volume)

    def start(self):
        if self.sound:
            self.channel.play(self.sound, loops=-1, fade_ms=1000)
            self.channel.set_volume(self.target_volume)
            self.is_playing = True
            self.is_paused = False

    def pause_toggle(self):
        if not self.is_playing:
            self.start()
            return "REANUDADA"
        if self.is_paused:
            self.channel.unpause()
            self.is_paused = False
            return "REANUDADA"
        else:
            self.channel.pause()
            self.is_paused = True
            return "PAUSADA"

    def set_volume(self, vol: float):
        self.target_volume = max(0.0, min(1.0, vol))
        if not self.is_paused and self.is_playing:
            self.channel.set_volume(self.target_volume)

    def duck(self):
        """Baja el volumen suavemente cuando Jarvis comienza a hablar."""
        if self.is_playing and not self.is_paused:
            self.channel.set_volume(self.duck_volume)

    def unduck(self):
        """Regresa el volumen a su nivel normal cuando Jarvis termina de hablar."""
        if self.is_playing and not self.is_paused:
            self.channel.set_volume(self.target_volume)

    def switch_next(self):
        names = list(TRACKS.keys())
        idx = (names.index(self.current_track_name) + 1) % len(names)
        self.load_track(names[idx])
        return names[idx]

def detect_chat_commands(user_text: str, music: MusicManager):
    """Detecta comandos de música escritos por el señor Luis en el chat."""
    text = user_text.lower()
    if any(k in text for k in ["subele", "sube la musica", "subele a la musica", "subir volumen", "mas volumen", "sube el volumen", "aumenta el volumen"]):
        new_vol = min(1.0, music.target_volume + 0.30 if music.target_volume < 0.9 else 1.0)
        music.set_volume(new_vol)
        print(f"\n🔊 [JARVIS]: Volumen aumentado al {int(music.target_volume * 100)}% por comando de chat.")
    elif any(k in text for k in ["bajale", "baja la musica", "bajale a la musica", "bajar volumen", "menos volumen", "baja el volumen", "disminuye el volumen"]):
        new_vol = max(0.10, music.target_volume - 0.25)
        music.set_volume(new_vol)
        print(f"\n🔉 [JARVIS]: Volumen disminuido al {int(music.target_volume * 100)}% por comando de chat.")
    elif "100%" in text or "al 100" in text or "cien por ciento" in text or "maximo" in text:
        music.set_volume(1.0)
        print("\n🎚️ [JARVIS]: Volumen de música ajustado al 100% por comando de chat.")
    elif "50%" in text or "al 50" in text or "cincuenta por ciento" in text:
        music.set_volume(0.50)
        print("\n🎚️ [JARVIS]: Volumen de música ajustado al 50% por comando de chat.")
    elif "pausa" in text or "silencia la musica" in text or "apaga la musica" in text or "deten la musica" in text:
        music.channel.pause()
        music.is_paused = True
        print("\n⏸️ [JARVIS]: Música pausada por comando de chat.")
    elif "lofi" in text or "lo-fi" in text:
        music.load_track("lofi")
        print("\n🎶 [JARVIS]: Cambiado a pista Lo-Fi Rhodes.")
    elif "synthwave" in text:
        music.load_track("synthwave")
        print("\n🎶 [JARVIS]: Cambiado a pista Synthwave Lab.")
    elif "cyber" in text or "cyberpunk" in text:
        music.load_track("cyber")
        print("\n🎶 [JARVIS]: Cambiado a pista Cyber Focus.")
    elif "ambient" in text or "stark" in text:
        music.load_track("ambient")
        print("\n🎶 [JARVIS]: Cambiado a pista Stark Ambient.")
    elif any(k in text for k in ["otra musica", "cambiar a otra", "cambia de musica", "cambia la musica", "siguiente musica", "otra cancion", "cambia cancion", "cambiar musica"]):
        nxt = music.switch_next()
        print(f"\n🎶 [JARVIS]: Pista alternada automáticamente a -> {nxt.upper()}")

def play_voice(voice_file: str, is_muted_ref, music: MusicManager):
    """Habla y gestiona el ducking de la música en tiempo real."""
    try:
        music.duck()
        pygame.mixer.music.load(voice_file)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if is_muted_ref[0]:
                pygame.mixer.music.stop()
                break

            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                if key == 's':
                    print("\n⏩ [JARVIS]: Voz detenida.")
                    pygame.mixer.music.stop()
                    break
                elif key == 'm':
                    is_muted_ref[0] = not is_muted_ref[0]
                    state = "MUTED" if is_muted_ref[0] else "ACTIVO"
                    print(f"\n🔇 [JARVIS]: Voz -> {state}")
                    pygame.mixer.music.stop()
                    break
                elif key == '1':
                    music.target_volume = 1.0
                    print("\n🎚️ [JARVIS]: Volumen fijado al 100%.")
                elif key == '5':
                    music.target_volume = 0.50
                    print("\n🎚️ [JARVIS]: Volumen fijado al 50%.")
                elif key == 'p':
                    st = music.pause_toggle()
                    print(f"\n🎵 [JARVIS]: Música {st}.")
                elif key == 't':
                    nxt = music.switch_next()
                    print(f"\n🎧 [JARVIS]: Cambiando a pista -> {nxt.upper()}")

            time.sleep(0.08)

        pygame.mixer.music.unload()
        music.unduck()
    except Exception as e:
        print(f"[Error en audio]: {e}")
        music.unduck()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 68)
    print(" 🤖 JARVIS TELEMETRÍA DE VOZ EN TIEMPO REAL - ANTIGRAVITY IDE")
    print("=" * 68)
    print(" [S]: Saltar / Callar voz actual   |  [M]: Mutear / Desmutear voz")
    print(" [1]: Música al 100%               |  [5]: Música al 50%")
    print(" [P]: Pausar / Reanudar música    |  [T]: Cambiar pista musical")
    print("=" * 68)
    print("💬 Comandos de chat disponibles: 'subele', 'bajale', '100%', '50%',")
    print("   'pausa', 'lofi', 'synthwave', 'cyber', 'ambient', 'otra musica'.")
    print("=" * 68)

    # Inicializar Pygame con 2 canales (Música + Voz)
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    music = MusicManager()
    music.start()
    print("🎵 [JARVIS]: Música de concentración activa de fondo (Synthwave Lab 50%).\n")

    audio_file = os.path.join(tempfile.gettempdir(), "jarvis_voice_temp.mp3")
    processed_steps = set()
    transcript_file = get_latest_transcript()
    is_muted = [False]
    last_tool_narration_time = 0

    if transcript_file:
        print(f"📡 Sesión vinculada: {os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(transcript_file))))}")
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        item = json.loads(line)
                        processed_steps.add(item.get('step_index'))
                    except Exception:
                        pass
        except Exception:
            pass

    saludo = "Sistemas en línea, Señor Luis. Telemetría de voz activa y música de concentración sincronizada."
    asyncio.run(generate_speech(saludo, audio_file))
    play_voice(audio_file, is_muted, music)

    while True:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                if key == '1':
                    music.set_volume(1.0)
                    print("\n🎚️ [JARVIS]: Música al 100%.")
                elif key == '5':
                    music.set_volume(0.50)
                    print("\n🎚️ [JARVIS]: Música al 50%.")
                elif key == 'p':
                    st = music.pause_toggle()
                    print(f"\n🎵 [JARVIS]: Música {st}.")
                elif key == 't':
                    nxt = music.switch_next()
                    print(f"\n🎧 [JARVIS]: Pista cambiada a: {nxt.upper()}")
                elif key == 'm':
                    is_muted[0] = not is_muted[0]
                    state = "🔴 MUTED" if is_muted[0] else "🟢 ACTIVO"
                    print(f"\n[JARVIS]: Estado voz -> {state}")

            curr = get_latest_transcript()
            if curr and curr != transcript_file:
                transcript_file = curr
                processed_steps.clear()

            if os.path.exists(transcript_file):
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            item = json.loads(line)
                            step_idx = item.get('step_index')
                            item_type = item.get('type')
                            status = item.get('status')
                            content = item.get('content')

                            # 1. Escuchar comandos del usuario desde el chat
                            if item_type == 'USER_INPUT' and content and step_idx not in processed_steps:
                                processed_steps.add(step_idx)
                                detect_chat_commands(content, music)

                            # 2. Narrar acciones del modelo en tiempo real mientras trabaja
                            elif item_type == 'PLANNER_RESPONSE' and item.get('tool_calls') and step_idx not in processed_steps:
                                processed_steps.add(step_idx)
                                if not is_muted[0] and (time.time() - last_tool_narration_time > 1.8):
                                    tc = item['tool_calls'][0]
                                    t_name = tc.get('name', '')
                                    t_args = tc.get('args', {})
                                    t_act = t_args.get('toolAction', '')
                                    t_sum = t_args.get('toolSummary', '')
                                    frase = narrar_accion_coloquial(t_name, t_act, t_sum, t_args)
                                    if frase:
                                        print(f"\n⚡ [JARVIS Acción en vivo]: {frase}")
                                        last_tool_narration_time = time.time()
                                        asyncio.run(generate_speech(frase, audio_file))
                                        play_voice(audio_file, is_muted, music)

                            # 3. Hablar respuestas finales de Jarvis
                            elif (item_type == 'PLANNER_RESPONSE' and 
                                  status == 'DONE' and 
                                  content and 
                                  step_idx not in processed_steps):
                                
                                processed_steps.add(step_idx)

                                if is_muted[0]:
                                    continue

                                speakable = clean_text_for_speech(content)
                                if len(speakable) > 10:
                                    print("\n🎙️ [JARVIS]: Hablando respuesta (Música atenuada)...")
                                    asyncio.run(generate_speech(speakable, audio_file))
                                    play_voice(audio_file, is_muted, music)
                                    print(f"✅ [JARVIS]: Respuesta concluida. Música restablecida al {int(music.target_volume*100)}%.")
                        except Exception:
                            continue

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n👋 Apagando Jarvis.")
            break
        except Exception:
            time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
