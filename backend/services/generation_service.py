@dataclass(slots=True)
class GenerationRequest:

    model: str

    prompt: str

    system: str | None = None

    temperature: float = 0.7

    top_p: float = 0.9

    repeat_penalty: float = 1.1

    stream: bool = False

    keep_alive: str = "30m"