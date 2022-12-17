from bs4 import BeautifulSoup
import requests, re, os, sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_help_page():
    print(f"{bcolors.HEADER}Example usage:{bcolors.ENDC}")
    print("python main.py <link> <quality_type?> <from_episode?> <to_episode?>")
    print(f"{bcolors.WARNING}if quality_type not specified - default value is 360p.")
    print(f"if from and to not specified - it will download all founded episodes.{bcolors.ENDC}")

def defineConfig(args = sys.argv):
    config = {
            "link": "",
            "quality_type": "360p",
            "from_episode": 0,
            "to_episode": 0,
            "headers": {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"}
    }
    if len(args) >= 2:
        config["link"] = args[1]
    else:
        print(f"{bcolors.FAIL}Link must be specified!")
        print_help_page()
        exit(1)
    if len(args) >= 3:
        config["quality_type"] = args[2]
    if len(args) >= 4:
        config["from_episode"] = int(args[3])
    if len(args) >= 5:
        config["to_episode"] = int(args[4])
    return config

config = defineConfig()

def download_file(url, filename):
    print(f"{bcolors.HEADER}downloading from: {url} to {filename}{bcolors.ENDC}");
    try:
        local_filename = "./"+filename
        with requests.get(url, headers=config["headers"], stream=True) as r:
            total_length = int(r.headers.get("content-length"))
            dl = 0
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(33 * dl / total_length) * 3
                    sys.stdout.write("\rStatus: %d%%" % (done))
                    sys.stdout.flush()
        print(f"\n{bcolors.OKGREEN}finished successfully{bcolors.ENDC}")
        return local_filename
    except Exception:
        print(f"{bcolors.FAIL}FATAL IN DOWNLOADING FILE{bcolors.ENDC}", Exeption)
        if os.path.exists(filename):
            os.remove(filename)
        exit()

resp_main = requests.get(config["link"], headers=config["headers"])
html_main = BeautifulSoup(resp_main.text, "html.parser")

episodes_buttons = html_main.find_all("a", {"class":"short-btn green video the_hildi"}, href=True)
if (len(episodes_buttons) > 0):
    dir_name = os.path.join("./", [*episodes_buttons[0].stripped_strings][0]);
    if not os.path.exists(dir_name):
        os.mkdir(os.path.join(dir_name))
    for el in episodes_buttons:
        if el:
            episode_number = int([*el.stripped_strings][1].split()[0])
            if config["from_episode"] > 0 and config["to_episode"] > 0 and not (episode_number in range(config["from_episode"], config["to_episode"] + 1)):
                continue
            if config["from_episode"] > 0 and episode_number < config["from_episode"]:
                continue
            if config["to_episode"] > 0 and episode_number > config["to_episode"]:
                continue
            resp_season = requests.get(el['href'], headers=config["headers"])
            html_season = BeautifulSoup(resp_season.text, "html.parser")
            filename = os.path.join(dir_name, el.text + "(" + config["quality_type"] + ").mp4")
            download_file(html_season.find("source", {"label": config["quality_type"]})["src"], filename)
    print(f"{bcolors.OKGREEN}%{bcolors.BOLD}episodes installed successfully!{bcolors.ENDC}")
else:
    print(f"{bcolors.FAIL}no episodes found!{bcolors.ENDC}")

