import re, sys, os, hashlib, hmac, argparse

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


def is_hexadecimal(string):
    pattern = r'^[0-9A-Fa-f]+$'
    return bool(re.match(pattern, string))


def CheckExtension(filename):
    return filename.lower().endswith(".hex")


def GFlag(key_file):
    if not CheckExtension(key_file):
        print("ft_otp.py: error: key must be a .hex file containing 64 hexadecimal characters.")
        return 0
    if not os.path.isfile(key_file):
        print(f"Error: Key {key_file} not found")
        return 0

    with open(key_file, 'r', encoding="utf-8") as f:
        line = f.readline().strip()
        print(f"{len(line)}: {line}")
        if len(line) != 64 or not is_hexadecimal(line):
            print("ft_otp.py: error: key must be 64 hexadecimal characters.")
            return 0
        key_bytes = bytes.fromhex(line)

    with open("ft_otp.key", "wb") as f:
        f.write(key_bytes)
        print("ft_otp.py: Success: key generated successfully")
    return 1


def hotp(key_bytes, counter):
    counter_bytes = counter.to_bytes(8, 'big')
    hmac_digest = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
    offset = hmac_digest[-1] & 0x0F
    truncated = hmac_digest[offset:offset+4]
    code = int.from_bytes(truncated, 'big') & 0x7FFFFFFF
    return code % 10**6


def KFlag(key_path):
    if not os.path.isfile(key_path):
        print(f"ft_otp.py: error: key file {key_path} not found")
        return 0

    try:
        with open(key_path, 'rb') as f:
            key_bytes = f.read()
    except:
        print("ft_otp.py: error: could not read key")
        return 0

    counter_file = "counter.txt"
    if not os.path.exists(counter_file):
        counter = 0
    else:
        with open(counter_file, 'r', encoding="utf-8") as f:
            counter = int(f.read())

    otp = hotp(key_bytes, counter)

    with open(counter_file, 'w') as f:
        f.write(str(counter + 1))

    print(f"ft_otp.py: Success: {otp:06d}")
    return 1


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", metavar="key.hex", help="Generate and save binary key from a 64-digit hex string")
    group.add_argument("-k", metavar="ft_otp.key", help="Use stored key to generate HOTP code")
    args = parser.parse_args()

    launch()

    if args.g:
        if not GFlag(args.g):
            sys.exit(1)
    elif args.k:
        if not KFlag(args.k):
            sys.exit(1)

if __name__ == "__main__":
    main()
