LISTING_USER_PROMPT_V1 = """
TASK:
Your task is to act as "COSMO-Writer" and generate a complete Amazon product listing.

You must strictly adhere to all rules, instructions, and your core philosophy defined in the system prompt. Your output must be a single, valid JSON object.

The data for this specific product is provided below in the `INPUT_DATA` section.
INPUT_DATA:{keyword_seed}
"""
prompt_version = 1.0