import enum
from collections.abc import Iterable
from typing import Any, TypeAlias

import dsp
import dspy
import pydantic

from sieves.engines.core import Engine, Executable

PromptSignature: TypeAlias = type[dspy.Signature] | type[dspy.Module]
Model: TypeAlias = dsp.LM | dspy.BaseLM
Result: TypeAlias = dspy.Prediction


class InferenceMode(enum.Enum):
    """Available inference modes.
    See https://dspy.ai/#__tabbed_2_6 for more information and examples.
    """

    # Default inference mode.
    predict = dspy.Predict
    # CoT-style inference.
    chain_of_thought = dspy.ChainOfThought
    # Agentic, i.e. with tool use.
    react = dspy.ReAct
    # For multi-stage pipelines within a task. This is handled differently than the other supported modules: dspy.Module
    # serves as both the signature as well as the inference generator.
    module = dspy.Module


class DSPy(Engine[PromptSignature, Result, Model, InferenceMode]):
    """Engine for DSPy."""

    def __init__(
        self,
        model: Model,
        config_kwargs: dict[str, Any] | None = None,
        init_kwargs: dict[str, Any] | None = None,
        inference_kwargs: dict[str, Any] | None = None,
    ):
        """
        :param model: Model to run. Note: DSPy only runs with APIs. If you want to run a model locally from v2.5
            onwards, serve it with OLlama - see here: # https://dspy.ai/learn/programming/language_models/?h=models#__tabbed_1_5.
            In a nutshell:
            > curl -fsSL https://ollama.ai/install.sh | sh
            > ollama run MODEL_ID
            > `model = dspy.LM(MODEL_ID, api_base='http://localhost:11434', api_key='')`
        :param config_kwargs: Optional kwargs supplied to dspy.configure().
        :param init_kwargs: Optional kwargs to supply to engine executable at init time.
        :param inference_kwargs: Optional kwargs to supply to engine executable at inference time.
        """
        super().__init__(model, init_kwargs, inference_kwargs)
        config_kwargs = {"max_tokens": 100000} | (config_kwargs or {})
        dspy.configure(lm=model, **config_kwargs)

    @property
    def inference_modes(self) -> type[InferenceMode]:
        return InferenceMode

    @property
    def supports_few_shotting(self) -> bool:
        return True

    def build_executable(
        self,
        inference_mode: InferenceMode,
        prompt_template: str | None,  # noqa: UP007
        prompt_signature: PromptSignature,
        fewshot_examples: Iterable[pydantic.BaseModel] = tuple(),
    ) -> Executable[Result | None]:
        # Note: prompt_template is ignored here, as DSPy doesn't use it directly (only prompt_signature_description).
        def execute(values: Iterable[dict[str, Any]]) -> Iterable[Result | None]:
            # Handled differently than the other supported modules: dspy.Module serves as both the signature as well as
            # the inference generator.
            if inference_mode == InferenceMode.module:
                assert isinstance(prompt_signature, dspy.Module), ValueError(
                    "In inference mode 'module' the provided prompt signature has to be of type dspy.Module."
                )
                generator = inference_mode.value(**self._init_kwargs)
            else:
                assert issubclass(prompt_signature, dspy.Signature)
                generator = inference_mode.value(signature=prompt_signature, **self._init_kwargs)

            # Compile predictor with few-shot examples.
            fewshot_examples_dict = DSPy._convert_fewshot_examples(fewshot_examples)
            examples = [dspy.Example(**fs_example) for fs_example in fewshot_examples_dict]
            generator = dspy.LabeledFewShot(k=5).compile(student=generator, trainset=examples)

            for doc_values in values:
                try:
                    yield generator(**doc_values, **self._inference_kwargs)
                except ValueError as err:
                    if self._strict_mode:
                        raise ValueError(
                            "Encountered problem when executing prompt. Ensure your few-shot examples and document "
                            "chunks contain sensible information."
                        ) from err
                    else:
                        yield None

        return execute
