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

def narrar_accion_coloquial(tool_name: str, tool_action: str, tool_summary: str) -> str:
    """Convierte la acción técnica del modelo en una frase hablada 100% coloquial y fluida."""
    raw = (tool_action or tool_summary or "").strip().strip('"\'')
    raw_lower = raw.lower()

    if any(k in raw_lower for k in ["listing directory", "listar archivos", "list_dir"]):
        return "Voy a revisar los archivos de la carpeta, Señor Luis."
    elif any(k in raw_lower for k in ["reading file", "viewing file", "view_file", "consultando", "inspeccionando"]):
        return "Voy a echarle un vistazo a los archivos para ver los datos, Señor Luis."
    elif any(k in raw_lower for k in ["running command", "ejecutando", "run_command"]):
        if "pip" in raw_lower or "install" in raw_lower:
            return "Un momento, Señor Luis: voy a instalar la paquetería necesaria."
        elif "inventario" in raw_lower:
            return "Procesando el inventario y las compatibilidades, Señor Luis. Esto tomará unos segundos."
        return "Ejecutando la tarea en segundo plano, Señor Luis."
    elif any(k in raw_lower for k in ["editing file", "writing file", "write_to_file", "replace_file_content", "creando script", "actualizando"]):
        return "Haciendo unos ajustes en el código fuente, Señor Luis."
    elif any(k in raw_lower for k in ["searching", "grep", "buscando"]):
        return "Buscando la información en el sistema, Señor Luis."

    # Conversión fluida de gerundios en español
    gerundios = [
        ("Inspeccionando", "echarle un vistazo a"),
        ("Analizando", "analizar"),
        ("Revisando", "revisar"),
        ("Creando", "crear"),
        ("Ejecutando", "ejecutar"),
        ("Verificando", "verificar"),
        ("Instalando", "instalar"),
        ("Consultando", "consultar"),
        ("Actualizando", "actualizar"),
        ("Optimizando", "optimizar"),
        ("Modificando", "modificar"),
        ("Validando", "validar"),
        ("Buscando", "buscar"),
        ("Probando", "probar"),
        ("Guardando", "guardar"),
        ("Compilando", "compilar")
    ]

    col = raw
    for g, inf in gerundios:
        if col.startswith(g):
            col = inf + col[len(g):]
            break

    if col and len(col) > 4:
        return f"Voy a {col}, Señor Luis."

    return "Trabajando en ello en este momento, Señor Luis."

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
    if "100%" in text or "al 100" in text or "cien por ciento" in text:
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
                                if not is_muted[0] and (time.time() - last_tool_narration_time > 2.0):
                                    tc = item['tool_calls'][0]
                                    t_name = tc.get('name', '')
                                    t_args = tc.get('args', {})
                                    t_act = t_args.get('toolAction', '')
                                    t_sum = t_args.get('toolSummary', '')
                                    frase = narrar_accion_coloquial(t_name, t_act, t_sum)
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
