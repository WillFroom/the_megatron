from typing import List, Union

from dataclasses import dataclass

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

    def add_stage_description(self, description):
        self.directions.append(StageDescription(description))

    def __repr__(self):
        return '\n'.join(repr(direction) for direction in self.directions)

@dataclass
class Episode():
    name: str
    scenes: List[Scene]

    def add_scene(self):
        self.scenes.append(Scene([]))

    def __repr__(self):
        return f'\n\nEpisode: {self.name}\n\n' + '\n\n'.join(repr(scene) for scene in self.scenes)
