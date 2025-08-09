from collections import namedtuple
Point = namedtuple('Point', 'x, y')
from agent import Agent, MODEL_TO_USE

ai = Agent(model_path=MODEL_TO_USE)