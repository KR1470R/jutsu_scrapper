from bs4 import BeautifulSoup
import requests, os, sys

class bcolors:
    HEADER = '\033[95m';
    OKBLUE = '\033[94m';
    OKCYAN = '\033[96m';
    OKGREEN = '\033[92m';
    WARNING = '\033[93m';
    FAIL = '\033[91m';
    ENDC = '\033[0m';
    BOLD = '\033[1m';
    UNDERLINE = '\033[4m';

class ArgsManager:
    def __init__(self):
        self.args = sys.argv;
    def get(self, index):
        try:
            return self.args[index];
        except IndexError:
            return None;

class JutsuScrapper:
    def __init__(self, url, quality_type="360p", from_episode=0, to_episode=0):
        self.config = {
            "link": "",
            "quality_type": "360p",
            "from_episode": 0,
            "to_episode": 0,
            "headers": {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"}
        };
        self.acceptable_quality_types = ["360p", "480p", "720p", "1080p"];
        if url:
            self.config["link"] = url;
        else:
            print(f"{bcolors.FAIL}Link must be specified!{bcolors.ENDC}");
            self.print_help_page();
            exit(1);
        if quality_type != "360p":
            if quality_type in self.acceptable_quality_types:
                self.config["quality_type"] = quality_type;
            else:
                print(f"{bcolors.FAIL}{quality_type} is not acceptable quality type{bcolors.ENDC}");
                print(f"{bcolors.WARNING}acceptable quality types:", ", ".join(self.acceptable_quality_types), bcolors.ENDC);
                exit(1);
        if from_episode:
            self.config["from_episode"] = int(from_episode);
        if to_episode:
            self.config["to_episode"] = int(to_episode);

    def print_help_page(self):
        print(f"{bcolors.HEADER}Example usage:{bcolors.ENDC}");
        print("python main.py <link> <quality_type?> <from_episode?> <to_episode?>");
        print(f"{bcolors.WARNING}if quality_type not specified - default value is 360p.");
        print(f"if from and to not specified - it will download all founded episodes.{bcolors.ENDC}");

    def get_request(self, url, headers, stream = False):
        try:
            return requests.get(url, headers=headers, stream=stream);
        except requests.exceptions.RequestException as error:
            print(f"{bcolors.FAIL}FATAL ERROR: {error}");
            exit(1);

    def download_file(self, url, filename):
        print(f"{bcolors.HEADER}downloading from: {bcolors.OKBLUE}{url} {bcolors.HEADER}to {bcolors.WARNING}{filename}{bcolors.ENDC}");
        try:
            local_filename = "./"+filename;
            with  self.get_request(url, headers=self.config["headers"], stream=True) as r:
                total_length = int(r.headers.get("content-length"));
                dl = 0;
                r.raise_for_status();
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        dl += len(chunk);
                        f.write(chunk);
                        done = int(33 * dl / total_length) * 3;
                        sys.stdout.write("\rStatus: %d%%" % (done));
                        sys.stdout.flush();
            print(f"\n{bcolors.OKGREEN}finished successfully{bcolors.ENDC}");
            return local_filename;
        except Exception:
            print(f"{bcolors.FAIL}FATAL IN DOWNLOADING FILE{bcolors.ENDC}", Exeption);
            if os.path.exists(filename):
                os.remove(filename);
            exit(1);

    def validateURL(self, url):
        url_start = "https://jut.su";
        if url.startswith(url_start):
            return url;
        else:
            return url_start+url;

    def getHTMLOfPageEpisodes(self):
        response = self.get_request(self.config["link"], headers=self.config["headers"]);
        return BeautifulSoup(response.text, "html.parser");

    def getEpisodesButtons(self, htmlPage):
        buttons_classs = ["short-btn green video the_hildi", "short-btn black video the_hildi"];
        episodes_buttons = [];
        for button_class in buttons_classs:
            episodes_buttons += htmlPage.find_all("a", {"class": button_class}, href=True);
        return episodes_buttons;

    def downloadEpisodes(self, episodes_buttons):
        if (len(episodes_buttons) > 0):
            print(f"{bcolors.OKCYAN}found {bcolors.OKGREEN}{len(episodes_buttons)} {bcolors.OKCYAN}episodes{bcolors.ENDC}");
            dir_name = os.path.join("./", [*episodes_buttons[0].stripped_strings][0]);
            if not os.path.exists(dir_name):
                os.mkdir(os.path.join(dir_name));
            for el in episodes_buttons:
                if el:
                    episode_number = int([*el.stripped_strings][1].split()[0]);
                    if self.config["from_episode"] > 0 and self.config["to_episode"] > 0 and not (episode_number in range(self.config["from_episode"], self.config["to_episode"] + 1)):
                        continue;
                    if self.config["from_episode"] > 0 and episode_number < self.config["from_episode"]:
                        continue;
                    if self.config["to_episode"] > 0 and episode_number > self.config["to_episode"]:
                        continue;
                    resp_season = self.get_request(self.validateURL(el['href']), headers=self.config["headers"]);
                    html_season = BeautifulSoup(resp_season.text, "html.parser");
                    filename = os.path.join(dir_name, el.text + "(" + self.config["quality_type"] + ").mp4");
                    target_video = html_season.find("source", {"label": self.config["quality_type"]});
                    if target_video:
                        self.download_file(target_video["src"], filename);
                    else:
                        print(f"{bcolors.FAIL}couldn't find video target with {self.config['quality_type']} quality of {episode_number} episode. skipping{bcolors.ENDC}");
                        continue;
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}episodes installed successfully!{bcolors.ENDC}");
            exit(0);
        else:
            print(f"{bcolors.FAIL}no episodes found!{bcolors.ENDC}");
            exit(1);

    def startParse(self):
        episodes_page_html = self.getHTMLOfPageEpisodes();
        episodes_buttons = self.getEpisodesButtons(episodes_page_html);
        self.downloadEpisodes(episodes_buttons);

args = ArgsManager();
jutsu_scrapper = JutsuScrapper(args.get(1), args.get(2), args.get(3), args.get(4));
jutsu_scrapper.startParse();
