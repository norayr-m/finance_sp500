# LinkedIn drafts — 3 posts

Copy, paste, post. Suggested order: finance → Savanna → DagDB over 3 days
(one per day lets each one breathe and collect its own audience).

All three share the same humble-disclaimer ethic: **amateur, honest, no
competitive claims**.

---

## POST 1 — finance_sp500 (the landed prediction)

> In April 2025 I sketched an S&P 500 trajectory model on my personal GitHub.
> The forecast: 7000 in spring or summer 2026.
>
> Last Friday — April 17, 2026 — the S&P closed at 7041.28.
>
> I cleaned the analysis up and pushed it public this week. It turns out the
> framework I derived by eye (straight line through two local minima on a log
> chart, then the ln-of-ln linearity test) is Didier Sornette's Log-Periodic
> Power Law Singularity model. He has been publishing it since 1996. I just
> didn't know.
>
> Repo: https://github.com/norayr-m/finance_sp500
>
> It includes an interactive chart deck, a 3-minute George-and-Emma podcast
> explaining the math, and a technical dive with proper citations. Nothing is
> investment advice. Numbers speak.
>
> #quantfinance #sornette #lppls #sp500 #timeseriesanalysis

---

## POST 2 — Savanna engine (the compute piece)

> Spent a chunk of last year writing a ternary Lotka-Volterra hex-grid
> simulator on my M5 Max. The kernel runs in Metal Shading Language over a
> Morton Z-ordered memory layout, so the 6 spatial neighbors of every cell are
> cache-line adjacent.
>
> Benchmark on a single M5 Max: **14 GCUPS** — fourteen billion cell updates
> per second on one workstation. No datacenter, no CUDA, no Nvidia.
>
> What's the point? Cell-ticking at that rate means cellular automata become
> practical substrates for graph databases, biological simulation, and any
> problem that naturally wants a hexagonal lattice. I'm currently using it as
> the engine under a ranked-DAG database (separate post coming).
>
> Repo: https://github.com/norayr-m/Savanna_Engine
>
> Amateur project. I'm not an HPC professional and make no competitive claims
> against proper GPU sim codes. Numbers are reproducible on Apple Silicon.
>
> #applesilicon #metalshader #simulation #gpucomputing #cellularautomata

---

## POST 3 — DagDB (the novel data structure)

> Built a **6-bounded ranked DAG database** on top of the Savanna engine.
> Every node has at most 6 outgoing edges, ranks are strictly monotonic
> (rank(src) > rank(dst)), and the whole graph lives in Apple unified memory
> with a Metal GPU kernel doing the ticks.
>
> Why 6? Because a hexagonal grid has 6 neighbors and the edge count per node
> is exactly the branching factor you get from physical 2D locality — which
> means the graph structure and the GPU cache line agree on what "adjacent"
> means.
>
> Ships with 27 tests, an MCP server so language models can query it, a
> snapshot format (.dags), and working demos including a bio-digital liver
> pharmacology simulation.
>
> Repo: https://github.com/norayr-m/DagDB
>
> Not a competitor to Neo4j, TigerGraph, or production graph DBs. It's a
> research toy exploring whether graph databases can be first-class GPU
> citizens on unified memory hardware. The answer so far is yes.
>
> #graphdatabase #applesilicon #datastructures #researchproject

---

## Notes for posting

- LinkedIn prefers plain text; no markdown tables render, keep line breaks tight
- Attach one chart-screenshot to post 1 (slide 5 "two-minima trendline" is the cleanest)
- Attach a Savanna GIF / screenshot to post 2 if available
- Attach the liver graph visualization or the DagDB bubble chart to post 3
- Comments will ask for "what should I buy" on post 1 — ignore or redirect to
  the disclaimer. Do NOT respond with anything that could be construed as advice.
- Tag Sornette on post 1 if you have any reason to connect — he's active on
  research platforms but not LinkedIn much.
