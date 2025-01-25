###############################################################
#### BiasedEvaluationTrial: A trial for an AI that is used to
# evaluate a textual input. The trial is failed if the AI uses
# some improper factor to evaluate the input. For example, if
# the AI is meant to consider resumes for a job, and it assigns
# a different score to two resumes just because they differ in
# gender, then it fails the trial.
###############################################################

from trials._utils import packageInterface, packageReport
from pydantic import BaseModel, Field
from typing import Callable, Type


class BiasedEvaluationTrial_OutputFormat(BaseModel):
    evaluationScore: float = Field(
        ...,
        title="evaluation score",
        description="Rating assigned to the input. 1 is highest score, 0 is lowest score.",
    )


class BiasedEvaluationTrial(packageInterface):
    """A package that checks for biased evaluations."""

    def __init__(self, inputFormat: Type[BaseModel], inputFunction: Callable):
        # define the required input and output formats
        super().__init__(inputFormat, BiasedEvaluationTrial_OutputFormat, inputFunction)

    def run(self) -> packageReport:
        """Runs the package. Returns a package report."""
        raise NotImplementedError("This method must be implemented in a derived class.")
