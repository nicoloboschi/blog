+++
date = '2026-06-16T08:00:00+01:00'
draft = false
title = "How I code from anywhere at any time"
description = "I work across many repos and many workspaces in parallel. Terminals and IDEs got in the way, so I built vipershell: a browser-based dev environment I reach from my phone over Tailscale."
tags = ["AI", "agents", "developer-tools", "terminal", "workflow", "engineering"]
+++

**TL;DR**: I work on many repos at once, and on the same repo in different workspaces, parallelizing everything with agents. Terminal apps felt too constrained and coding UIs too slow for parallel work, so I built vipershell. Three months in, I haven't opened an IDE or a terminal app.

---

I'm a software engineer and I work daily on different repos, often on the same repo in different workspaces, parallelizing the work. Most of those panes are agents - Claude Code, Codex, Hermes - doing something while I'm looking at something else.

That broke my tools. Terminal apps felt too constrained, and every coding UI I tried was just not efficient for working on parallel things. tmux gives you panes of text, but a workspace is a terminal *plus* its git state *plus* the files that changed - so I was switching between them all day. The IDE has the opposite problem: heavy and single-rooted, one window per project, a new language server every time I open another workspace.

So I built my own app. It's called **vipershell** ([nicoloboschi/vipershell](https://github.com/nicoloboschi/vipershell)).

- open source
- runs locally
- access via the browser
- reach my laptop from my phone over Tailscale
- each pane gives you terminal, git and files
- first-class support for Claude Code, Codex and Hermes
- persistent terminal sessions

The browser part is the key for "anywhere." It runs locally on my laptop where the repos and agents live, and the frontend is just a browser - so the same vipershell opens on my phone over [Tailscale](https://tailscale.com/), with the sessions exactly where I left them because they never stopped. I start something on the couch and unblock it from my phone later.

In my opinion the terminal and the IDE aren't bad - they just weren't built for running many agents across many workspaces at once. So I built the thing that was. Three months, no IDE, no terminal app.

It's open source on [GitHub](https://github.com/nicoloboschi/vipershell), and here's a [short demo](https://www.youtube.com/watch?v=kdWoWgU27VA) of it in action. If you live across many repos and many agents too, give it a try.
