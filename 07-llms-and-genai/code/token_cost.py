"""
token_cost.py - count tokens with tiktoken and estimate the cost of an LLM workload.

Run:  python token_cost.py --in-price 0 --out-price 0
      (replace 0 with the current prices per 1 million tokens from the provider's official pricing page)
Needs: tiktoken

Prices are NOT built in, because they change often. Look them up here:
  OpenAI:    https://openai.com/api/pricing/
  Anthropic: https://platform.claude.com/docs/en/about-claude/pricing
  Gemini:    https://ai.google.dev/gemini-api/docs/pricing
"""
import argparse
import tiktoken

enc = tiktoken.get_encoding("o200k_base")       # exact for recent OpenAI models; an estimate for others


def count_tokens(text):
    """Number of tokens in a piece of text."""
    return len(enc.encode(text))


def count_message_tokens(messages, per_message_overhead=4):
    """Rough count for a chat: content tokens plus a few tokens per message for role markers."""
    return sum(count_tokens(m["content"]) + per_message_overhead for m in messages)


def cost_per_request(input_tokens, output_tokens, in_price_per_m, out_price_per_m):
    """Cost in dollars of one call. Prices are per 1,000,000 tokens."""
    return input_tokens * in_price_per_m / 1_000_000 + output_tokens * out_price_per_m / 1_000_000


def monthly_cost(requests_per_day, input_tokens, output_tokens, in_price, out_price, days=30):
    return requests_per_day * days * cost_per_request(input_tokens, output_tokens, in_price, out_price)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Estimate LLM cost. Prices per 1M tokens, from the official page.")
    ap.add_argument("--in-price", type=float, required=True, help="input price per 1M tokens (USD)")
    ap.add_argument("--out-price", type=float, required=True, help="output price per 1M tokens (USD)")
    ap.add_argument("--requests-per-day", type=int, default=1000)
    ap.add_argument("--output-tokens", type=int, default=200, help="expected answer length in tokens")
    a = ap.parse_args()

    system = "You are a helpful support agent for an online bakery. Answer in under 80 words."
    user = "Hi, my cake order #5512 was supposed to arrive at 4pm but it's 6pm now. Can you check?"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    n_in = count_message_tokens(messages)
    per_req = cost_per_request(n_in, a.output_tokens, a.in_price, a.out_price)
    print(f"Input tokens per request (estimate): {n_in}")
    print(f"Output tokens per request (assumed): {a.output_tokens}")
    print(f"Cost per request:  ${per_req:.6f}")
    print(f"Cost per month:    ${monthly_cost(a.requests_per_day, n_in, a.output_tokens, a.in_price, a.out_price):.2f}"
          f"  ({a.requests_per_day} requests/day x 30 days)")
    if a.in_price == 0 and a.out_price == 0:
        print("Prices are 0 - fill in real prices from the official pricing page to get a real estimate.")
