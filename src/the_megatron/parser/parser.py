from typing import List, Tuple

from html.parser import HTMLParser
from urllib import request
import os.path
import re
import unicodedata
import urllib.parse

from .dialogue import PeepShow, Episode, Scene, Dialogue, StageDescription

# Turn a Unicode string to plain ASCII, thanks to
# https://stackoverflow.com/a/518232/2809427
def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if unicodedata.category(c) != 'Mn'
    )

class EpisodeParser(HTMLParser):
    TRANSCRIPT_ID = 'Transcript'
    def __init__(self, name: str):
        super().__init__()
        self.in_transcript = False
        self.in_p = False
        self.episode = Episode(name, [])

        self.current_paragraph = ""

        self.stage_re = re.compile(r'^\[(?P<stage_direction>.*)\]')
        # see https://transcripts.fandom.com/wiki/Spin_War
        self.alt_new_scene_re = re.compile(r'^-{5,}')
        self.diag_re = re.compile(r'^(?P<name>\w+):(?P<dialogue>.+)')

    def handle_starttag(self, tag, attrs):
        if ('id', self.TRANSCRIPT_ID) in attrs:
            self.in_transcript = True
        if tag == 'p' and self.in_transcript:
            self.in_p = True

    def handle_endtag(self, tag):
        if tag == 'p':
            if stage_match := self.stage_re.match(self.current_paragraph):
                self.new_scene(self.normalise_data(stage_match['stage_direction']))
            elif diag_match := self.diag_re.match(self.current_paragraph):
                if not self.episode.scenes:
                    self.new_scene('')
                self.add_dialogue(diag_match['name'], self.normalise_data(diag_match['dialogue']))
            elif self.alt_new_scene_re.match(self.current_paragraph):
                self.new_scene('')

            self.current_paragraph = ""
            self.in_p = False

        if tag == 'div' and self.in_transcript:
            self.in_transcript = False

    def handle_data(self, data):
        if self.in_p:
            # some data has spurious newlines in it!
            self.current_paragraph += data.replace('\n', ' ')

    def normalise_data(self, data):
        data = unicodeToAscii(data.lower().strip())

        # add a space before punctuation (and before closing bracket)
        # TODO maybe deal with dialogue stage directions differently
        data = re.sub(r"([\.!?,]+|\)|\])", r" \1", data)

        # add space after openening bracet
        data = re.sub(r"(\(|\[)", r"\1 ", data)

        # add space arround quotes
        data = re.sub(r"(\w)(\")", r"\1 \2", data)
        data = re.sub(r"(\")(\w)", r"\1 \2", data)

        return data

    @property
    def current_scene(self) -> Scene:
        return self.episode.scenes[-1]

    @property
    def current_directions(self):
        return self.current_scene.directions[-1]

    def new_scene(self, stage_description):
        self.episode.add_scene()
        self.add_stage_description(stage_description)

    def add_dialogue(self, name, speech):
        self.current_scene.add_dialogue(name, speech)

    def add_stage_description(self, description):
        self.current_scene.add_stage_description(description)


class EpisodeListParser(HTMLParser):
    LIST_ID = 'mw-content-text'
    def __init__(self):
        super().__init__()
        self.in_list = False
        self.tags: List[str] = []
        self.links: List[Tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        if ('id', self.LIST_ID) in attrs:
            self.in_list = True
            self.tags.append('div_list')
        else:
            self.tags.append(tag)

        if self.in_list:
            if self.tags[-1] == 'a' and self.tags[-2] == 'li':
                title = next(filter(lambda x: x[0] == 'title', attrs))[1]
                href = next(filter(lambda x: x[0] == 'href', attrs))[1]
                self.links.append((title, href))

    def handle_endtag(self, tag):
        if self.tags.pop() == 'div_list':
            self.in_list = False


def _get_html_response(url: str):
    with request.urlopen(url) as response:
        return str(response.read().decode('utf-8'))

def parse_episode(name: str, url: str) -> Episode:
    html_response = _get_html_response(url)

    parser = EpisodeParser(name)
    parser.feed(html_response)

    return parser.episode

def parse_all(url: str) -> PeepShow:
    html_response = _get_html_response(url)

    parser = EpisodeListParser()
    parser.feed(html_response)

    peep_show = PeepShow()
    for name, rel_url in parser.links:
        peep_show.add_episode(parse_episode(name, urllib.parse.urljoin(url, rel_url)))

    return peep_show
