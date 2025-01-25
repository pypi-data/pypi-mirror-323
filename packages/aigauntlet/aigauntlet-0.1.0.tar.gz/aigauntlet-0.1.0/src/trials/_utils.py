import inspect
from typing import Callable, Type, get_type_hints

import requests
from pydantic import BaseModel


class TrialReport:
    """The base class for trial reports. Trial reports are
    what are returned when a trial is run."""

    pass


class TrialInterface:
    """Abstract base class for trial interfaces. A trial interface is how end users interact with a trial."""

    def __init__(
        self,
        email: str,
        api_key: str,
        input_format: Type[BaseModel],
        output_format: Type[BaseModel],
        interact_function: Callable,  # takes input_format, returns output_format
    ):
        # the format of the input that the agent will be receiving
        self.input_format: Type[BaseModel] = input_format
        # the format of the output that the agent will be returning
        self.output_format: Type[BaseModel] = output_format
        # the function that the agent will be using to get the input and return the output
        self.interact_function: Callable = interact_function

        # validate the input and output formats
        if not isinstance(self.input_format, BaseModel):
            raise ValueError("input_format must be a subclass of BaseModel")
        if not isinstance(self.output_format, BaseModel):
            raise ValueError("output_format must be a subclass of BaseModel")
        if not callable(self.interact_function):
            raise ValueError("interact_function must be a callable")

        # Make sure the input function fits the input / output formats.
        hints = get_type_hints(self.interact_function)
        sig = inspect.signature(self.interact_function)
        params = list(sig.parameters.values())

        if not params or len(params) != 1:
            raise ValueError("interact_function must take exactly one argument")

        param_type = hints.get(params[0].name)
        if param_type != self.input_format:
            raise ValueError(
                f"interact_function's input type must be {self.input_format}"
            )

        return_type = hints.get("return")
        if return_type != self.output_format:
            raise ValueError(
                f"interact_function's return type must be {self.output_format}"
            )

        # send a request to http://127.0.0.1:8000/check_user to make sure the user is valid
        response = requests.post(
            "http://127.0.0.1:8000/check_user",
            headers={"Authorization": api_key},
            json={"email": email},
        )
        if response.status_code != 200:
            raise ValueError("User is not valid")
        if response.json()["is_deleted"] is True:
            raise ValueError("User is deleted")
        if response.json()["credit_left"] <= 0:
            raise ValueError("User has no credits left")

    def run(self) -> TrialReport:
        """Runs the trial. Returns a trial report."""
        raise NotImplementedError("This method must be implemented in a derived class.")
