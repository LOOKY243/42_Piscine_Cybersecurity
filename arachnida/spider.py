import sys, re, os, requests, signal
from concurrent.futures import ThreadPoolExecutor


base_url = ""
visited_urls = set()
wordlist = requests.get("https://raw.githubusercontent.com/3ndG4me/KaliLists/refs/heads/master/dirbuster/directory-list-lowercase-2.3-medium.txt")
max_depth = -1
image_folder = "./data/"
executor = ThreadPoolExecutor(max_workers=20)

def handle_sigint(signal_number, frame):
    print("\nCtrl + C detected! Exiting...")
    executor.shutdown(wait=True)
    exit(0)

signal.signal(signal.SIGINT, handle_sigint)

def DownloadImages(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return

    pattern = r'<img\s+[^>]*src="([^"]+\.(?:jpeg|jpg|png|gif|bmp))"'
    image_links = re.findall(pattern, str(response.content))

    if image_links:
        if not os.path.isdir(image_folder):
            os.makedirs(image_folder)

    for link in image_links:
        try:
            if link.startswith('http'):
                image_url = link
            else:
                image_url = base_url.rstrip('/') + '/' + link.lstrip('/')
            
            image_name = image_folder + image_url.split('/')[-1]
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            with open(image_name, "wb") as handle:
                handle.write(image_response.content)
            print(f"Downloaded: {image_name}")
        except requests.RequestException as e:
            print(f"Failed to download image from {link}: {e}")

def RecursiveEnum(url, depth):
    if url[-1] != '/':
        url += '/'
    if depth >= max_depth:
        return
    
    for word in wordlist.text.splitlines():
        if word.startswith('#'):
            continue
        full_url = url.rstrip('/') + '/' + word.lstrip('/')
        
        try:
            response = requests.get(full_url)
            if 200 <= response.status_code < 400:
                if full_url not in visited_urls:
                    visited_urls.add(full_url)
                    executor.submit(ThreadPath, full_url, depth + 1)
        except requests.RequestException as e:
            continue

def ThreadPath(url, depth):
    DownloadImages(url)
    RecursiveEnum(url, depth)

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
                            if max_depth < 0:
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
        return

    global base_url
    base_url = sys.argv[-1]
    ret = ParseFlags(sys.argv[1:-1])
    if ret == 1:
        RecursiveEnum(base_url, 0)
    elif ret == 0:
        DownloadImages(base_url)
    else:
        return
    executor.shutdown(wait=True)

if __name__ == "__main__":
    main()
