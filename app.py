import uvicorn
import argparse
from fastapi import FastAPI
from pydantic import BaseModel
from mlx_lm import load, generate
import json
import time
import sys

# Argument parsing for CLI options
parser = argparse.ArgumentParser(description="serveMLX: Ultra-light MLX API")
parser.add_argument("--model", type=str,
                    default="mlx-community/Mistral-Small-24B-Instruct-2501-4bit",
                    help="MLX model name or path")
parser.add_argument("--logfile", type=str, default=None,
                    help="File for logging JSONL; no default logging if omitted")
parser.add_argument("--log-stdout", action="store_true",
                    help="Enable logging to stdout (disabled by default)")
parser.add_argument("--host", type=str, default="127.0.0.1",
                    help="Host IP for serving")
parser.add_argument("--port", type=int, default=8000,
                    help="Host port for serving")
args = parser.parse_args()

# Load model globally at startup using given CLI argument
model_name = args.model
model, tokenizer = load(model_name)

# Setup logging (defaults to no logging)
log_file = None
if args.logfile:
    log_file = open(args.logfile, 'a', encoding='utf-8')
elif args.log_stdout:
    log_file = sys.stdout
# else: if neither is specified, log_file remains None (no logging)

# Define FastAPI app
app = FastAPI(title="serveMLX: Ultra-light MLX API")

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: list[Message]
    max_tokens: int = 256

@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest):
    start_time = time.time()
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    prompt_tokens_list = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )
    if not (isinstance(prompt_tokens_list, list) and all(isinstance(i, int) for i in prompt_tokens_list)):
        raise TypeError(f"Unexpected prompt format: {type(prompt_tokens_list)}")
    prompt_tokens_count = len(prompt_tokens_list)
    prompt_str = tokenizer.decode(prompt_tokens_list)

    response_text = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt_str,
        max_tokens=request.max_tokens,
        verbose=False
    )

    completion_tokens_list = tokenizer.encode(response_text)
    completion_tokens_count = len(completion_tokens_list)
    generation_time = time.time() - start_time
    tokens_per_second = completion_tokens_count / generation_time if generation_time > 0 else 0

    response = {
        "id": f"mlx-request-{int(time.time()*1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens_count,
            "completion_tokens": completion_tokens_count,
            "total_tokens": prompt_tokens_count + completion_tokens_count
        }
    }

    if log_file:
        log_line = json.dumps({
            "request": request.dict(),
            "response": response,
            "generation_time": generation_time,
            "tokens_per_second": round(tokens_per_second, 2)
        })
        print(log_line, flush=True, file=log_file)

    return response

# Run server (CLI-specified or default settings)
if __name__ == "__main__":
    uvicorn.run("app:app", host=args.host, port=args.port, reload=True)
