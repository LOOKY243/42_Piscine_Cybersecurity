import sys, re, os, requests, signal, threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin


base_url = ""
visited_urls = set()
max_depth = -1
image_folder = "./data/"
executor = ThreadPoolExecutor(max_workers=10)
download_lock = threading.Lock()
Downloaded = set()


def handle_sigint(signal_number, frame):
    print("\nCtrl + C detected! Exiting...")
    executor.shutdown(wait=True)
    exit(0)


signal.signal(signal.SIGINT, handle_sigint)


def launch():
    ascii_art = r"""
 ________  ________  ___  ________  _______   ________      ________  ___    ___ 
|\   ____\|\   __  \|\  \|\   ___ \|\  ___ \ |\   __  \    |\   __  \|\  \  /  /|
\ \  \___|\ \  \|\  \ \  \ \  \_|\ \ \   __/|\ \  \|\  \   \ \  \|\  \ \  \/  / /
 \ \_____  \ \   ____\ \  \ \  \ \\ \ \  \_|/_\ \   _  _\   \ \   ____\ \    / / 
  \|____|\  \ \  \___|\ \  \ \  \_\\ \ \  \_|\ \ \  \\  \| __\ \  \___|\/  /  /  
    ____\_\  \ \__\    \ \__\ \_______\ \_______\ \__\\ _\|\__\ \__\ __/  / /    
   |\_________\|__|     \|__|\|_______|\|_______|\|__|\|__\|__|\|__||\___/ /     
   \|_________|  
   """

    for line in ascii_art.splitlines():
        print("\033[1m" + line + "\033[0m")


def DownloadImages(url):

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return

    pattern = r'(?:href|src)=["\']?([^"\'>]+(?:\.jpeg|\.jpg|\.png|\.gif|\.bmp))["\']?'
    image_links = re.findall(pattern, response.text)
    if image_links:
        if not os.path.isdir(image_folder):
            os.makedirs(image_folder)

    for link in image_links:
        try:
            image_url = urljoin(url, link)
            
            image_name = image_folder + image_url.split('/')[-1]
            with download_lock:
                if image_name in Downloaded:
                    continue
                Downloaded.add(image_name)

            image_response = requests.get(image_url)
            image_response.raise_for_status()
        
            content_type = image_response.headers.get("Content-Type")
            if "image" in content_type:
                with open(image_name, "wb") as handle:
                    handle.write(image_response.content)
                print(f"Downloaded: {image_name}")
        except requests.RequestException as e:
            continue


def RecursiveEnum(url, depth):
    if url[-1] != '/':
        url += '/'

    DownloadImages(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return
    
    pattern = r'(?:href|src)=["\']?([^"\'>]+)["\']?'
    matches = re.findall(pattern, response.text)
    for match in matches:
        full_url = urljoin(url, match)

        if full_url not in visited_urls:
            visited_urls.add(full_url)
            if depth + 1 <= max_depth or max_depth == -1:
                executor.submit(RecursiveEnum, full_url, depth + 1)


def ParseFlags(flags):
    global max_depth, image_folder
    seen_flags = set()
    i = 0
    while i < len(flags):
        flag = flags[i]
        if flag.startswith('-') and len(flag) > 1:
            flag_list = list(flag[1:])
            for j in range(len(flag_list)):
                if flag_list[j] == 'r' and 'r' not in seen_flags:
                    seen_flags.add('r')
                elif flag_list[j] == 'p' and 'p' not in seen_flags:
                    if i + 1 < len(flags):
                        image_folder = flags[i + 1]
                        if image_folder[-1] != '/':
                            image_folder += '/'
                        seen_flags.add('p')
                        i += 1
                    else:
                        print("Error: No path specified for -p")
                        return 2
                elif flag_list[j] == 'l' and 'l' not in seen_flags:
                    if i + 1 < len(flags):
                        try:
                            max_depth = int(flags[i + 1])
                            if max_depth <= 0:
                                print("Error: Invalid depth value for -l")
                                return 2
                            seen_flags.add('l')
                            i += 1
                        except ValueError:
                            print("Error: Invalid depth value for -l")
                            return 2
                    else:
                        max_depth = 5
                else:
                    print(f"Error: Invalid or repeated flag -{flag_list[j]}")
                    return 2
        else:
            print(f"Error: Invalid flag {flag}")
            return 2
        i += 1
    return 1 if 'r' in seen_flags else 0


def main():
    if len(sys.argv) == 1:
        print("Usage: python3 spider.py -[FLAGS] [URL]")
        return 1
    launch()
    global base_url
    base_url = sys.argv[-1]
    ret = ParseFlags(sys.argv[1:-1])
    if ret == 1 and max_depth != 1:
        RecursiveEnum(base_url, 1)
    elif ret == 0 or max_depth == 1:
        DownloadImages(base_url)
    else:
        return 1
    executor.shutdown(wait=True)
    return 0


if __name__ == "__main__":
    main()
