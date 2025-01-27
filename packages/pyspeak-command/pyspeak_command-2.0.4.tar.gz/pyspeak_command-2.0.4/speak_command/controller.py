import subprocess as sp
import os, sys
import pyttsx3
import ftfy
# import utils as util
from deep_translator import GoogleTranslator
from speak_command import utils as util

engine = pyttsx3.init()
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "terminal_log.txt")

def run_normal_command(qtdArgs, cmd):
    if qtdArgs==3: #Tradução
        log_command(cmd[0])
        translate_log(cmd[1],cmd[2])
        read_log()
                
    elif qtdArgs==1: #Exibe o help
        log_command(cmd[0])
        util.change_voice("Portuguese")
        read_log()
    else:
        print('Error: Insira os argumentos corretamente!')
        util.speak('Error: Insira os argumentos corretamente!')
        sys.exit()

def run_help(qtdArgs, cmd):
    if qtdArgs==3: #Tradução
        util.text_help()
        translate_log(cmd[1],cmd[2])
        read_log()
                
    elif qtdArgs==1: #Exibe o help
        util.change_voice("Portuguese")
        util.save_log(util.text_help())
        read_log()

    else: #
        print('Error: Insira os argumentos corretamente!')
        util.speak('Error: Insira os argumentos corretamente!')
        sys.exit()

def run_scripts(qtdArgs, cmd):
    if qtdArgs==2:
        run_python_script(cmd[1])
        read_log()
    elif qtdArgs==4: #Tradução
        run_python_script(cmd[1])
        translate_log(cmd[2], cmd[3])
        read_log()
    else:
        print('Error: Insira os argumentos corretamente!')
        util.speak('Error: Insira os argumentos corretamente!')
        sys.exit()

def translate_log(lingua_ori, lingua_dst):
    try:
        util.change_voice(lingua_dst)
        lingua_ori = util.lang_suport(lingua_ori)
        lingua_dst = util.lang_suport(lingua_dst)
        translated = GoogleTranslator(source=lingua_ori, target=lingua_dst).translate_file(LOG_FILE)
        util.save_log(translated)
    except Exception as e:
        util.save_log(f"Erro na tradução: {e}")
        print(f"Erro na tradução: {e}")

def log_command(command):
    try:
        result = sp.run(
            command,
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.STDOUT
        )
        
        if os.name == 'nt':
            encoding = 'cp850'
        else:
            encoding = 'utf-8'
        
        output = result.stdout.decode(encoding, errors='replace')
        output = ftfy.fix_text(f"\n> {"".join(command)}\n{output}")

        util.save_log(output)
                    
    except Exception as e:
        util.save_log(f"Erro ao executar o comando: {e}")
        print(f"Erro ao executar o comando:: {e}")

def read_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding='utf-8') as file:
            output = file.read()
        print(output)
        util.speak(output)
    else:
        no_history = "Nenhum histórico encontrado."
        print(no_history)
        util.speak(no_history)


def run_python_script(script_name):
    current_directory = os.getcwd()
    script_path = os.path.join(current_directory, script_name)
    
    if not os.path.exists(script_path):
        error_msg = f"Erro: O arquivo '{script_name}' não foi encontrado no diretório '{current_directory}'"
        util.save_log(error_msg)
        return

    try:
        python_cmd = "python" if os.name == "nt" else "python3"
        
        result = sp.run(
            [python_cmd, script_path],
            capture_output=True,  
            text=True
        )

        stdout_text = ftfy.fix_text(result.stdout) if result.stdout else ""
        stderr_text = ftfy.fix_text(f"\nErros:\n{result.stderr}") if result.stderr else ""

        output = f"\n> {script_name}\n{stdout_text}{stderr_text}"

        util.save_log(output)
    
    except Exception as e:
        error_msg = f"Erro ao executar o script: {e}"
        util.save_log(error_msg)
        return