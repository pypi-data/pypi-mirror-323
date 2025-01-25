import os
from pathlib import Path

import pytest
from PIL import Image

from media_analyzer.data.enums.config_types import LLMProvider
from media_analyzer.machine_learning.visual_llm.base_visual_llm import ChatMessage
from media_analyzer.machine_learning.visual_llm.get_llm import get_llm_by_provider


@pytest.mark.parametrize(
    "llm_provider",
    [
        pytest.param(LLMProvider.MINICPM, marks=pytest.mark.cuda),
        LLMProvider.OPENAI,
    ],
)
def test_minicpm_visual_llm(assets_folder: Path, llm_provider: LLMProvider) -> None:
    """Test the VisualLLM with MiniCPM and OpenAI."""
    if llm_provider == LLMProvider.OPENAI and os.environ.get("OPENAI_API_KEY") is None:
        # Only run test if OPENAI_API_KEY is set.
        pytest.skip("OPENAI_API_KEY is not set, so OpenAILLM test is skipped.")

    visual_llm = get_llm_by_provider(llm_provider)
    image = Image.open(assets_folder / "tent.jpg")
    answer = visual_llm.image_question(
        image=image,
        question="What type of vehicle is shown here?",
    )
    assert "car" in answer.lower()
    found_cat = False
    for message in visual_llm.stream_chat(
        [
            ChatMessage(message="What type of vehicle is shown here?", images=[image]),
        ],
    ):
        if "car" in message.lower():
            found_cat = True
    assert found_cat
