from dataclasses import dataclass 


# use smolagents library for agentic workflows


@dataclass 
class AgentConfig:
    ...


class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config 

