import os
import pyttsx3
from pynput import keyboard
import threading
import ftfy

key_listener = None
engine = pyttsx3.init()

if os.name == "nt":
    LOG_DIR = os.path.join(os.getenv("APPDATA"), "speak_command", "logs")
else:
    LOG_DIR = os.path.expanduser("~/.speak_command/logs")

os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "terminal_log.txt")

def lang_suport(lingua):
    idiomas_suportados = {
        "afrikaans": "af", "albanian": "sq", "amharic": "am", "arabic": "ar",
        "armenian": "hy", "assamese": "as", "aymara": "ay", "azerbaijani": "az",
        "bambara": "bm", "basque": "eu", "belarusian": "be", "bengali": "bn",
        "bhojpuri": "bho", "bosnian": "bs", "bulgarian": "bg", "catalan": "ca",
        "cebuano": "ceb", "chichewa": "ny", "chinese (simplified)": "zh-CN",
        "chinese (traditional)": "zh-TW", "corsican": "co", "croatian": "hr",
        "czech": "cs", "danish": "da", "dutch": "nl", "english": "en",
        "esperanto": "eo", "estonian": "et", "finnish": "fi", "french": "fr",
        "german": "de", "greek": "el", "haitian creole": "ht", "hindi": "hi",
        "hungarian": "hu", "icelandic": "is", "indonesian": "id", "italian": "it",
        "japanese": "ja", "korean": "ko", "latvian": "lv", "lithuanian": "lt",
        "malay": "ms", "norwegian": "no", "persian": "fa", "polish": "pl",
        "portuguese": "pt", "romanian": "ro", "russian": "ru", "serbian": "sr",
        "slovak": "sk", "slovenian": "sl", "spanish": "es", "swahili": "sw",
        "swedish": "sv", "thai": "th", "turkish": "tr", "ukrainian": "uk",
        "urdu": "ur", "vietnamese": "vi", "welsh": "cy", "yiddish": "yi", "zulu": "zu"
    }
    lingua = lingua.lower()
    if lingua in idiomas_suportados.values():
        return lingua  

    if lingua in idiomas_suportados:
        return idiomas_suportados[lingua]

    raise ValueError(
        f"Idioma '{lingua}' não suportado. Use um dos seguintes: {list(idiomas_suportados.keys()) + list(idiomas_suportados.values())}"
    )

def change_voice(language):
    voices = engine.getProperty('voices')
    i = 0
    for voice in voices:
        voice.name = voice.name.lower()
        if language.lower() in voice.name.split():
            engine.setProperty('voice', voice.id)
            break


def speak(text):
    keyPressed()
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Erro ao falar: {e}")

def stop_speaking():
    global key_listener
    engine.stop()
    if key_listener:
        key_listener.stop()

def detect_keypress():
    global key_listener
    key_listener = keyboard.Listener(on_press=on_press)
    key_listener.start()
        
def on_press(key):
    try:
        if key == keyboard.Key.esc:
            print("Parando a fala...")
            stop_speaking()
            return False  # Interrompe o listener
    except:
        pass

def keyPressed():
    detect_keypress()
    
def text_help() -> str:
    string = """Como Utilizar a biblioteca:
  scmd <comando> [opções]

Opções gerais:
  --help, --h                                                    Mostra os comandos da biblioteca.
  --help [Lingua de Destino]                                     Traduz e mostra os comandos da biblioteca.
  --pyFile <Nome do arquivo.py>                                  Lê a saída do arquivo ou o erro que deu.
  --pyFile [Lingua de Origem] [Lingua de Destino]                Traduz, e lê a saída do arquivo ou o erro que deu.
  
    """
    return string

def save_log(content):
    try:
        with open(LOG_FILE, "w", encoding='utf-8', errors='replace') as log:
            log.write(content + "\n")
            log.flush()
    except Exception as e:
        print(f"Erro ao salvar o log: {e}")