from providers import Model

SYSTEM = """\
Solve the task step by step.
When you are done, output a single line starting with FINAL: followed by the answer.
"""


class Loop:
    def __init__(self, model: Model):
        self.model = model

    def run(self, task: str) -> str:
        transcript = f"{SYSTEM}\nTask: {task}"
        while True:
            last = self.model.generate(transcript)
            transcript += f"\n{last}"
            if "FINAL:" in last:
                return last.split("FINAL:", 1)[1].strip()
