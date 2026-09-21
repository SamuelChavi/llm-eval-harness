"""Model providers. The default is a deterministic MOCK so the harness runs and the
tests pass with no API key. Swap in RealProvider to evaluate an actual model.
"""


class MockProvider:
    """Deterministic answers keyed by case id. Intentionally seeded to produce ONE
    failure of each root cause, so the root-cause report has something to show:
      - speed-light  -> wrong number      (root cause = model)
      - everest-h    -> the CORRECTED value 8849, which mismatches the stale
                        expected 8848     (root cause = ground-truth)
      - translate-empty -> handled as malformed input before scoring (root cause = input)
    """
    name = "mock"

    ANSWERS = {
        "capital-fr": "The capital of France is Paris.",
        "water-boil": "Water boils at 100 degrees Celsius at sea level.",
        "mars-moons": "Mars has 2 moons, Phobos and Deimos.",
        "speed-light": "Approximately 150000 km/s.",              # WRONG -> model
        "romeo-author": "William Shakespeare wrote Romeo and Juliet.",
        "everest-h": "8849 meters (2020 re-survey).",             # corrected -> ground-truth
        "translate-empty": "No source text was provided.",        # malformed -> input
        "largest-ocean": "The Pacific Ocean is the largest.",
        "python-author": "Python was created by Guido van Rossum.",
        "one-prime": "No, 1 is not a prime number.",
    }

    def answer(self, case: dict) -> str:
        return self.ANSWERS.get(case["id"], "")


class RealProvider:
    """Stub for a real model. Implement `answer()` against an OpenAI-compatible API
    or a local Ollama server. Kept out of the default path so the repo runs offline.

    Example (OpenAI-compatible):
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(model=self.model,
                 messages=[{"role": "user", "content": case["input"]}])
        return resp.choices[0].message.content
    """
    name = "real"

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def answer(self, case: dict) -> str:
        raise NotImplementedError(
            "RealProvider is a stub. Implement answer() with your model API "
            "(see the docstring), then run: python -m src.harness --provider real"
        )


def get_provider(name: str = "mock"):
    return RealProvider() if name == "real" else MockProvider()
