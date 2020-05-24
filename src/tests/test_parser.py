from the_megatron.parser.dialogue import character_dialogue
from the_megatron.parser.parser import parse_all


if __name__ == '__main__':
    episodes = parse_all('https://transcripts.fandom.com/wiki/Peep_Show')

    print(episodes)
