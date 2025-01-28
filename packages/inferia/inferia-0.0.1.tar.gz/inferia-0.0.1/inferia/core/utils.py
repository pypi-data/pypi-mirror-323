import importlib
import inspect
import logging
from inspect import signature, Parameter
from typing import Any, Callable, get_type_hints

from pydantic import Field, create_model

from inferia.api.responses import ResultResponse
from inferia.core.models import BasePredictor
from inferia.core.exceptions import InvalidHandlerSignature


def load_predictor(class_path) -> Any:
    predictor_path, predictor_class = class_path.split(":")
    module = importlib.import_module(f"{predictor_path}")

    if not hasattr(module, predictor_class):
        raise AttributeError(
            f"Class {predictor_class} not found in module {predictor_path}"
        )

    predict_class = getattr(module, predictor_class)

    # Build an instance of the class
    predict_instance = predict_class()

    # Instantiate and return the class
    return predict_instance


def get_predictor_handler_return_type(predictor: BasePredictor):
    """This method returns the type of the output of the predictor.predict method"""
    # Get the return type of the predictor.predict method
    return_type = predictor.predict.__annotations__.get("return", None)

    # Create a new dynamic type based on ResultResponse, with the correct module and annotated field
    return type(
            f"{predictor.__class__.__name__}Response",
            (ResultResponse,),
            {
                "__annotations__": {"result": return_type},  # Annotate the result field with the return type
                "__module__": ResultResponse.__module__,  # Ensure the module is set correctly for Pydantic
            },
    )
def wrap_handler(class_name: str, original_handler: Callable) -> Callable:
    sig = signature(original_handler)
    type_hints = get_type_hints(original_handler)

    input_fields = {}
    for name, param in sig.parameters.items():
        param_type = type_hints.get(name, Any)
        default_value = param.default if param.default != Parameter.empty else ...
        input_fields[name] = (param_type, Field(default=default_value))
    InputModel = create_model(f"{class_name}.Input", **input_fields)

    # Check if the original handler is an async function
    if inspect.iscoroutinefunction(original_handler):
        async def handler(input: InputModel):
            result = await original_handler(**input.model_dump())
            return result
    else:
        def handler(input: InputModel):
            return original_handler(**input.model_dump())

    handler.__annotations__ = {
        "input": InputModel,
        'return': type_hints.get("return", Any)
    }
    logging.debug(f"Handler of {original_handler.__name__} annotated with {handler.__annotations__}")
    return handler
