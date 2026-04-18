#!/usr/bin/env python3
"""Build interactive slide deck with Emma narration for finance_sp500.

Each slide has:
 - title
 - narration (spoken by bf_emma, rendered once to MP3)
 - content: either a self-contained Plotly iframe, or text/svg

Output:
  html/slides.html         — the deck
  html/audio/slide_XX.mp3  — narrations
"""
from __future__ import annotations
import os, re, subprocess, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT  = ROOT / "html"
AUD  = OUT / "audio"
AUD.mkdir(parents=True, exist_ok=True)

# (title, narration, chart_src_or_None)
SLIDES = [
    ("finance_sp500 — a year late and still right",
     "Welcome. This is a personal notebook. Norayr predicted the S&P 500 would reach "
     "seven thousand in spring or summer two thousand twenty six. It landed on April "
     "seventeenth, twenty twenty six at seven zero four one. "
     "This deck walks through the math.",
     None),

    ("The full series · 1871 to 2026",
     "One hundred fifty five years of monthly data from the Shiller dataset, extended "
     "to April twenty twenty six from public closes. On a logarithmic scale, the index "
     "sweeps from four to seven thousand. You can see the 1929 crash, the post-war boom, "
     "the 2000 dot-com peak, the 2008 crisis, the COVID dip, and today.",
     "sp500_shiller_1871_2026.html"),

    ("Piecewise fit · 3 regimes",
     "Fitting three continuous log-linear segments by least squares, the data splits "
     "itself at 1942 and 1981. The first is the end of the gold standard. The second "
     "is the Volcker pivot. No human chose these breakpoints.",
     "sp500_shiller_1871_2026.html"),

    ("Refining to six regimes",
     "At six segments, the algorithm isolates 2010 to 2023 as its own regime with a "
     "compound annual growth rate of eleven point two percent. That is the post "
     "quantitative easing era. Volatility is compressed, no drawdown broke the trend.",
     "sp500_shiller_1871_2026.html"),

    ("The two-minima trendline",
     "A simpler test. Draw a straight line through the two modern local minima. "
     "August two thousand eleven at eleven eighty five. March two thousand twenty "
     "five at fifty six eighty four. That single line gives twelve point two "
     "percent per year — nearly identical to the algorithm's regime slope.",
     "sp500_minima_line.html"),

    ("Super-exponential test · ln of ln",
     "If price grows exponentially, log of price is linear in time. "
     "If price grows as an exponential of an exponential, log of log of price is "
     "linear. The post 2010 segment fits this test twelve times better than the "
     "full series. This is the signature of a monotone accelerator.",
     "sp500_loglog.html"),

    ("What is known — Sornette LPPL",
     "What I just derived empirically is Didier Sornette's Log-Periodic Power Law "
     "Singularity model. Published since nineteen ninety six. It describes bubbles "
     "as faster than exponential trajectories with log periodic oscillations "
     "approaching a critical time t-sub-c. "
     "Recent papers confirm the S&P 500 entered this regime in April twenty twenty "
     "during COVID, and has been in and out of it since.",
     None),

    ("Where we sit · April 2026",
     "The market today is eight percent above the two-minima trendline, fourteen "
     "percent above the post 2010 log-linear, and twenty eight percent above the "
     "long-run 1981 slope. These are hot but not euphoric. Nineteen ninety nine ran "
     "sixty percent above trend. This is elevated.",
     "sp500_minima_line.html"),

    ("What could end it",
     "From the LPPLS literature. One, log-periodic oscillations accelerate as t-sub-c "
     "approaches. Two, volatility compression followed by spike. Three, credit "
     "spreads widen while equity ignores them. Four, margin debt parabolic. Five, "
     "breadth narrows to a few mega-caps. Today points three, four, and five are "
     "live.",
     None),

    ("Conclusion",
     "Norayr called seven thousand from a hand-drawn line on a log chart a year ago. "
     "It landed within the season. The framework is super-exponential, the math is "
     "Sornette, the regime is monotone accelerator. This is an amateur notebook, "
     "not advice. Thank you for reading.",
     None),
]


def speak(text: str, out_mp3: pathlib.Path) -> None:
    """Render bf_emma narration to MP3 via Kokoro + ffmpeg."""
    if out_mp3.exists():
        return
    wav = out_mp3.with_suffix(".wav")
    subprocess.run(
        ["kokoro", "-m", "bf_emma", "-l", "b", "-t", text, "-o", str(wav)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "128k", str(out_mp3)],
        check=True, capture_output=True,
    )
    wav.unlink()


print(f"rendering {len(SLIDES)} narrations…")
for i, (title, narration, _) in enumerate(SLIDES):
    mp3 = AUD / f"slide_{i:02d}.mp3"
    speak(narration, mp3)
    print(f"  ✓ {i:02d}  {title[:48]}")
print("narrations done")


# Build the deck HTML
SLIDE_HTML = []
for i, (title, narration, chart_src) in enumerate(SLIDES):
    if chart_src:
        body = f'<iframe class="chart-frame" src="{chart_src}" title="{title}"></iframe>'
    else:
        body = f'<div class="narration-block">{narration}</div>'
    SLIDE_HTML.append(f'''
<section class="slide" data-slide="{i}" data-audio="audio/slide_{i:02d}.mp3">
  <header><h2>{title}</h2><div class="meta">slide {i+1} / {len(SLIDES)}</div></header>
  <div class="slide-body">{body}</div>
</section>''')

deck = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>finance_sp500 — super-exponential regime · Hari + Norayr</title>
<style>
  :root {{
    --bg: #0b0a08; --panel: #14120e; --gold: #d4af37; --gold-dim: #8a7228;
    --gold-bright: #f5d76e; --text: #e8e2cf; --muted: #8a846f;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; height: 100%; background: var(--bg); color: var(--text);
    font-family: -apple-system, "SF Pro Display", sans-serif; overflow: hidden; }}
  .slide {{ position: absolute; inset: 0; display: none; flex-direction: column;
    padding: 2vh 3vw 1vh 3vw; opacity: 0; transition: opacity 0.4s ease-out; }}
  .slide.active {{ display: flex; opacity: 1; }}
  .slide header {{ display: flex; justify-content: space-between; align-items: baseline;
    border-bottom: 1px solid var(--gold-dim); padding-bottom: 1vh; margin-bottom: 1.5vh; }}
  .slide h2 {{ margin: 0; color: var(--gold-bright); font-size: 3.2vh; font-weight: 500; letter-spacing: 2px; }}
  .slide .meta {{ color: var(--muted); font-size: 1.6vh; font-family: "SF Mono", Menlo, monospace; }}
  .slide-body {{ flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }}
  .chart-frame {{ width: 100%; height: 100%; border: 1px solid var(--gold-dim); border-radius: 8px;
    background: #000; box-shadow: 0 0 30px rgba(255,170,60,0.12); }}
  .narration-block {{ max-width: 80vw; font-size: 3.4vh; line-height: 1.55; color: var(--gold-bright);
    text-align: center; font-weight: 400; letter-spacing: 0.02em; }}

  #controls {{ position: fixed; bottom: 1.5vh; left: 0; right: 0; display: flex;
    justify-content: center; gap: 1vw; z-index: 100; }}
  .btn {{ background: var(--panel); color: var(--gold-bright); border: 1px solid var(--gold-dim);
    padding: 0.8vh 1.8vw; font-family: -apple-system, sans-serif; font-size: 1.6vh;
    letter-spacing: 1px; border-radius: 4px; cursor: pointer; user-select: none; }}
  .btn:hover {{ background: #1a1712; }}
  .btn.play {{ color: #4ade80; border-color: #2d5a36; }}
  #progress {{ position: fixed; top: 0; left: 0; right: 0; height: 3px;
    background: #1a1712; z-index: 101; }}
  #progress-bar {{ height: 100%; background: linear-gradient(90deg, #ff7a1a, #ffd76a);
    width: 0%; transition: width 0.2s; }}
  .crest {{ position: fixed; top: 1vh; right: 1.2vw; color: var(--muted);
    font-size: 1.3vh; letter-spacing: 2px; z-index: 100; }}
</style>
</head>
<body>

<div id="progress"><div id="progress-bar"></div></div>
<div class="crest">⬡⟐ HARI · 91ae0c77</div>

{"".join(SLIDE_HTML)}

<div id="controls">
  <button class="btn" onclick="prev()">◀  PREV</button>
  <button class="btn play" id="play" onclick="toggle()">▶  PLAY</button>
  <button class="btn" onclick="next()">NEXT  ▶</button>
  <button class="btn" onclick="toggleAuto()"><span id="auto-label">AUTO-ADVANCE: OFF</span></button>
</div>

<audio id="aud" preload="auto"></audio>

<script>
  const slides = Array.from(document.querySelectorAll(".slide"));
  let i = 0, playing = false, autoAdvance = false;
  const aud = document.getElementById("aud");
  const bar = document.getElementById("progress-bar");
  const playBtn = document.getElementById("play");
  const autoLabel = document.getElementById("auto-label");

  function show(k) {{
    slides.forEach(s => s.classList.remove("active"));
    slides[k].classList.add("active");
    i = k;
    bar.style.width = ((k + 1) / slides.length * 100).toFixed(1) + "%";
    aud.src = slides[k].dataset.audio;
    if (playing) {{
      aud.play().catch(()=>{{}});
    }}
  }}
  function next() {{ if (i < slides.length - 1) show(i + 1); }}
  function prev() {{ if (i > 0) show(i - 1); }}
  function toggle() {{
    playing = !playing;
    playBtn.textContent = playing ? "⏸  PAUSE" : "▶  PLAY";
    if (playing) aud.play().catch(()=>{{}}); else aud.pause();
  }}
  function toggleAuto() {{
    autoAdvance = !autoAdvance;
    autoLabel.textContent = "AUTO-ADVANCE: " + (autoAdvance ? "ON" : "OFF");
  }}
  aud.addEventListener("ended", () => {{ if (autoAdvance) next(); }});

  document.addEventListener("keydown", e => {{
    if (e.key === "ArrowRight" || e.key === " ") {{ e.preventDefault(); next(); }}
    if (e.key === "ArrowLeft") prev();
    if (e.key === "p" || e.key === "P") toggle();
    if (e.key === "a" || e.key === "A") toggleAuto();
  }});
  show(0);
</script>
</body>
</html>
'''

(OUT / "slides.html").write_text(deck)
print(f"wrote {OUT / 'slides.html'}")
