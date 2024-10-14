import sys, re, os, requests, threading, signal

wordlist = requests.get("https://raw.githubusercontent.com/3ndG4me/KaliLists/refs/heads/master/dirbuster/directory-list-lowercase-2.3-medium.txt")
visited_urls = []
threads = []
max_depth = -1
image_folder = "./data/"

def handle_sigint(signal_number, frame):
    print("\nCtrl + C detected! Exiting...")
    exit(0)

signal.signal(signal.SIGINT, handle_sigint)

def ThreadPath(url, depth):
    DownloadImages(url)
    RecursiveEnum()
    

def DownloadImages(url):
    response = requests.get(url)
    if not response.ok:
        return 
    pattern = r"https?://\S+\.(?:jpeg|jpg|png|gif|bmp)"
    image_links = re.findall(pattern, str(response.content))
    if len(image_links) > 0:
        if not os.path.isdir(image_folder):
            os.mkdir(image_folder)
    for link in image_links:
        image_name = image_folder + link.split('/')[-1]
        image = requests.get(link)
        with open(image_name, "wb") as handle:
            handle.write(image.content)


def RecursiveEnum(url, depth):
    if url[-1] != '/':
        url += '/'
    if (depth == max_depth):
        return 
    
    for word in wordlist.text.splitlines():
        if (word.startswith('#')):
            continue
        print(word)
        full_url = url + str(word)
        response = requests.get(full_url)

        if 200 <= response.status_code < 400:
            with threading.Lock():
                if response.url not in visited_urls:
                    visited_urls.append(response.url)
                    thread = threading.Thread(target=DownloadImages, args=(response.url,))
                    threads.append(thread)
                    thread.start()
                    print(f"{response.status_code}: {response.url.split('/')[-1]}")
                    
    for thread in threads:
        threads.join()

def ParseFlags(flags):
    global max_depth
    global image_folder
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
                        return 2, print("Error: No path specified for -p")

                elif flag_list[j] == 'l' and 'l' not in seen_flags:
                    if i + 1 < len(flags):
                        try:
                            max_depth = int(flags[i + 1])
                            seen_flags.add('l')
                            i += 1
                        except ValueError:
                            return 2, print("Error: Invalid depth value for -l")
                    else:
                        return 2, print("Error: No depth specified for -l")

                else:
                    return 2, print(f"Error: Invalid or repeated flag {flag_list[j]}")

        else:
            return print(f"Error: Invalid flag {flag}")
        
        i += 1
    if ('r' in seen_flags):
        return 1
    return 0

def main():
    if len(sys.argv) == 1:
        return print("Usage: python3 spider.py -[FLAGS] [URL]")
    ret = ParseFlags(sys.argv[1:-1])
    if ret == 1:
        RecursiveEnum(sys.argv[-1], 0)
    elif not ret:
        RecursiveEnum(sys.argv[-1], 0)
    else:
        return 0
    return 1

if __name__ == "__main__":
    main()