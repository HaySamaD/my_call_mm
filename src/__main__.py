import argparse
import json
import numpy as np
from llm_sdk import Small_LLM_Model


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(functions: list[dict], user_prompt: str) -> str:
    lines = ["Choose ONLY one function name from this list, or 'none':"]
    for fn in functions:
        lines.append(f"- {fn['name']}: {fn['description']}")
    lines.append('Reply ONLY with JSON like: {"name": "fn_name"}')
    lines.append(f"User prompt: {user_prompt}")
    lines.append('Assistant: {"name": "')
    return "\n".join(lines)


def get_vocab(model: Small_LLM_Model) -> dict[str, int]:
    path = model.get_path_to_tokenizer_file()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("model", {}).get("vocab", {})


def pick_best_function(
    model: Small_LLM_Model,
    vocab: dict[str, int],
    functions: list[dict],
    user_prompt: str,
    max_tokens: int = 15,
) -> str:
    allowed_names = [fn["name"] for fn in functions] + ["none"]
    prompt_text = build_prompt(functions, user_prompt)

    input_ids = model.encode(prompt_text)[0].tolist()
    chosen_name_chars = ""

    for _ in range(max_tokens):
        logits = np.array(model.get_logits_from_input_ids(input_ids), dtype=np.float32)

        valid_ids = []
        for token_str, token_id in vocab.items():
            if not token_str or "\n" in token_str or "\r" in token_str:
                continue

            clean_part = token_str.replace('"', "")
            candidate = chosen_name_chars + clean_part

            if '"' in token_str:
                if chosen_name_chars in allowed_names:
                    valid_ids.append(token_id)
            else:
                if any(name.startswith(candidate) for name in allowed_names):
                    valid_ids.append(token_id)

        if valid_ids:
            masked = np.full_like(logits, -1e9)
            masked[valid_ids] = logits[valid_ids]
            next_id = int(np.argmax(masked))
        else:
            next_id = int(np.argmax(logits))

        next_piece = model.decode([next_id])
        input_ids.append(next_id)

        if '"' in next_piece:
            break
        chosen_name_chars += next_piece

    final_name = chosen_name_chars.strip().strip('"')
    return final_name if final_name in allowed_names else "none"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/input/function_calling_tests.json")
    parser.add_argument("--functions_definition", default="data/input/functions_definition.json")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--show", choices=["name", "description"], default="name")
    parser.add_argument("--max_tokens", type=int, default=15)
    args = parser.parse_args()

    model = Small_LLM_Model(model_name=args.model)
    vocab = get_vocab(model)
    functions = load_json(args.functions_definition)
    tests = load_json(args.input)

    desc_map = {fn["name"]: fn["description"] for fn in functions}

    for item in tests:
        user_prompt = item["prompt"] if isinstance(item, dict) else str(item)
        fn_name = pick_best_function(
            model=model,
            vocab=vocab,
            functions=functions,
            user_prompt=user_prompt,
            max_tokens=args.max_tokens,
        )

        if args.show == "name":
            result = fn_name
        else:
            result = desc_map.get(fn_name, "No matching function")

        print(f"{user_prompt} -> {result}")


if __name__ == "__main__":
    main()
