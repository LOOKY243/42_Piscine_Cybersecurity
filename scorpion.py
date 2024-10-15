import sys, os, subprocess, json

def launch():
    ascii_art = r"""
 ________  ________  ________  ________  ________  ___  ________  ________       ________  ___    ___ 
|\   ____\|\   ____\|\   __  \|\   __  \|\   __  \|\  \|\   __  \|\   ___  \    |\   __  \|\  \  /  /|
\ \  \___|\ \  \___|\ \  \|\  \ \  \|\  \ \  \|\  \ \  \ \  \|\  \ \  \\ \  \   \ \  \|\  \ \  \/  / /
 \ \_____  \ \  \    \ \  \\\  \ \   _  _\ \   ____\ \  \ \  \\\  \ \  \\ \  \   \ \   ____\ \    / / 
  \|____|\  \ \  \____\ \  \\\  \ \  \\  \\ \  \___|\ \  \ \  \\\  \ \  \\ \  \ __\ \  \___|\/  /  /  
    ____\_\  \ \_______\ \_______\ \__\\ _\\ \__\    \ \__\ \_______\ \__\\ \__\\__\ \__\ __/  / /    
   |\_________\|_______|\|_______|\|__|\|__|\|__|     \|__|\|_______|\|__| \|__\|__|\|__||\___/ /     
   \|_________|                                                                          \|___|/      
                      
   """

    for line in ascii_art.splitlines():
        print("\033[1m" + line + "\033[0m")

def ProcessFile(file):
    process = subprocess.Popen(["exiftool", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=False)
    output, errors = process.communicate()
    if not errors:
        width = 50
        signs_per_side = (width - len(file) - 2) // 2
        print("")
        print(f"\033[1m{'=' * signs_per_side} {file} {'=' * signs_per_side}\033[0m")
        print("")
        for line in output.splitlines():
            print(line.decode("utf-8"))
        
def CheckFileExt(file):
    file_extensions = ["png", "jpg", "jpeg", "bmp", "gif"]
    name_splits = file.split('.')
    if name_splits[-1] not in file_extensions:
        return 0
    return 1
    

def main():
    if len(sys.argv) <= 1:
        print("Usage: python3 scorpion.py FILE1 [FILE 2...]")
        return 0
    launch()
    for file in sys.argv[1:]:
        if not CheckFileExt(file):
            return 0
        else:
            ProcessFile(file)
    return 1
    


if __name__ == "__main__":
    main()