"""prompt_builder – mix-in that injects an adaptive prompt based on weight."""

from pathlib import Path
import json
from shunollo_core.agents.base_hat_agent import _load_weight

_MANIFEST = json.loads(
    (Path(__file__).resolve().parents[2] / "agent_manifest.json").read_text()
)


class PromptBuilder:
    """Provides _build_prompt() for Hat agents."""

    def _build_prompt(self) -> str:
        role_key = self.role.lower()
        base = _MANIFEST.get(role_key, {}).get(
            "base_prompt",
            f"{role_key.title()}-Hat system guardian."
        )
        w = _load_weight(role_key)
        tone = (
            "high-confidence" if w > 0.75
            else "cautious" if w < 0.4
            else "balanced"
        )
        return f"{base} [tone:{tone}] (weight={w:.2f})"
