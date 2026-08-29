from agents import Agent, Runner, set_tracing_disabled

set_tracing_disabled(True)


class Loop:
    def __init__(self, agent: Agent):
        self.agent = agent

    def run(self, task: str) -> str:
        return Runner.run_sync(self.agent, task).final_output
