import sys, re, os, requests, threading, signal

wordlist = requests.get("https://raw.githubusercontent.com/3ndG4me/KaliLists/refs/heads/master/dirbuster/directory-list-lowercase-2.3-medium.txt")
visited_urls = []
threads = []

def handle_sigint(signal_number, frame):
    print("\nCtrl + C detected! Exiting...")
    exit(0)

signal.signal(signal.SIGINT, handle_sigint)

def DownloadImages(url):
    response = requests.get(url)
    if not response.ok:
        return
    pattern = r"https?://\S+\.(?:jpeg|jpg|png|gif|bmp)"
    image_links = re.findall(pattern, str(response.content))
    if len(image_links) > 0:
        if not os.path.isdir("images"):
            os.mkdir("images")
    for link in image_links:
        image_name = "images/" + link.split('/')[-1]
        image = requests.get(link)
        with open(image_name, "wb") as handle:
            handle.write(image.content)


def recursiveEnum(url):
    if url[-1] != '/':
        url += '/'
    for word in wordlist.text.splitlines():
        full_url = url + str(word)
        response = requests.get(full_url)
        if 200 <= response.status_code < 400:
            if response.url not in visited_urls:
                visited_urls.append(response.url)
                thread = threading.Thread(target=DownloadImages, args=(response.url,))
                threads.append(thread)
                thread.start()
                print(str(response.status_code) + ":     " + response.url)
    for thread in threads:
        threads.join()


def ParseFlags(flags):
    pass

def main():
    if len(sys.argv) == 1:
        return print("Usage: python3 spider.py -[FLAGS] [URL]")
    elif len(sys.argv) == 2:
        response = requests.get(sys.argv[1])
        if not response.ok:
            return print("Error: Invalid Url")
    elif len(sys.argv) >= 3:
        recursiveEnum(sys.argv[2])
        ParseFlags(sys.argv[1:-1])
    return 1

if __name__ == "__main__":
    main()