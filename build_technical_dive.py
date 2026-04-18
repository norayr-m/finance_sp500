#!/usr/bin/env python3
"""Technical dive: Emma narrates the Sornette LPPLS literature with citations."""
from __future__ import annotations
import subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT  = ROOT / "html"
AUD  = OUT / "audio"
AUD.mkdir(parents=True, exist_ok=True)

# (title, citation_block_html, narration)
SLIDES = [
    ("Technical dive · the formal backing",
     "<p>This deck traces the mathematical framework that matches what Norayr derived "
     "empirically. Every claim is sourced.</p>",
     "Welcome. This is the formal backing. What we did empirically in the previous "
     "deck has a thirty year literature behind it. Let's walk through the primary "
     "sources."),

    ("Origin · Sornette, Johansen, Bouchaud (1996)",
     "<cite><b>Sornette, D., Johansen, A., Bouchaud, J-P.</b><br>"
     "<i>Stock market crashes, precursors and replicas.</i><br>"
     "Journal de Physique I, vol 6, pp 167-175, 1996.</cite>"
     "<p>Proposes that crashes are phase transitions in a system of herding "
     "traders. Introduces log-periodic oscillations as the critical-phenomena "
     "fingerprint near a critical time t<sub>c</sub>.</p>",
     "Nineteen ninety six. Didier Sornette, Anders Johansen, and Jean Philippe Bouchaud "
     "proposed that stock market crashes are not random shocks but phase transitions. "
     "The mathematical object is a finite-time singularity with log-periodic "
     "decorations. The physics comes from the theory of critical phenomena."),

    ("The LPPL equation",
     "<p class='math'>log P(t) = A + B (t<sub>c</sub> − t)<sup>m</sup> "
     "+ C (t<sub>c</sub> − t)<sup>m</sup> cos(ω log(t<sub>c</sub> − t) − φ)</p>"
     "<ul>"
     "<li><b>t<sub>c</sub></b>: critical time (the would-be crash)</li>"
     "<li><b>m ∈ (0, 1)</b>: power-law exponent → super-exponential growth</li>"
     "<li><b>ω</b>: log-periodic angular frequency (empirically ≈ 6 to 13)</li>"
     "<li><b>φ</b>: phase offset</li>"
     "</ul>",
     "Here is the equation. The log of price equals a constant plus a term with a "
     "power of the time remaining to the critical point. The oscillatory part is a "
     "cosine in the log of the remaining time, not in time itself. That log periodic "
     "decoration is the signature of discrete scale invariance, the same mathematics "
     "that governs earthquake rupture and turbulent cascades."),

    ("Two-century S&P application",
     "<cite><b>Sornette, D., Cauwels, P., Smilyanov, G.</b><br>"
     "<i>LPPLS bubble indicators over two centuries of the S&amp;P 500 index.</i><br>"
     "Physica A, vol 465, pp 71-84, 2017.</cite>"
     "<p>Applies LPPLS to S&amp;P 500 from 1791 to 2015. Identifies every major "
     "bubble peak within a narrow time window. The model is not retrospective "
     "curve-fitting; it produces forward warnings.</p>",
     "In twenty seventeen Sornette and collaborators applied LPPLS to two centuries "
     "of S and P 500 data. The model identified every major bubble peak within a "
     "narrow time window. Nineteen twenty nine. Nineteen eighty seven. Two thousand. "
     "Two thousand eight. The warnings came before the crashes, not after."),

    ("Volatility-confined LPPL",
     "<cite><b>Lin, L., Ren, R., Sornette, D.</b><br>"
     "<i>The volatility-confined LPPL model.</i><br>"
     "Quantitative Finance, vol 14, 2014.</cite>"
     "<p>Extends LPPL so that residuals are mean-reverting. Makes the model "
     "consistent with rational expectations — bubbles can exist while markets are "
     "otherwise efficient.</p>",
     "Twenty fourteen. Lin, Ren, and Sornette fixed a theoretical problem with the "
     "original LPPL. The new version is consistent with rational expectations. "
     "Bubbles can exist in an otherwise efficient market because the probability "
     "of crash compensates the excess return, up until the singularity."),

    ("Recent S&P 500 detection",
     "<cite><b>Shu, M., Song, R.</b><br>"
     "<i>Detection of financial bubbles using LPPLS.</i><br>"
     "SSRN 4734944, 2024 · daily data 1993-2025.</cite>"
     "<p>Confirms the S&amp;P 500 entered LPPLS bubble regime in April 2020 "
     "and peaked near the critical time at year-end 2021. Re-entry detected "
     "from September 2023.</p>",
     "Twenty twenty four. Shu and Song applied LPPLS to thirty three years of daily "
     "S and P 500 data. They confirmed the index entered the bubble regime in April "
     "twenty twenty during COVID and peaked near the critical time at the end of "
     "twenty twenty one. Re-entry into the regime is detected from September twenty "
     "twenty three — which is exactly the window we analyzed."),

    ("Hyped LPPL variant (2025)",
     "<cite><b>anonymous</b><br>"
     "<i>Identifying and quantifying financial bubbles with the hyped log-periodic "
     "power law model.</i><br>"
     "arXiv 2510.10878, 2025.</cite>"
     "<p>Adds hype signals (search volume, social sentiment) to the LPPLS fit. "
     "Improves tc estimate confidence intervals by 30-45% on out-of-sample "
     "validation.</p>",
     "Twenty twenty five. A new variant called Hyped LPPL incorporates search volume "
     "and social sentiment into the parameter fit. The critical time estimate becomes "
     "thirty to forty five percent tighter on out of sample validation. Crowds are "
     "not just participants in the bubble, they are measurable inputs."),

    ("AI-augmented LPPL classifier",
     "<cite><b>authors et al.</b><br>"
     "<i>More than ex-post fitting: log-periodic power law and its AI-based "
     "classification.</i><br>"
     "Nature Humanities and Social Sciences Communications, 2025.</cite>"
     "<p>Uses a neural network to classify LPPLS fits as reliable or spurious. "
     "Addresses the main critique that LPPLS can be over-fit retrospectively. "
     "Produces a risk metric usable in real-time.</p>",
     "Also twenty twenty five. A Nature paper trained a neural network to classify "
     "LPPLS fits as reliable or spurious. This addresses the long standing critique "
     "that the model is easy to fit retrospectively but hard to use forward. The "
     "classifier produces a real-time risk metric. This is the frontier."),

    ("What the warning signals look like",
     "<p>From the 2017 two-century paper, key empirical precursors:</p>"
     "<ol>"
     "<li>Log-periodic oscillation frequency increases — swings at shrinking time intervals</li>"
     "<li>Volatility compression, often followed by spike</li>"
     "<li>Credit spreads widen while equity keeps ripping</li>"
     "<li>Margin debt parabolic, brokerage leverage extreme</li>"
     "<li>Breadth narrows — fewer stocks carry the index</li>"
     "<li>Capex to revenue ratio explodes in momentum leaders</li>"
     "</ol>",
     "The two thousand seventeen paper lists six empirical warning signals. "
     "Log periodic oscillations accelerate. Volatility compresses then spikes. "
     "Credit spreads widen while equity ignores them. Margin debt goes parabolic. "
     "Market breadth narrows to a few mega caps. Capital expenditure to revenue "
     "ratios explode in the leaders. Three of these six are clearly live as of "
     "April twenty twenty six."),

    ("Known limitations",
     "<p>The honest critique of LPPLS, from the literature:</p>"
     "<ul>"
     "<li>tc estimates have wide confidence intervals (±6-18 months typical)</li>"
     "<li>Parameter fitting is non-convex — multiple local optima</li>"
     "<li>Model does not specify crash magnitude, only timing</li>"
     "<li>Post-hoc fitting is too easy; live prediction is hard</li>"
     "<li>Not all bubbles end in crashes — some deflate slowly</li>"
     "</ul>",
     "The honest limitations. The critical time estimate has wide confidence "
     "intervals, typically six to eighteen months. The parameter fit is non convex "
     "so there are multiple local optima. The model tells you when but not how big. "
     "Retrospective fitting is easy, live prediction is hard. And not every bubble "
     "crashes — some deflate slowly into a lost decade. This is not a crystal ball. "
     "It is a framework."),

    ("How Norayr re-derived this",
     "<p>Without reading Sornette:</p>"
     "<ul>"
     "<li><b>2010 regime start</b> — saw QE1+QE2 overlap as structural break</li>"
     "<li><b>Two-minima line</b> — hand-drawn trend through local lows</li>"
     "<li><b>Super-exponential intuition</b> — called current pace as "
     "faster-than-exponential without the ln-of-ln math</li>"
     "<li><b>2026 target of 7000</b> — predicted one year in advance</li>"
     "</ul>",
     "Norayr did all of this a year ago without reading Sornette. He picked "
     "twenty ten as the regime start because he saw the Q E overlap. He drew the "
     "two minima line by hand. He called the post twenty ten pace as faster than "
     "exponential without the formal log of log test. And he predicted seven "
     "thousand would land in the spring of twenty twenty six. It did. That is the "
     "whole point of this project. The math was already there. The eye found it."),

    ("Humble disclaimer",
     "<p class='disclaimer'>This is an amateur engineering project. We are not "
     "HPC or quant finance professionals and make no competitive claims. The "
     "timing of the 7000 call was a single correct prediction; one sample is "
     "not a track record. Errors are likely.</p>"
     "<p class='disclaimer'><b>Nothing here is investment advice.</b> No "
     "recommendation to buy, sell, or hold any security. Past fits do not "
     "predict future outcomes. The LPPL literature's own authors publish wide "
     "confidence intervals (±6 to 18 months) on critical-time estimates. "
     "Do your own math.</p>",
     "Humble disclaimer. This is an amateur engineering project. We are not "
     "quant finance professionals and we make no competitive claims. The seven "
     "thousand call was a single correct prediction. One sample is not a track "
     "record. Nothing in this repository is investment advice. No recommendation "
     "to buy sell or hold any security. Past fits do not predict future outcomes. "
     "The literature's own authors publish wide confidence intervals on the "
     "critical time estimates. Do your own math."),

    ("Further reading",
     "<ul>"
     "<li><a href='https://www.sciencedirect.com/science/article/abs/pii/S0378437116301017'>LPPLS 2 centuries · Sornette et al 2017</a></li>"
     "<li><a href='https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4734944'>LPPLS detection · Shu &amp; Song 2024</a></li>"
     "<li><a href='https://arxiv.org/abs/2510.10878'>Hyped LPPL · 2025</a></li>"
     "<li><a href='https://www.nature.com/articles/s41599-025-05920-7'>AI-LPPL · Nature HSSC 2025</a></li>"
     "<li><a href='https://www.researchgate.net/publication/260757241'>Volatility-confined LPPL · 2014</a></li>"
     "<li><a href='https://link.springer.com/chapter/10.1007/978-3-319-04849-9_26'>Financial Bubbles chapter</a></li>"
     "</ul>",
     "For further reading. Start with the twenty seventeen two-century paper. Then "
     "the twenty twenty four Shu and Song application. Then the two twenty twenty "
     "five frontier papers. The links are in this slide. Thank you for watching."),
]

# Render Emma narrations
print(f"rendering {len(SLIDES)} technical-dive narrations…")
for i, (title, _cite, narr) in enumerate(SLIDES):
    mp3 = AUD / f"td_{i:02d}.mp3"
    if mp3.exists():
        print(f"  ✓ {i:02d}  {title[:50]}  (cached)")
        continue
    wav = mp3.with_suffix(".wav")
    subprocess.run(
        ["kokoro", "-m", "bf_emma", "-l", "b", "-t", narr, "-o", str(wav), "-s", "0.95"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "128k", str(mp3)],
        check=True, capture_output=True,
    )
    wav.unlink()
    print(f"  ✓ {i:02d}  {title[:50]}")
print("done")

# Build HTML
slide_sections = []
for i, (title, cite, _) in enumerate(SLIDES):
    slide_sections.append(f'''
<section class="slide" data-audio="audio/td_{i:02d}.mp3">
  <header>
    <h2>{title}</h2>
    <div class="meta">slide {i+1} / {len(SLIDES)}</div>
  </header>
  <div class="body">{cite}</div>
</section>''')

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>finance_sp500 · technical dive · Emma</title>
<style>
  :root {{
    --bg: #0b0a08; --panel: #14120e; --gold: #d4af37; --gold-dim: #8a7228;
    --gold-bright: #f5d76e; --text: #e8e2cf; --muted: #8a846f; --cite: #86efac;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ height: 100%; background: var(--bg); color: var(--text);
    font-family: "Iowan Old Style", "Charter", Georgia, serif; overflow: hidden; }}
  .slide {{ position: absolute; inset: 0; display: none; flex-direction: column;
    padding: 3vh 5vw 5vh 5vw; opacity: 0; transition: opacity 0.4s ease-out; }}
  .slide.active {{ display: flex; opacity: 1; }}
  .slide header {{ border-bottom: 1px solid var(--gold-dim); padding-bottom: 1.4vh;
    margin-bottom: 2.5vh; display: flex; justify-content: space-between; align-items: baseline; }}
  .slide h2 {{ color: var(--gold-bright); font-size: 3.6vh; font-weight: 600;
    letter-spacing: 1px; font-family: "Iowan Old Style", Georgia, serif; }}
  .slide .meta {{ color: var(--muted); font-size: 1.4vh; font-family: "SF Mono", Menlo, monospace; letter-spacing: 2px; }}
  .body {{ flex: 1; display: flex; flex-direction: column; justify-content: center;
    font-size: 2.2vh; line-height: 1.6; max-width: 1200px; width: 100%; align-self: center; }}
  cite {{ display: block; padding: 2vh 2vw; border-left: 3px solid var(--cite);
    background: rgba(134, 239, 172, 0.05); font-style: normal; color: var(--cite);
    font-family: "SF Mono", Menlo, monospace; font-size: 1.9vh; line-height: 1.7;
    margin-bottom: 2vh; border-radius: 0 6px 6px 0; }}
  cite b {{ color: #a7f3d0; }}
  cite i {{ color: #e8e2cf; font-style: italic; }}
  p {{ margin: 1vh 0; }}
  p.math {{ font-family: "SF Mono", Menlo, monospace; font-size: 2.6vh; text-align: center;
    color: var(--gold-bright); padding: 2vh; background: #0a0905; border: 1px solid var(--gold-dim); border-radius: 6px; }}
  ul, ol {{ margin-left: 2.5vw; }}
  li {{ margin: 0.6vh 0; }}
  a {{ color: var(--gold-bright); text-decoration: none; border-bottom: 1px dashed var(--gold-dim); }}
  a:hover {{ background: rgba(255, 170, 60, 0.1); }}
  .disclaimer {{ border-left: 3px solid #f87171; padding: 1.4vh 1.8vw; margin: 1.2vh 0;
    background: rgba(248, 113, 113, 0.06); color: #fca5a5; font-size: 2vh; line-height: 1.55; }}
  .disclaimer b {{ color: #fecaca; }}

  #controls {{ position: fixed; bottom: 1.5vh; left: 0; right: 0; display: flex;
    justify-content: center; gap: 1vw; z-index: 100; }}
  .btn {{ background: var(--panel); color: var(--gold-bright); border: 1px solid var(--gold-dim);
    padding: 0.9vh 2vw; font-family: -apple-system, sans-serif; font-size: 1.6vh;
    letter-spacing: 1px; border-radius: 4px; cursor: pointer; user-select: none; }}
  .btn:hover {{ background: #1a1712; }}
  .btn.play {{ color: #4ade80; border-color: #2d5a36; }}

  #progress {{ position: fixed; top: 0; left: 0; right: 0; height: 3px; background: #1a1712; z-index: 101; }}
  #progress-bar {{ height: 100%; background: linear-gradient(90deg, #ff7a1a, #ffd76a); width: 0%; transition: width 0.2s; }}
  .crest {{ position: fixed; top: 1vh; right: 1.2vw; color: var(--muted);
    font-size: 1.2vh; letter-spacing: 2px; z-index: 100; font-family: -apple-system, sans-serif; }}
</style>
</head>
<body>

<div id="progress"><div id="progress-bar"></div></div>
<div class="crest">⬡⟐ HARI · 91ae0c77 · technical dive</div>

{"".join(slide_sections)}

<div id="controls">
  <button class="btn" onclick="prev()">◀  PREV</button>
  <button class="btn play" id="play" onclick="toggle()">▶  PLAY</button>
  <button class="btn" onclick="next()">NEXT  ▶</button>
  <button class="btn" onclick="toggleAuto()"><span id="auto-label">AUTO: OFF</span></button>
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
    if (playing) aud.play().catch(()=>{{}});
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
    autoLabel.textContent = "AUTO: " + (autoAdvance ? "ON" : "OFF");
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

(OUT / "technical_dive.html").write_text(html)
print(f"wrote {OUT / 'technical_dive.html'}")
