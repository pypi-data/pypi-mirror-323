from typing import Dict, Type


class TrialRegistry:
    _trials: Dict[str, Type] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(trial_class: Type):
            cls._trials[name] = trial_class
            return trial_class

        return decorator

    @classmethod
    def get_trial(cls, name: str) -> Type:
        if name not in cls._trials:
            raise ValueError(f"Trial {name} not found")
        return cls._trials[name]

    @classmethod
    def list_trials(cls) -> list[str]:
        return list(cls._trials.keys())
