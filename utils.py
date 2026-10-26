"""Audio preparation for the simple two-condition TRIBE notebook."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


def prepare_audio(stimuli, folder):
    """Cache English speech and align the supplied words; return one item per row."""
    from gtts import gTTS

    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    items = []
    for text in stimuli.stimulus:
        key = hashlib.sha256(text.encode()).hexdigest()[:20]
        audio = folder / f"{key}.mp3"
        if not audio.exists():
            gTTS(text, lang="en").save(str(audio))
        items.append({"text": text, "audio": str(audio),
                      "alignment": str(folder / f"{key}.json")})

    manifest = folder / "manifest.json"
    manifest.write_text(json.dumps(items, indent=2))
    if any(not Path(item["alignment"]).exists() for item in items):
        script = Path(__file__).resolve().parent.parent / "align_localizer.py"
        env = dict(os.environ)
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
        subprocess.run(["uvx", "--from", "whisperx", "python", str(script),
                        str(manifest)], check=True, env=env)
    return items


def stimulus_events(item, window, onset=16.0):
    """Put one clip in its own model window, with rest before and after it.

    Returns (events, onset, duration). Word times come from forced alignment;
    each word's context contains only the stimulus prefix through that word.
    """
    from neuralset.events.utils import standardize_events

    alignment = json.loads(Path(item["alignment"]).read_text())
    duration = float(alignment["duration"])
    words = item["text"].split()
    if [w["word"].casefold() for w in alignment["words"]] != [w.casefold() for w in words]:
        raise ValueError("Alignment does not match the supplied text.")
    if not 0 < duration <= window - onset - 16:
        raise ValueError("Stimulus must fit in one model window with 16 seconds of trailing rest.")

    rows = [
        {"type": "Event", "start": 0, "duration": window},
        {"type": "Audio", "start": onset, "duration": duration, "filepath": item["audio"]},
    ]
    for i, word in enumerate(alignment["words"]):
        rows.append({"type": "Word", "start": onset + word["start"],
                     "duration": word["end"] - word["start"], "text": words[i],
                     "context": " ".join(words[:i + 1])})
    events = pd.DataFrame(rows).assign(timeline="stimulus", subject="default", study="localizer")
    return standardize_events(events), onset, duration
