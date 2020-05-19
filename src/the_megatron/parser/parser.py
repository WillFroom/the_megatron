from typing import List

from html.parser import HTMLParser
from urllib import request

from .dialogue import Dialogue

class EpisodeParser(HTMLParser):
    TRANSCRIPT_ID = 'Transcript'
    def __init__(self):
        super().__init__()
        self.in_transcript = False
        self.tags: List[str] = []
        self.dialogue: List[Dialogue] = []

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
                self.dialogue.append(Dialogue(
                    data.split(':')[0],
                    None))
            elif self.tags[-1] == 'p':
                if self.dialogue and self.dialogue[-1].speech is None:
                    self.dialogue[-1].speech = data


def parse_page(url: str):
    with request.urlopen(url) as response:
        html_response = str(response.read())

    parser = EpisodeParser()
    parser.feed(html_response)

    print(parser.dialogue)
