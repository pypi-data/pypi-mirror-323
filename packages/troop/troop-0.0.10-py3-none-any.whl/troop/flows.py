import json
from functools import wraps
from inspect import getdoc
from typing import TypeVar, get_type_hints

from openai import AsyncOpenAI
from pydantic import BaseModel

from .clients import OpenAIClient, BaseClient
from .types import Agent

T = TypeVar("T")


def ai_flow(client: BaseClient = OpenAIClient()):
    """
    A decorator that transforms a function into an AI-powered function using OpenAI's GPT.
    The function's docstring becomes the system prompt, its return type becomes the response format,
    and its parameters are converted into a JSON-like string for the user message.

    Example:
        @ai_function
        def summarize_text(text: str, max_words: int = 100) -> SummaryResponse:
            '''Generate a concise summary of the given text.'''
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            # Get the function's signature
            bound_args = func.__annotations__
            param_names = list(bound_args.keys())[:-1]  # Exclude return annotation

            params = {}
            if args:
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        params[param_names[i]] = arg
            params.update(kwargs)

            user_content = json.dumps(params, indent=2)
            system_prompt = getdoc(func) or ""
            return_type = get_type_hints(func).get("return", str)
            # Always use JSON response format for BaseModel and dict return types
            response_format = (
                {"type": "json_object"}
                if issubclass(return_type, (dict, BaseModel))
                else None
            )

            # For Pydantic models, append the expected schema to the system prompt
            if issubclass(return_type, BaseModel):
                schema = return_type.model_json_schema()
                system_prompt = f"{system_prompt}\n\nResponse must be a JSON object matching this schema:\n{json.dumps(schema, indent=2)}"

            response = await client.aget_chat_completion(
                agent=Agent(
                    model="gpt-4o",
                    instructions=system_prompt,
                ),
                history=[{"role": "user", "content": user_content}],
                context_variables={},
                model_override=None,
                stream=False,
                debug=False,
            )
            result = response.choices[0].message.content

            if issubclass(return_type, BaseModel):
                return return_type.model_validate_json(result)
            elif issubclass(return_type, dict):
                return json.loads(result)
            else:
                return result

        return wrapper
    return decorator
