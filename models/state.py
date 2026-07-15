from typing import TypedDict

import pandas as pd


class WorkflowState(TypedDict):

    df: pd.DataFrame

    profile: dict

    hypotheses: dict

    analysis: dict

    critic: dict

    report: dict

    memory: dict

    retry_count: int