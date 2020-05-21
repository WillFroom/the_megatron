from typing import List

from html.parser import HTMLParser
from urllib import request

from .dialogue import Episode, Scene, Dialogue, StageDescription

class EpisodeParser(HTMLParser):
    TRANSCRIPT_ID = 'Transcript'
    def __init__(self):
        super().__init__()
        self.in_transcript = False
        self.tags: List[str] = []
        self.episode = Episode([])

    def handle_starttag(self, tag, attrs):
        if ('id', self.TRANSCRIPT_ID) in attrs:
            self.in_transcript = True
        self.tags.append(tag)

    def handle_endtag(self, tag):
        self.tags.pop()
        if tag == 'div' and self.in_transcript:
            self.in_transcript = False

    def handle_data(self, data):
        if self.in_transcript:
            if self.tags[-1] == 'b':
                self.add_dialogue(
                    data.split(':')[0],
                    None
                )
            elif self.tags[-1] == 'p':
                last_direction = self.current_scene.directions[-1]
                if isinstance(last_direction, Dialogue):
                    assert last_direction.speech is None, "ruh-ro!"
                    last_direction.speech = data.rstrip('\\n').replace('\\', '')
            elif self.tags[-1] == 'i':
                self.new_scene(data.strip('[]'))

    @property
    def current_scene(self) -> Scene:
        return self.episode.scenes[-1]

    def new_scene(self, stage_description):
        self.episode.add_scene()
        self.add_stage_description(stage_description)

    def add_dialogue(self, name, speech):
        self.current_scene.add_dialogue(name, speech)

    def add_stage_description(self, description):
        self.current_scene.add_stage_description(description)



def parse_page(url: str):
    with request.urlopen(url) as response:
        html_response = str(response.read())

    parser = EpisodeParser()
    parser.feed(html_response)

    print(parser.episode)
