import asyncio

from config import Config

_TIMEOUT_SECONDS = 60


class TerminalSession:
    def __init__(self, config: Config):
        self._config = config

    async def start(self):
        pass

    async def do_exec(self, script: str) -> str:
        proc = await asyncio.create_subprocess_exec(
            "bash",
            "-c",
            script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            stdout, _ = await asyncio.wait_for(
                proc.communicate(), timeout=_TIMEOUT_SECONDS
            )
        except TimeoutError:
            proc.kill()
            await proc.communicate()
            return "timed out"
        output = stdout.decode(errors="replace")
        if output and not output.endswith("\n"):
            output += "\n"
        return f"{output}exit code: {proc.returncode}"

    async def close(self):
        pass
