from enum import StrEnum


class AvailableModels(StrEnum):
    llama_small = "accounts/fireworks/models/llama-v3p1-8b-instruct"
    llama_medium = "accounts/fireworks/models/llama-v3p1-70b-instruct"
    llama_large = "accounts/fireworks/models/llama-v3p1-405b-instruct"
    # Function calling models
    mixtral_8x7b = "accounts/fireworks/models/mixtral-8x7b-instruct"
    mixtral_8x22b = "accounts/fireworks/models/mixtral-8x22b-instruct"
    firefunction_2 = "accounts/fireworks/models/firefunction-v2"
