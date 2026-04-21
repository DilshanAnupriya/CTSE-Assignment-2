"""
Diagnose: Does the ACTUAL format_places_summary output cause a timeout?
"""
import sys, os, requests, time, json, re
sys.path.insert(0, os.path.abspath("src"))

from tools.travel_tool import format_places_summary

destination = "Kandy"
summary = format_places_summary(destination)
print(f"Summary length: {len(summary)} chars")
print(f"First 500 chars:\n{summary[:500]}\n{'='*60}")
print(f"Truncated to 2000: {len(summary[:2000])} chars")

payload = {
    "model": "qwen2.5",
    "prompt": (
        f'You are a travel quality evaluator. Rate this travel research report\n'
        f'for "{destination}" on a scale of 1 to 10.\n\n'
        f'Criteria:\n'
        f'- Relevance: Does it mention real, known attractions in {destination}?\n'
        f'- Completeness: Does it cover places, ratings, and activities?\n'
        f'- Clarity: Is it well-structured and readable?\n\n'
        f'Report to evaluate:\n---\n{summary[:2000]}\n---\n\n'
        f'Respond ONLY in JSON format like this:\n'
        f'{{"score": <number 1-10>, "reason": "<one sentence>"}}'
    ),
    "stream": False,
}

print(f"Total prompt length: {len(payload['prompt'])} chars")
print("Sending to Ollama (timeout=180s)...")
start = time.time()
try:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=180,
    )
    elapsed = time.time() - start
    print(f"Status: {r.status_code}, Time: {elapsed:.1f}s")
    raw = r.json().get("response", "{}")
    print(f"Raw: {raw[:400]}")
    match = re.search(r'\{[^}]+\}', raw)
    if match:
        parsed = json.loads(match.group())
        print(f"Score: {parsed.get('score')}, Reason: {parsed.get('reason')}")
    else:
        print("WARNING: Could not parse JSON from response!")
except requests.exceptions.Timeout as e:
    elapsed = time.time() - start
    print(f"TIMEOUT after {elapsed:.1f}s — this is why tests skip!")
except Exception as e:
    elapsed = time.time() - start
    print(f"ERROR after {elapsed:.1f}s: {type(e).__name__}: {e}")
