import os
import pyttsx3
import keyboard, threading
import ftfy

keypress_event = threading.Event()
engine = pyttsx3.init()
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "terminal_log.txt")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

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
    engine.stop()

def detect_keypress():
    while not keypress_event.is_set():
        if keyboard.is_pressed('esc'):
            print("Parando a fala...")
            stop_speaking()
            keypress_event.set()
            break

def keyPressed():
    keypress_event.clear()
    keypress_thread = threading.Thread(target=detect_keypress, daemon=True)
    keypress_thread.start()
    
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
            log.write(content+"\n")
            log.flush()
    except Exception as e:
        with open(LOG_FILE, "w", encoding='utf-8') as log:
            log.write(f"Erro ao salvar o arquivo: {str(e)}\n")
        print(f"Erro: {e}")