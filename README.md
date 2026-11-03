
<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="./assets/header-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/header-light.svg">
  <img alt="Suchit Chopade — I build AI systems that have to prove their answers." src="./assets/header-dark.svg" width="100%">
</picture>

</div>

<br/>

Most AI systems are judged by how good their answers *sound*. I work on the part that decides whether an answer is **allowed to reach a user at all**: the verification layers, evaluation loops and backend plumbing that sit between a model and the real world.

<br/>

## Problems I've worked on

Each row is a real problem I have shipped a system for. The interesting part is rarely the model; it's the column in the middle.

| The problem | What made it hard | How I approached it |
|:--|:--|:--|
| **AI answers that sound right but aren't** | Errors hide inside fluent paragraphs, so one bad fact poisons a mostly-correct response | Break every response into atomic claims and score each one for trust *before* delivery |
| **Automated code review that invents bugs** | LLM reviewers comment on code they never actually parsed | Pair specialist review agents with deterministic AST checks: a finding ships only if the code's structure confirms it |
| **Grading agent runs with no answer key** | No ground-truth database to compare against | A calibrated evaluator that returns PASS / FAIL with a confidence ranking, so humans review the uncertain cases first |
| **Predicting failure in live biological systems** | Noisy IoT sensor streams, spatial context and expensive false alarms | Time-series + geospatial storage feeding a risk engine bounded by physical limits, not just model output |
| **Public pollution data nobody can act on** | City-wide air-quality spikes don't tell an inspector where to go | Turn regulator and open air-quality spikes into street-level inspection leads |
| **Judging ideas on gut feel** | Single-model opinions are confident and unfalsifiable | Parallel specialist agents grounded in live market signals, merged through a weighted scoring gate |
| **Multimodal message overload** | Text, image and voice arrive mixed, and everything looks urgent | A router that classifies each message into notify / digest / mute paths |

<sub>🏆 Best Use of AI — GDG Coimbatore (Tech for Good) &nbsp;·&nbsp; 🎯 Rank #507 — HackerRank Orchestrate</sub>

<br/>

## How I work

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="./assets/method-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/method-light.svg">
  <img alt="Frame → Ground → Guard → Ship → Measure" src="./assets/method-dark.svg" width="100%">
</picture>

<table>
<tr>
<td width="50%" valign="top">

**Verification is a boundary, not a feature.**
It sits in the architecture before the user, not in a backlog after launch.

**Models propose, structure decides.**
Probabilistic output is checked against something deterministic: an AST, a physical limit, a measured baseline.

</td>
<td width="50%" valign="top">

**Uncertain beats wrong.**
When a system can't justify an answer, it flags it for a human instead of guessing quietly.

**Stream, don't block.**
Long-running agent work goes to queues and streams back progressively, so users never stare at a spinner.

</td>
</tr>
</table>

<br/>

## Toolbelt

| | |
|:--|:--|
| **AI / ML** | `LangGraph` `LangChain` `RAG` `embeddings` `hallucination detection` `LLaMA` `Gemma` `Mixtral` `scikit-learn` |
| **Backend** | `Python` `FastAPI` `async I/O` `REST` `SSE` `webhooks` `retry / backoff` `GitHub Apps` |
| **Data** | `PostgreSQL` `pgvector` `TimescaleDB` `PostGIS` `MongoDB` `Pinecone` `Supabase` `SQLite` |
| **Code analysis** | `tree-sitter` `ts-morph` `AST verification` |
| **Infra** | `Docker` `Bun` `Linux` `Git` `pytest` |
| **Frontend** | `Next.js` `React` `TypeScript` `Tailwind` |

<br/>

## Commit telemetry

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://streak-stats.demolab.com/?user=suchitchopade3110-arch&hide_border=true&background=0D1117&stroke=30363D&ring=F0883E&fire=F0883E&currStreakNum=E6EDF3&sideNums=E6EDF3&currStreakLabel=F0883E&sideLabels=7D8590&dates=7D8590">
  <img alt="Commit streak" src="https://streak-stats.demolab.com/?user=suchitchopade3110-arch&hide_border=true&background=FFFFFF&stroke=D0D7DE&ring=BC4C00&fire=BC4C00&currStreakNum=1F2328&sideNums=1F2328&currStreakLabel=BC4C00&sideLabels=59636E&dates=59636E" width="49%">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://github-readme-stats.vercel.app/api?username=suchitchopade3110-arch&show_icons=true&hide_border=true&include_all_commits=true&count_private=true&rank_icon=percentile&bg_color=0D1117&title_color=F0883E&icon_color=F0883E&text_color=E6EDF3&ring_color=F0883E">
  <img alt="GitHub stats" src="https://github-readme-stats.vercel.app/api?username=suchitchopade3110-arch&show_icons=true&hide_border=true&include_all_commits=true&count_private=true&rank_icon=percentile&bg_color=FFFFFF&title_color=BC4C00&icon_color=BC4C00&text_color=1F2328&ring_color=BC4C00" width="49%">
</picture>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="./profile-3d-contrib/profile-night-green.svg">
  <img alt="3D contribution calendar" src="./profile-3d-contrib/profile-green-animate.svg" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://github-readme-activity-graph.vercel.app/graph?username=suchitchopade3110-arch&bg_color=0D1117&color=7D8590&line=F0883E&point=E6EDF3&area=true&area_color=F0883E&hide_border=true&title_color=E6EDF3&custom_title=Commits%20%E2%80%94%20last%2031%20days">
  <img alt="Contribution activity" src="https://github-readme-activity-graph.vercel.app/graph?username=suchitchopade3110-arch&bg_color=FFFFFF&color=59636E&line=BC4C00&point=1F2328&area=true&area_color=BC4C00&hide_border=true&title_color=1F2328&custom_title=Commits%20%E2%80%94%20last%2031%20days" width="100%">
</picture>

</div>

<br/>

## Reach me

<a href="https://suchitdev.netlify.app/"><img src="https://img.shields.io/badge/Portfolio-suchitdev.netlify.app-F0883E?style=flat-square&labelColor=0D1117"/></a>
<a href="https://www.linkedin.com/in/suchit-sachin-chopade-635347338/"><img src="https://img.shields.io/badge/LinkedIn-Suchit%20Chopade-0A66C2?style=flat-square&logo=linkedin&logoColor=white&labelColor=0D1117"/></a>
<img src="https://komarev.com/ghpvc/?username=suchitchopade3110-arch&style=flat-square&color=F0883E&label=Profile%20views"/>

Open to internships, research collaborations and backend / AI-systems roles.

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="./assets/footer-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/footer-light.svg">
  <img alt="Deterministic guarantees over probabilistic hand-waving." src="./assets/footer-dark.svg" width="100%">
</picture>
