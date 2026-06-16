# Content distribution: Why I built vipershell instead of fighting my terminal

## Twitter

### Tweet (main)

I stopped using IDEs and terminal apps 3 months ago.

My day isn't 1 repo + 1 task. It's 6 repos, some with 2-3 workspaces each, agents running in parallel.

tmux: one-dimensional text panes. Switching between terminal / git status / diff / file all day. Dies the second you want it from your phone.

IDE: heavy, single-rooted. One window = one project. Four workspaces = four language servers + four indexers melting your fan.

Neither was built for "8 sessions in flight while I supervise."

So I built vipershell:
- runs locally, opens in the browser
- each pane = terminal + git + files, all at once
- persistent sessions (close the tab, the agent keeps running)
- reach it from my phone over Tailscale
- first-class Claude Code / Codex / Hermes

Open source. 3 months, no IDE, no terminal app.

[link]

### Alt shorter hook variants
- "I haven't opened an IDE or a terminal app in 3 months. Here's the tool I built instead 👇"
- "tmux is great until your work is 15 long-running agent sessions. Then it falls apart. So did my IDE."
- "A workspace isn't a terminal. It's a terminal + git state + the files that just changed. No tool showed me all three at once, so I built one."

## LinkedIn

**Story → Problem → WTF moment → Solution → Link**

Three months ago I closed my IDE and my terminal app and never reopened them. Not a productivity stunt - they just stopped fitting how I work.

My day isn't one repo and one task. It's five or six repos, and inside some of them two or three workspaces of the same repo at different points in history. One workspace runs a long refactor, another has an agent fixing tests, another is where I'm actually typing. Claude Code, Codex and Hermes are all in the mix. The unit of work stopped being "a file" and became "a session doing something while I'm somewhere else."

That broke both my tools.

tmux is one-dimensional - panes of text. But a workspace is a terminal PLUS its git state PLUS the files that just changed. I spent the day switching between them. And accessing it from my phone? A party trick, not a workflow.

The IDE failed the opposite way: heavy and single-rooted. One window wants one project. Multiple workspaces = multiple windows, each loading its own language server and indexer. My laptop fans told me when I'd opened the fourth.

The WTF moment: I had a tool optimized for text panes and a tool optimized for one deep project, and my actual work was neither.

So I built vipershell:
- runs locally, opens in any browser
- each pane shows terminal, git and files at once
- persistent sessions - close the tab, the agent keeps running
- reachable from my phone over Tailscale, sessions exactly where I left them
- first-class support for Claude Code, Codex and Hermes

It's open source. I built it for exactly one user and one workflow - but if you also live across many repos and many agents, the terminal-vs-IDE tradeoff probably annoys you the same way it annoyed me.

[link]
