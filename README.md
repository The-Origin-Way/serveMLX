# serveMLX: Lightweight simple MLX service

A lightweight, efficient chat API server built with **FastAPI** and powered by the high-performance [mlx-community](https://github.com/ml-explore/mlx-examples) language models. This project allows you to quickly spin up an HTTP interface for chat-based completion tasks with MLX models on Apple silicon systems. 

---

## Background 

The current-generation Mac Mini is an incredibly efficient desktop. They have very low idle power draw, and are excellent and responsive for most interactive tasks. Even with standard compute duties within one of our clinics there are plenty of cycles to spare for background work like LLM completion requests.

A Mac Mini M4 Pro with >=32GB of memory can run pretty high quality models like Mistral Small (2501 @ 4bit) at roughly 18 tokens / second with a power draw of ~60 watts measured at the wall. This is an incredibly efficient and compelling solution to many of the LLM completion needs for our internal AI products where these kinds of token generation speeds are sufficient.

Do not expose this service to the internet or untrusted networks. Any sensitive information and certainly any PHI must only be transmitted over an encrypted connection, and not stored in any logs. Please ensure you understand the security and privacy requirements of anything you deploy.

---

## Quickstart Guide

### Installation

Clone this repository and navigate to the project directory:

```bash
git clone https://github.com/The-Origin-Way/serveMLX
cd serveMLX
```

Create a virtual environment and activate it (recommended):

```bash
python -m venv venv
source venv/bin/activate 
```

Install dependencies from the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

If you wish to make the service start on boot, use the example plist file and install it like this:

```bash
sudo chown root:wheel /Library/LaunchDaemons/com.servemlx.api.plist
sudo chmod 644 /Library/LaunchDaemons/com.servemlx.api.plist
sudo launchctl load -w /Library/LaunchDaemons/com.servemlx.api.plist
```

### Running the Server

Run the API server with default parameters:

```bash
python app.py
```

Alternatively, specify custom parameters via CLI arguments:

```bash
python app.py --model mlx-community/Mistral-Small-24B-Instruct-2501-4bit --host 127.0.0.1 --port 8080 --logfile logs.jsonl
```

| Argument           | Default value                                       | Description                               |
|--------------------|-----------------------------------------------------|-------------------------------------------|
| `--model`          | `mlx-community/Mistral-Small-24B-Instruct-2501-4bit`| MLX model name or path                    |
| `--host`           | `0.0.0.0`                                           | IP address or hostname to bind the server |
| `--port`           | `8000`                                              | Port for the server                       |
| `--logfile`        | logging disabled                                    | JSONL logfile (optional)                  |
| `--log-stdout`     | logging disabled                                    | Console logging (optional)                |

---

## Usage Example

Once your server is running, you can POST requests to the `/v1/chat/completions` endpoint.

**Example Request (`curl`)**:
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{
           "messages": [
              {"role": "user", "content": "how much wood could a wood chuck chuck if a wood chuck could chuck wood"}
           ],
           "max_tokens": 200
         }'
```

**Example Response**:

```json
{
    "request": {
        "messages": [
            {
                "role": "user",
                "content": "how much wood could a wood chuck chuck if a wood chuck could chuck wood"
            }
        ],
        "max_tokens": 200
    },
    "response": {
        "id": "mlx-request-1744231225614",
        "object": "chat.completion",
        "created": 1744231225,
        "model": "mlx-community/Mistral-Small-24B-Instruct-2501-4bit",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "The phrase \"How much wood could a woodchuck chuck if a woodchuck could chuck wood?\" is a classic tongue twister and not a question with a literal answer, as woodchucks (also known as groundhogs) do not actually chuck (throw) wood. However, for fun, a New York fish and wildlife researcher, Richard Thomas, calculated a whimsical answer.\n\nAccording to Thomas's calculations, if a woodchuck could chuck wood, it could chuck approximately 700 pounds of it! This number is based on the volume of dirt a woodchuck can dig, which is then converted into an equivalent volume of wood. Again, it's important to note that this is a humorous and hypothetical calculation, not a real behavior of woodchucks."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 22,
            "completion_tokens": 165,
            "total_tokens": 187
        }
    },
    "generation_time": 9.167434930801392,
    "tokens_per_second": 18
}
```

---


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
