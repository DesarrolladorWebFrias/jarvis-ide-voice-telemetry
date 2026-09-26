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
    """Limpia markdown, código y caracteres especiales para que suene fluido y natural."""
    if not text:
        return ""
    text = re.sub(r'```[\s\S]*?```', ' [Código omitido] ', text)
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
    """Traduce términos y frases comunes en inglés al español técnico y natural."""
    reemplazos = [
        ("Allow checking git status", "¿Permitir verificar el estado del repositorio?"),
        ("allow checking git status", "¿permitir verificar el estado del repositorio?"),
        ("Allow inspecting Excel file", "¿Permitir inspeccionar el archivo de Excel?"),
        ("allow inspecting Excel file", "¿permitir inspeccionar el archivo de Excel?"),
        ("Allow inspecting", "¿Permitir inspeccionar"),
        ("allow inspecting", "¿permitir inspeccionar"),
        ("Allow checking", "¿Permitir verificar"),
        ("allow checking", "¿permitir verificar"),
        ("Allow running", "¿Permitir ejecutar"),
        ("allow running", "¿permitir ejecutar"),
        ("Allow ", "¿Permitir "),
        ("allow ", "permitir "),
        ("Checking git status", "Verificando el estado del repositorio"),
        ("checking git status", "verificando el estado del repositorio"),
        ("Git status", "Estado del repositorio Git"),
        ("git status", "estado del repositorio Git"),
        ("Inspecting Excel file", "Inspeccionando el archivo de Excel"),
        ("inspecting Excel file", "inspeccionando el archivo de Excel"),
        ("Inspecting Excel", "Inspeccionando el archivo de Excel"),
        ("inspecting Excel", "inspeccionando el archivo de Excel"),
        ("Excel inventory structure", "la estructura del inventario"),
        ("Excel inventory data", "los datos del inventario en Excel"),
        ("Excel columns", "las columnas del archivo Excel"),
        ("Excel file", "el archivo de Excel"),
        ("excel file", "el archivo de Excel"),
        ("Listing directory contents", "Listando los archivos del directorio"),
        ("listing directory contents", "listando los archivos del directorio"),
        ("List directory contents", "Listar los archivos de la carpeta"),
        ("list directory contents", "listar los archivos de la carpeta"),
        ("Directory contents", "Contenido del directorio"),
        ("directory contents", "contenido del directorio"),
        ("Directory analysis", "Análisis del directorio"),
        ("directory analysis", "análisis del directorio"),
        ("workspace root directory", "el directorio principal del proyecto"),
        ("workspace root", "la raíz del proyecto"),
        ("parent directory contents", "los archivos del directorio superior"),
        ("parent directory", "el directorio superior"),
        ("Searching in workspace", "Buscando en los archivos del proyecto"),
        ("searching in workspace", "buscando en los archivos del proyecto"),
        ("Web search", "Búsqueda en la web"),
        ("web search", "búsqueda en la web"),
        ("File edit", "Modificación del archivo"),
        ("file edit", "modificación del archivo"),
        ("Command execution", "Ejecución de la instrucción en consola"),
        ("command execution", "ejecución de instrucción en consola"),
        ("Task status", "Estado de la tarea"),
        ("task status", "estado de la tarea"),
        ("Status check", "Revisión de estado"),
        ("status check", "revisión de estado"),
        ("completed with exit code 0", "completado con éxito"),
        ("exited with code 0", "finalizado con éxito"),
        ("user denied permission", "permiso denegado por el usuario"),
        ("permission denied", "permiso no concedido"),
        ("Inspecting", "Inspeccionando"),
        ("inspecting", "inspeccionando"),
        ("Checking", "Verificando"),
        ("checking", "verificando"),
        ("Viewing", "Revisando"),
        ("viewing", "revisando"),
        ("Reading", "Leyendo"),
        ("reading", "leyendo"),
        ("Running command", "Ejecutando la instrucción"),
        ("running command", "ejecutando la instrucción"),
        ("Running", "Ejecutando"),
        ("running", "ejecutando"),
        ("Listing", "Listando"),
        ("listing", "listando"),
        ("Searching", "Buscando"),
        ("searching", "buscando"),
        ("Editing", "Modificando"),
        ("editing", "modificando"),
        ("Updating", "Actualizando"),
        ("updating", "actualizando"),
        ("Writing", "Escribiendo"),
        ("writing", "escribiendo"),
        ("Opening", "Abriendo"),
        ("opening", "abriendo"),
        ("Navigating to", "Navegando hacia"),
        ("navigating to", "navegando hacia"),
        ("Navigating", "Navegando en"),
        ("navigating", "navegando en"),
        ("Processing", "Procesando"),
        ("processing", "procesando"),
        ("Styling", "Estilizando"),
        ("styling", "estilizando"),
        ("Analyzing", "Analizando"),
        ("analyzing", "analizando"),
        ("Cleaning", "Limpiando"),
        ("cleaning", "limpiando"),
        ("Converting", "Convirtiendo"),
        ("converting", "convirtiendo"),
        ("Testing", "Probando"),
        ("testing", "probando"),
        ("Executing", "Ejecutando"),
        ("executing", "ejecutando"),
        ("Creating", "Creando"),
        ("creating", "creando"),
        ("Scanning", "Escaneando"),
        ("scanning", "escaneando"),
        ("compatibility script", "el script de compatibilidad"),
        ("processing logic", "la lógica de procesamiento"),
        ("recent transcript items", "los eventos recientes de la sesión"),
        ("transcript processing", "el procesamiento de la sesión"),
        ("transcript parsing logic", "la lectura de eventos en tiempo real"),
        ("GitHub repository in default browser", "el repositorio de GitHub en el navegador"),
        ("GitHub repository", "el repositorio de GitHub"),
        ("repository in browser", "el repositorio en el navegador"),
        ("speech telemetry", "la telemetría de voz"),
        ("sample row from inventory", "una fila de muestra del inventario"),
        ("inventory data", "los datos del inventario"),
        ("auto parts inventory", "el inventario de refacciones"),
        ("auto parts", "las refacciones"),
        ("narration function", "la función de voz en vivo"),
        ("batch file", "el archivo por lotes"),
        ("file contents", "el contenido del archivo"),
        ("in default browser", "en el navegador"),
        ("inspection", "inspección"),
        ("structure", "estructura"),
        ("columns", "columnas"),
    ]
    res = texto
    for eng, esp in reemplazos:
        res = re.sub(re.escape(eng), esp, res)
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

    # Extraer nombre del archivo si aplica
    target_path = args.get('TargetFile') or args.get('AbsolutePath') or ''
    target_filename = os.path.basename(target_path) if target_path else ''

    # 1. Petición de confirmación en comandos de consola (El IDE muestra 'Allow <accion>?')
    if tool_name == "run_command":
        if act:
            return convertir_a_confirmacion(act)
        elif sum_txt:
            return convertir_a_confirmacion(sum_txt)
        cmd = args.get('CommandLine', '').strip()
        if "pip" in cmd.lower() or "install" in cmd.lower():
            return "Señor Luis, ¿me confirma por favor para instalar la paquetería necesaria?"
        elif "git" in cmd.lower():
            return "Señor Luis, ¿me confirma por favor para revisar el repositorio con Git?"
        return "Señor Luis, ¿me confirma por favor la ejecución de este comando en terminal?"

    # 2. Consultas interactivas al usuario
    if tool_name == "ask_question":
        return "Señor Luis, le he presentado una consulta en pantalla para conocer sus preferencias."

    # 3. Edición y guardado de archivos
    if tool_name in ["replace_file_content", "write_to_file", "multi_replace_file_content"]:
        if raw_desc and len(raw_desc) > 8:
            desc_limpia = raw_desc.rstrip('.')
            return f"{desc_limpia}, Señor Luis."
        elif target_filename:
            return f"Actualizando el archivo {target_filename}, Señor Luis."
        return "Aplicando cambios en el código, Señor Luis."

    # 4. Lectura / consulta de archivos
    if tool_name == "view_file":
        if act:
            act_trad = traducir_terminos_tecnicos(act)
            return f"{act_trad}, Señor Luis."
        elif target_filename:
            return f"Revisando el archivo {target_filename}, Señor Luis."
        elif sum_txt:
            base = traducir_terminos_tecnicos(sum_txt)
            return f"{base}, Señor Luis."
        return "Revisando el archivo correspondiente, Señor Luis."

    # 4. Navegador web
    if tool_name == "browser_subagent":
        task_sum = args.get('TaskSummary', '') or sum_txt
        if task_sum:
            task_trad = traducir_terminos_tecnicos(task_sum)
            return f"{task_trad}, Señor Luis."
        return "Navegando en el navegador web, Señor Luis."

    # 5. Búsqueda de código
    if tool_name in ["grep_search", "search_web"]:
        q = args.get('Query') or args.get('query') or ''
        if q:
            return f"Buscando coincidencias de '{q}', Señor Luis."
        return "Buscando referencias en el proyecto, Señor Luis."

    # 6. Listado de carpetas
    if tool_name == "list_dir":
        dp = args.get('DirectoryPath', '')
        dir_name = os.path.basename(dp) if dp else "el proyecto"
        return f"Listando los archivos de {dir_name}, Señor Luis."

    # 7. Fallback dinámico con traducción
    if act:
        frase = traducir_terminos_tecnicos(act)
        return f"{frase}, Señor Luis."
    elif sum_txt:
        frase = traducir_terminos_tecnicos(sum_txt)
        return f"{frase}, Señor Luis."

    return "Trabajando en la tarea en este momento, Señor Luis."

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
    print(" 🤖 SISTEMA JARVIS - MÓDULO DE VOZ Y MÚSICA DE CONCENTRACIÓN")
    print("=" * 68)
    print(" Controles rápidos por teclado:")
    print("  [1] -> Fijar música al 100%     [5] -> Fijar música al 50%")
    print("  [P] -> Pausar / Reanudar música [T] -> Cambiar pista (Synthwave / LoFi)")
    print("  [M] -> Silenciar / Activar voz  [S] -> Saltar respuesta actual")
    print("  [Q] -> Salir completamente")
    print("=" * 68)

    pygame.mixer.init(frequency=44100)
    music = MusicManager()
    music.start()  # Comienza a sonar la música de concentración
    print(f"🎵 Música de enfoque iniciada: {music.current_track_name.upper()} al 50% de volumen.")

    transcript_file = get_latest_transcript()
    if not transcript_file:
        print("❌ No se encontró archivo de conversación activo.")
        return

    print("📡 Conectado al entorno del señor Luis. Listo para trabajar.\n")

    processed_steps = set()
    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get('step_index') is not None:
                        processed_steps.add(data.get('step_index'))
                except Exception:
                    pass
    except Exception:
        pass

    is_muted = [False]
    temp_dir = tempfile.gettempdir()
    audio_file = os.path.join(temp_dir, "jarvis_temp_reply.mp3")
    last_tool_narration_time = 0.0

    while True:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                if key == 'q':
                    print("\n👋 Apagando sistemas. ¡Excelente jornada, señor Luis!")
                    break
                elif key == '1':
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

                            # Escuchar comandos del usuario desde el chat
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
