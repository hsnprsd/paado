from agents import Agent, Runner, set_tracing_disabled

set_tracing_disabled(True)


class Loop:
    def __init__(self, agent: Agent):
        self.agent = agent

    async def run(self, task: str) -> str:
        return (await Runner.run(self.agent, task)).final_output
