from typing import List, Tuple

from html.parser import HTMLParser
from urllib import request
import os.path
import re
import unicodedata
import urllib.parse

from .dialogue import Episode, Scene, Dialogue, StageDescription

class EpisodeParser(HTMLParser):
    TRANSCRIPT_ID = 'Transcript'
    def __init__(self, name: str):
        super().__init__()
        self.in_transcript = False
        self.in_p = False
        self.tags: List[str] = []
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
        self.tags.append(tag)

    def handle_endtag(self, tag):
        self.tags.pop()
        if tag == 'p':
            if stage_match := self.stage_re.match(self.current_paragraph):
                self.new_scene(self.clean_string(stage_match['stage_direction']))
            elif diag_match := self.diag_re.match(self.current_paragraph):
                if not self.episode.scenes:
                    self.new_scene('')
                self.add_dialogue(diag_match['name'], self.clean_string(diag_match['dialogue']))
            elif self.alt_new_scene_re.match(self.current_paragraph):
                self.new_scene('')

            self.current_paragraph = ""
            self.in_p = False

        if tag == 'div' and self.in_transcript:
            self.in_transcript = False

    def clean_string(self, arg):
        # https://en.wikipedia.org/wiki/Unicode_equivalence#Normal_forms
        arg = unicodedata.normalize('NFKD', arg)
        return arg.rstrip('\\n').strip(' ').replace('\\', '')

    def handle_data(self, data):
        if self.in_p:
            self.current_paragraph += data

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

def parse_episode(name: str, url: str):
    html_response = _get_html_response(url)

    parser = EpisodeParser(name)
    parser.feed(html_response)

    return parser.episode

def parse_all(url: str):
    html_response = _get_html_response(url)

    parser = EpisodeListParser()
    parser.feed(html_response)

    return [
        parse_episode(name, urllib.parse.urljoin(url, rel_url))
        for name, rel_url in parser.links
    ]
