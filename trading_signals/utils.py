import pandas as pd
import numpy as np

def summarize_results(results):
    agg_returns = sum([r["Return [%]"] for r in results])
