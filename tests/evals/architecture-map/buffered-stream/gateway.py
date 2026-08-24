from http_adapter import BufferedHttpAdapter


class Gateway:
    def __init__(self, http: BufferedHttpAdapter) -> None:
        self.http = http

    async def generate(self, prompt: str) -> list[str]:
        body = await self.http.post_json(
            "/generate",
            {"prompt": prompt, "stream": True},
        )
        return [line for line in body.splitlines() if line]
