from typing import Dict, List, Union

from collections import defaultdict
from dataclasses import dataclass, field


character_dialogue: Dict[str, List[str]]= defaultdict(list)

@dataclass
class Dialogue:
    name: str
    speech: str

    def __repr__(self):
        return f"{self.name}: {self.speech}"

@dataclass
class StageDescription:
    description: str

    def __repr__(self):
        return f"[{self.description}]"

@dataclass
class Scene:
    directions : List[Union[Dialogue, StageDescription]]

    def add_dialogue(self, name, speech):
        self.directions.append(Dialogue(name, speech))
        character_dialogue[name].append(speech)

    def add_stage_description(self, description):
        self.directions.append(StageDescription(description))

    def __repr__(self):
        return '\n'.join(repr(direction) for direction in self.directions)

@dataclass
class Episode:
    name: str
    scenes: List[Scene]

    def add_scene(self):
        self.scenes.append(Scene([]))

    def __repr__(self):
        return f'Episode: {self.name}\n\n' + '\n\n'.join(repr(scene) for scene in self.scenes)

@dataclass
class PeepShow:
    episodes: List[Episode] = field(default_factory=list)

    def add_episode(self, episode):
        self.episodes.append(episode)

    def __repr__(self):
        return '\n\n'.join(repr(episode) for episode in self.episodes)
