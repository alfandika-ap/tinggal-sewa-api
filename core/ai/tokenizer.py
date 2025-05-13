import tiktoken


def count_token(text: str):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    num_tokens = len(encoding.encode(text))
    return num_tokens
