import re, sys, time, os, hashlib, hmac
def launch():
    ascii_art = r"""
 ________ _________        ________  _________  ________   ________  ___    ___ 
|\  _____\\___   ___\     |\   __  \|\___   ___\\   __  \ |\   __  \|\  \  /  /|
\ \  \__/\|___ \  \_|     \ \  \|\  \|___ \  \_\ \  \|\  \\ \  \|\  \ \  \/  / /
 \ \   __\    \ \  \       \ \  \\\  \   \ \  \ \ \   ____\\ \   ____\ \    / / 
  \ \  \_|     \ \  \       \ \  \\\  \   \ \  \ \ \  \___|_\ \  \___|\/  /  /  
   \ \__\       \ \__\       \ \_______\   \ \__\ \ \__\ |\__\ \__\ __/  / /    
    \|__|        \|__|        \|_______|    \|__|  \|__| \|__|\|__||\___/ /     
                                                                   \|___|/      
                                                                            
   """

    for line in ascii_art.splitlines():
        print("\033[1m" + line + "\033[0m")

def get_current_time():
    return int(time.time())


def is_hexadecimal(string):
    pattern = r'^[0-9A-Fa-f]+$'
    return bool(re.match(pattern, string))


def CheckExtension(filename):
    return filename.split('.')[-1] == 'hex'


def GFlag(key):
    if not CheckExtension(key):
        print("ft_otp.py: error: key must be 64 hexadecimal characters.")
        return 0
    if not os.path.isfile(key):
        print(f"Error: Key {key} not found")
        return 0

    with open(key, 'r') as handle:
        line = handle.readline().strip()
        if len(line) != 64 or not is_hexadecimal(line):
            print("ft_otp.py: error: key must be 64 hexadecimal characters.")
            return 0
        val = get_current_time()
        byte_arr = bytearray(val.to_bytes(8, sys.byteorder))
        hmac_digest = hmac.new(byte_arr, bytes.fromhex(line), hashlib.sha256).digest()

    with open("ft_otp.key", "wb") as handle:
        handle.write(hmac_digest)
        print("ft_otp.py: Success: key generated succesfully")
    return 1


def KFlag(key):

    with open(key, 'rb') as handle:
        hmac_digest = handle.read()

        val = get_current_time()
        byte_arr = bytearray(val.to_bytes(8, sys.byteorder))

        hmac_digest = hmac.new(byte_arr, hmac_digest, hashlib.sha256).digest()
        
        offset = hmac_digest[-1] & 0x0F
        truncated_hash = hmac_digest[offset:offset + 4]

        otp = int.from_bytes(truncated_hash, sys.byteorder) & 0x7FFFFFFF
        otp %= 10**6
    
    print(f"ft_otp.py: Success: {otp}")
    
    return 1


def main():
    launch()
    if len(sys.argv) <= 2:
        print("ft_otp.py: Usage: python3 ft_otp.py -[FLAG] [ARG]")
        print("ft_otp.py: This script does not handle flags -k and -g at the same time")
        return 1
    if sys.argv[1] == "-g":
        if not GFlag(sys.argv[2]):
            return 1
        return 0
    elif sys.argv[1] == "-k":
        if not KFlag(sys.argv[2]):
            return 1
        return 0
    print(f"ft_otp.py: error: Unknown flag {sys.argv[1]}")
    return 1
    

if __name__ == "__main__":
    main()