from typing import List, Union

from dataclasses import dataclass

@dataclass
class Dialogue:
    name: str
    speech: str

@dataclass
class StageDescription:
    description: str

@dataclass
class Scene:
    directions : List[Union[Dialogue, StageDescription]]

    def add_dialogue(self, name, speech):
        self.directions.append(Dialogue(name, speech))

    def add_stage_description(self, description):
        self.directions.append(StageDescription(description))

@dataclass
class Episode():
    scenes: List[Scene]

    def add_scene(self):
        self.scenes.append(Scene([]))
