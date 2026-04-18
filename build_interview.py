#!/usr/bin/env python3
"""Build George + Emma interview about finance_sp500.
- Segments = (speaker, text, chart_to_show_on_right_panel)
- Renders each segment to WAV via Kokoro, concatenates to one MP3
- Emits interview.html with transcript + synced chart swaps
"""
from __future__ import annotations
import subprocess, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT  = ROOT / "html"
AUD  = OUT / "audio"
AUD.mkdir(parents=True, exist_ok=True)

# (speaker, text, chart_src)  — chart persists until a new one is set
INTERVIEW = [
    ("george", "Welcome back. Today we are joined by Emma who is looking at the "
               "S&P 500 across one hundred fifty five years. Emma, what is the story?",
               "sp500_shiller_1871_2026.html"),
    ("emma",   "Thank you George. The story is in the math. From eighteen seventy one "
               "to today, the index grew from under five to seven thousand on a log scale "
               "it looks almost linear, but that hides the real structure.",
               "sp500_shiller_1871_2026.html"),
    ("george", "What structure?",
               None),
    ("emma",   "When you let a piecewise algorithm choose where to break the series, "
               "it picks nineteen forty two and nineteen eighty one. Those are the end "
               "of the gold standard and the Volcker pivot. The algorithm had no idea "
               "about monetary policy. It just followed the data.",
               "sp500_shiller_1871_2026.html"),
    ("george", "So three regimes?",
               None),
    ("emma",   "Three macro regimes, yes. But you can go further. With six segments "
               "the algorithm isolates two thousand ten onwards as its own clean monotone "
               "regime at eleven point two percent per year.",
               "sp500_shiller_1871_2026.html"),
    ("george", "What is special about two thousand ten?",
               None),
    ("emma",   "That is when quantitative easing stopped being an emergency tool and "
               "became structural. Norayr picked this regime start visually a year ago. "
               "He drew a straight line through the two most recent local minima "
               "August twenty eleven and March twenty twenty five.",
               "sp500_minima_line.html"),
    ("george", "And that line predicted seven thousand by twenty twenty six?",
               "sp500_minima_line.html"),
    ("emma",   "Within a few months, yes. The index landed at seven thousand forty one "
               "on April seventeenth. Norayr's two-minima line said six thousand five "
               "hundred for today. So the market is eight percent above his channel.",
               "sp500_minima_line.html"),
    ("george", "Is that a problem?",
               None),
    ("emma",   "It is the signal we need to examine. If price is growing exponentially "
               "log of price is linear in time. If price is growing faster than that "
               "— super-exponentially — then log of log of price is linear. On the post "
               "2010 data, log of log of price is twelve times more linear than on "
               "the full series.",
               "sp500_loglog.html"),
    ("george", "So this is a super-exponential regime.",
               "sp500_loglog.html"),
    ("emma",   "Mathematically, yes. Didier Sornette calls this a log-periodic power "
               "law singularity. He has been publishing on it since nineteen ninety six. "
               "Norayr re-derived the framework empirically without knowing it.",
               "sp500_loglog.html"),
    ("george", "What does Sornette's model say happens next?",
               None),
    ("emma",   "Super-exponential trajectories end in finite time. The critical time "
               "t-sub-c can be estimated from log-periodic oscillations in the price. "
               "The literature lists five warnings — volatility compression then spike, "
               "credit spread widening, margin debt parabolic, breadth narrowing, and "
               "capex concentration. Three of five are live right now.",
               None),
    ("george", "Not financial advice.",
               None),
    ("emma",   "Correct. This is a mathematical study of a price series. Nothing here "
               "is a recommendation. Thank you George.",
               None),
    ("george", "Thank you Emma.",
               None),
]

VOICES = {"george": "bm_george", "emma": "bf_emma"}

print(f"rendering {len(INTERVIEW)} segments…")
wav_files: list[pathlib.Path] = []
for i, (spk, text, _) in enumerate(INTERVIEW):
    wav = AUD / f"iv_{i:03d}_{spk}.wav"
    if not wav.exists():
        subprocess.run(
            ["kokoro", "-m", VOICES[spk], "-l", "b", "-t", text, "-o", str(wav), "-s", "0.95"],
            check=True, capture_output=True,
        )
    wav_files.append(wav)

# Concatenate via ffmpeg concat demuxer
list_path = AUD / "iv_list.txt"
list_path.write_text("".join(f"file '{p}'\n" for p in wav_files))
full_wav = AUD / "interview_full.wav"
mp3 = OUT / "interview.mp3"
subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
     "-codec:a", "pcm_s16le", str(full_wav)],
    check=True, capture_output=True,
)
subprocess.run(
    ["ffmpeg", "-y", "-i", str(full_wav),
     "-codec:a", "libmp3lame", "-b:a", "128k", str(mp3)],
    check=True, capture_output=True,
)

# Probe durations to build the timeline
def duration(p: pathlib.Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_entries", "format=duration", str(p)],
        capture_output=True, text=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])

timeline = []
t = 0.0
for i, ((spk, text, chart), wav) in enumerate(zip(INTERVIEW, wav_files)):
    d = duration(wav)
    timeline.append({"i": i, "speaker": spk, "text": text, "chart": chart,
                     "start": t, "end": t + d})
    t += d

print(f"total duration: {t:.1f}s ({int(t)//60}m {int(t)%60}s)")

list_path.unlink(); full_wav.unlink()

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>finance_sp500 · George + Emma interview</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --bg: #0b0a08; --panel: #14120e; --gold: #d4af37; --gold-dim: #8a7228;
    --gold-bright: #f5d76e; --text: #e8e2cf; --muted: #8a846f;
    --george: #6b9fff; --emma: #ff86bf;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ height: 100%; background: var(--bg); color: var(--text);
    font-family: -apple-system, "SF Pro Display", sans-serif; overflow: hidden; }}
  header {{ padding: 1vh 2vw; border-bottom: 1px solid var(--gold-dim);
    display: flex; justify-content: space-between; align-items: baseline; }}
  header h1 {{ color: var(--gold); font-size: 2.4vh; font-weight: 500; letter-spacing: 2px; }}
  header .meta {{ color: var(--muted); font-size: 1.4vh; }}
  main {{ display: grid; grid-template-columns: 38vw 1fr; height: calc(100vh - 4vh - 10vh); gap: 1vw; padding: 1vh 1vw; }}
  #transcript {{ overflow-y: auto; padding: 1vh 1vw; background: #0d0b07;
    border: 1px solid var(--gold-dim); border-radius: 8px; }}
  .seg {{ padding: 0.9vh 0.8vw; margin-bottom: 0.4vh; border-radius: 6px;
    font-size: 1.7vh; line-height: 1.5; opacity: 0.45; transition: all 0.2s; }}
  .seg.active {{ opacity: 1; background: rgba(255, 170, 60, 0.08); border-left: 2px solid var(--gold-bright); }}
  .seg .who {{ font-weight: 700; letter-spacing: 2px; font-size: 1.3vh; margin-right: 0.5vw; }}
  .seg.george .who {{ color: var(--george); }}
  .seg.emma   .who {{ color: var(--emma); }}
  #chart-host {{ border: 1px solid var(--gold-dim); border-radius: 8px; overflow: hidden; background: #000;
    box-shadow: 0 0 30px rgba(255, 170, 60, 0.1); }}
  #chart-host iframe {{ width: 100%; height: 100%; border: none; }}
  footer {{ position: fixed; bottom: 0; left: 0; right: 0; height: 10vh;
    background: linear-gradient(180deg, transparent, rgba(0,0,0,0.9) 40%);
    display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  audio {{ width: 92vw; height: 5vh; filter: invert(1) hue-rotate(180deg); }}
  .crest {{ color: var(--muted); font-size: 1.1vh; letter-spacing: 2px; margin-top: 0.4vh; }}
  .label-row {{ display: flex; gap: 2vw; font-size: 1.4vh; margin-top: 0.3vh; }}
  .label-row b {{ letter-spacing: 1px; }}
</style>
</head>
<body>

<header>
  <h1>finance_sp500 · interview with George &amp; Emma</h1>
  <div class="meta">⬡⟐ HARI · 91ae0c77 · auto-advancing transcript + charts</div>
</header>

<main>
  <div id="transcript">
'''
for seg in timeline:
    cls = seg["speaker"]
    who = "GEORGE" if cls == "george" else "EMMA"
    html += f'<div class="seg {cls}" data-start="{seg["start"]:.2f}" data-end="{seg["end"]:.2f}" data-chart="{seg["chart"] or ""}"><span class="who">{who}</span>{seg["text"]}</div>\n'

html += f'''
  </div>
  <div id="chart-host"><iframe id="chart-frame" src=""></iframe></div>
</main>

<footer>
  <audio id="aud" controls src="interview.mp3"></audio>
  <div class="label-row"><b style="color:var(--george)">◆ GEORGE</b> <b style="color:var(--emma)">◆ EMMA</b></div>
  <div class="crest">⬡⟐ HARI · 91ae0c77 · finance_sp500</div>
</footer>

<script>
  const segs = Array.from(document.querySelectorAll(".seg"));
  const frame = document.getElementById("chart-frame");
  const aud = document.getElementById("aud");
  let currentChart = "";
  function onTick() {{
    const t = aud.currentTime;
    let active = -1;
    for (let i = 0; i < segs.length; i++) {{
      const s = +segs[i].dataset.start, e = +segs[i].dataset.end;
      if (t >= s && t < e) {{ active = i; break; }}
    }}
    segs.forEach((s, i) => s.classList.toggle("active", i === active));
    if (active >= 0) {{
      segs[active].scrollIntoView({{ block: "center", behavior: "smooth" }});
      const chart = segs[active].dataset.chart;
      if (chart && chart !== currentChart) {{
        frame.src = chart;
        currentChart = chart;
      }}
    }}
  }}
  aud.addEventListener("timeupdate", onTick);
  aud.addEventListener("loadedmetadata", () => {{ frame.src = segs[0].dataset.chart || "sp500_shiller_1871_2026.html"; currentChart = frame.src; }});
  // Click a segment to seek
  segs.forEach(s => s.addEventListener("click", () => {{ aud.currentTime = +s.dataset.start + 0.05; aud.play(); }}));
</script>
</body>
</html>
'''

(OUT / "interview.html").write_text(html)
print(f"wrote {OUT / 'interview.html'}")
print(f"wrote {mp3}")
