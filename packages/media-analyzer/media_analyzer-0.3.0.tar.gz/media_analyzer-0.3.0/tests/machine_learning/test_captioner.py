import os
from pathlib import Path

import pytest
from PIL import Image

from media_analyzer.data.enums.config_types import LLMProvider
from media_analyzer.machine_learning.caption.blip_captioner import BlipCaptioner
from media_analyzer.machine_learning.caption.llm_captioner import LLMCaptioner


@pytest.mark.cuda
def test_blip_captioner(
    assets_folder: Path,
) -> None:
    """Test the BlipCaptioner."""
    image = Image.open(assets_folder / "sunset.jpg")
    blip = BlipCaptioner()
    caption = blip.caption(image)
    assert isinstance(caption, str)
    min_caption_length = 3
    assert len(caption) > min_caption_length


@pytest.mark.cuda
def test_blip_captioner_conditional(
    assets_folder: Path,
) -> None:
    """Test the BlipCaptioner with a conditional caption."""
    image = Image.open(assets_folder / "sunset.jpg")
    blip = BlipCaptioner()
    caption = blip.caption(image, "A photo of ")
    assert isinstance(caption, str)
    min_caption_length = 3
    assert len(caption) > min_caption_length


@pytest.mark.parametrize(
    "llm_provider",
    [
        pytest.param(LLMProvider.MINICPM, marks=pytest.mark.cuda),
        LLMProvider.OPENAI,
    ],
)
def test_minicpm_captioner(
    assets_folder: Path,
    llm_provider: LLMProvider,
) -> None:
    """Test the LLMCaptioner with MiniCPM and OpenAI."""
    if llm_provider == LLMProvider.OPENAI and os.environ.get("OPENAI_API_KEY") is None:
        # Only run test if OPENAI_API_KEY is set.
        pytest.skip("OPENAI_API_KEY is not set, so OpenAI captioning test is skipped.")

    image = Image.open(assets_folder / "sunset.jpg")
    llm = LLMCaptioner(LLMProvider.MINICPM)
    caption = llm.caption(image)
    print(caption)
    assert isinstance(caption, str)
    min_caption_length = 3
    assert len(caption) > min_caption_length
