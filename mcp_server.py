"""
AI Influencer Generator MCP Server for Hermes
Create virtual AI influencers using Stable Diffusion + gTTS + SadTalker.
"""
import json, os, subprocess, sys

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_generate_influencer_image(args):
    prompt = args.get("prompt")
    if not prompt:
        return {"error": "prompt is required"}
    model = args.get("model", "stable-diffusion-xl")
    steps = args.get("steps", 30)
    seed = args.get("seed", -1)
    cmd = ["python", os.path.join(TOOL_DIR, "generate_image.py"), "--prompt", prompt, "--model", model, "--steps", str(steps), "--seed", str(seed)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=TOOL_DIR)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

def handle_generate_speech(args):
    text = args.get("text")
    if not text:
        return {"error": "text is required"}
    language = args.get("language", "en")
    cmd = ["python", os.path.join(TOOL_DIR, "generate_speech.py"), "--text", text, "--lang", language]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=TOOL_DIR)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

def handle_create_lipsync_video(args):
    image_path = args.get("image_path")
    audio_path = args.get("audio_path")
    if not image_path or not audio_path:
        return {"error": "image_path and audio_path are required"}
    cmd = ["python", os.path.join(TOOL_DIR, "lipsync.py"), "--image", image_path, "--audio", audio_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=TOOL_DIR)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

def handle_run_full_pipeline(args):
    prompt = args.get("prompt")
    text = args.get("text")
    if not prompt or not text:
        return {"error": "prompt and text are required"}
    language = args.get("language", "en")
    cmd = ["python", os.path.join(TOOL_DIR, "full_pipeline.py"), "--prompt", prompt, "--text", text, "--lang", language]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=TOOL_DIR)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}

TOOLS = {
    "generate_influencer_image": {
        "description": "Generate an AI influencer portrait image using Stable Diffusion.",
        "parameters": {
            "prompt": {"type": "string", "description": "Image generation prompt"},
            "model": {"type": "string", "description": "Stable Diffusion model variant"},
            "steps": {"type": "integer", "description": "Number of diffusion steps"},
            "seed": {"type": "integer", "description": "Random seed (-1 for random)"}
        },
        "handler": handle_generate_influencer_image
    },
    "generate_speech": {
        "description": "Generate speech audio from text using gTTS.",
        "parameters": {
            "text": {"type": "string", "description": "Text to convert to speech"},
            "language": {"type": "string", "description": "Language code (en, es, fr, etc.)"}
        },
        "handler": handle_generate_speech
    },
    "create_lipsync_video": {
        "description": "Create a lip-synced talking head video from an image and audio using SadTalker.",
        "parameters": {
            "image_path": {"type": "string", "description": "Path to the face image"},
            "audio_path": {"type": "string", "description": "Path to the audio file"}
        },
        "handler": handle_create_lipsync_video
    },
    "run_full_pipeline": {
        "description": "Run the full AI influencer pipeline: generate image, speech, and lip-sync video.",
        "parameters": {
            "prompt": {"type": "string", "description": "Image generation prompt"},
            "text": {"type": "string", "description": "Speech text"},
            "language": {"type": "string", "description": "Language code"}
        },
        "handler": handle_run_full_pipeline
    }
}

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            method = req.get("method")
            if method == "tools/list":
                tools_list = []
                for name, t in TOOLS.items():
                    tools_list.append({"name": name, "description": t["description"], "inputSchema": {"type": "object", "properties": t["parameters"]}})
                print(json.dumps({"result": tools_list}), flush=True)
            elif method == "tools/call":
                tool_name = req.get("params", {}).get("name")
                arguments = req.get("params", {}).get("arguments", {})
                if tool_name in TOOLS:
                    result = TOOLS[tool_name]["handler"](arguments)
                    print(json.dumps({"result": result}), flush=True)
                else:
                    print(json.dumps({"error": f"Unknown tool: {tool_name}"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    main()
