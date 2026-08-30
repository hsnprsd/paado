from uuid import uuid4

from agents import Agent, Runner, SQLiteSession, set_tracing_disabled

set_tracing_disabled(True)


class Loop:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.session = SQLiteSession(str(uuid4()), db_path=":memory:")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        self.session.close()

    async def run(self, task: str) -> str:
        result = await Runner.run(self.agent, task, session=self.session)
        return result.final_output

    def stream(self, task: str):
        return Runner.run_streamed(self.agent, task, session=self.session)
