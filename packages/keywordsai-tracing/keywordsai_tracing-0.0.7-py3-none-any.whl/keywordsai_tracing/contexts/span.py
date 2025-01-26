from contextlib import contextmanager
import logging
from typing import Any, Dict
from opentelemetry import trace
from opentelemetry.trace.span import Span
from keywordsai_sdk.keywordsai_types.span_types import KEYWORDSAI_SPAN_ATTRIBUTES_MAP
from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIParams
from pydantic import ValidationError

logger = logging.getLogger(__name__)

@contextmanager
def keywordsai_span_attributes(keywordsai_params: Dict[str, Any] | KeywordsAIParams):
    """Adds KeywordsAI-specific attributes to the current active span.
    
    Args:
        keywordsai_params: Dictionary of parameters to set as span attributes.
                          Must conform to KeywordsAIParams model structure.
    
    Notes:
        - If no active span is found, a warning will be logged and the context will continue
        - If params validation fails, a warning will be logged and the context will continue
        - If an attribute cannot be set, a warning will be logged and the context will continue
    """
    current_span = trace.get_current_span()
    
    if not isinstance(current_span, Span):
        logger.warning("No active span found. Attributes will not be set.")
        yield
        return

    try:
        # Keep your original validation
        validated_params = (
            keywordsai_params 
            if isinstance(keywordsai_params, KeywordsAIParams) 
            else KeywordsAIParams.model_validate(keywordsai_params)
        )
        
        for key, value in validated_params.model_dump(mode="json").items():
            if key in KEYWORDSAI_SPAN_ATTRIBUTES_MAP:
                try:
                    current_span.set_attribute(KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key], value)
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Failed to set span attribute {KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key]}={value}: {str(e)}"
                    )
        yield
    except ValidationError as e:
        logger.warning(f"Failed to validate params: {str(e.errors(include_url=False))}")
        yield
    except Exception as e:
        logger.exception(f"Unexpected error in span attribute context: {str(e)}")
        raise
