"""Image description functions."""

from .base import describe_image, VisionModel, ModelFactory
from .ollama import describe_image_ollama, LlamaVisionModel
from .openai import describe_image_openai, GPT4VisionModel

# Register models with the factory
ModelFactory.register_model("llama", LlamaVisionModel)
ModelFactory.register_model("gpt4", GPT4VisionModel)

__all__ = [
    "describe_image",
    "describe_image_ollama",
    "describe_image_openai",
    "VisionModel",
    "ModelFactory",
    "LlamaVisionModel",
    "GPT4VisionModel",
]
