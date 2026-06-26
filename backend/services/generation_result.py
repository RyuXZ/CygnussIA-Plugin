@dataclass(slots=True)
class GenerationResult:

    model: str

    response: str

    total_duration: float

    load_duration: float

    prompt_tokens: int

    completion_tokens: int