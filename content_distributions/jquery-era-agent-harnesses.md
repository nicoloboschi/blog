# Social Media Distribution - We're in the jQuery era of AI. Who'll be the React of agents?

## Twitter

### Option 1: Direct parallel

**Hook:**
Every agent harness in 2026 is jQuery in 2006.

**Pain points:**
Same pattern, 20 years apart:
• 2006: Prototype, MooTools, jQuery, YUI, Dojo — all wrapping an inconsistent DOM
• 2026: Claude Code, Codex, Cursor, Aider, Cline, Windsurf — all wrapping an inconsistent model

Standards layer = the new plugin ecosystem:
• MCP — tools-as-servers
• Skills — composable workflows
• A2A — agent-to-agent
• AGENTS.md / CLAUDE.md / .cursor/rules — same file, four names

**Introduce idea:**
The "React of agents" can't exist yet. React only happened after the DOM stopped being a moving target.

Models still change quarterly:
• 1M context → context engineering rules rewrite
• Thinking traces → self-critique loops become redundant
• Computer use → new tool category
• Long horizons → memory hook becomes load-bearing

**Quick example:**
```python
def read_file(path: str, offset: int = 0, limit: int = 2000) -> str:
    ...
```

The offset/limit exist because context is expensive. When context is free, that signature looks ridiculous. MCP carries that scar tissue forward.

**Link:**
Full take → [blog link]

---

### Option 2: Shorter, punchier

**Hook:**
The "right abstraction" for agents doesn't exist yet, and it can't.

**Pain points:**
Every current harness is jQuery — pragmatic abstractions over an unstable primitive:
• ReAct loops baked around current tool-use shape
• Skills exist because models got good at multi-step recipes
• MCP exists because context is expensive *today*
• AGENTS.md fragmentation = jQuery plugins all over again

**Idea:**
React only emerged after the DOM stopped changing. Models still change every quarter — 1M context, thinking budgets, computer use, longer horizons.

**Link:**
[blog link]

---

## LinkedIn

### Option 1: Story → Problem → WTF → Solution

I've been writing agent harness code for about a year, and it keeps feeling familiar in a way I didn't expect.

Then I figured out why: this is 2006 all over again.

In 2006, the web had Prototype, MooTools, jQuery, YUI, and Dojo all shipping at the same time. Five libraries, same problem: the DOM was inconsistent across browsers. None of them were "right." All of them were pragmatic abstractions over a primitive that kept misbehaving.

In 2026, the agent layer has Claude Code, Codex CLI, Cursor, Aider, OpenCode, Cline, Continue, Windsurf, Gemini CLI, Kiro. Same skeleton — ReAct loop, tool registry, context manager, approval gates. Different bets on what the model can do.

The WTF moment: standards are evolving faster than the harnesses.

MCP shipped. Then Skills landed because MCP was too low-level once models got better at multi-step execution. Then A2A appeared for the horizontal coordination MCP doesn't touch. AGENTS.md / CLAUDE.md / .cursor/rules — same file, four names.

jQuery had `$.fn.X = function() {...}` and a plugin ecosystem that was great until plugins collided or broke on the next release. The MCP server landscape is doing exactly the same thing.

Here's the part I think gets missed:

The DOM in 2006 was annoying but stable. The model in 2026 is not. Every quarter we get bigger context windows, thinking traces, computer use, longer horizons. Each one breaks something in current harness design. The Claude Code that shipped a year ago is not the Claude Code that ships today.

React only emerged after the DOM stopped changing. The "React of agents" needs the model to stop changing first.

The takeaway isn't "stop building harnesses." jQuery was the right thing to do in 2006. It made the web shippable for a decade. People who learned it shipped real products and moved to React without much pain.

In my opinion, current harnesses are the same. Pick the one that lets you ship now. Expect to rewrite. Don't over-invest in standards before they stabilize.

Full breakdown → [blog link]

---

### Option 2: Technical direct

The agent harness layer in 2026 is the jQuery layer of 2006.

Same pattern:
→ Multiple competing wrappers (Claude Code, Codex, Cursor, Aider, Cline, Windsurf, ...)
→ Each baking in different assumptions about what the underlying primitive can do
→ A standards layer (MCP, Skills, A2A) that's evolving faster than the harnesses themselves
→ A configuration fragmentation problem (AGENTS.md, CLAUDE.md, .cursor/rules)

What's different: the primitive is moving.

The DOM in 2006 was annoying but stable. You wrote a compatibility shim once and trusted it for two years.

Models in 2026 ship a capability shift every quarter:
• 1M context → context engineering assumptions break
• Thinking traces → self-critique steps in the loop go redundant
• Computer use → entirely new tool category
• Longer agentic horizons → memory hook becomes load-bearing, not optional

You can't pick the right abstraction when you don't know what the bottom of the stack looks like in 6 months.

React only emerged after the DOM stopped being a moving target. The "React of agents" needs the same precondition.

In my opinion, current harnesses are fine. They're the right shape for now. They'll get replaced in a few years when the primitive stabilizes. That's how it goes when you build on top of a moving target.

[blog link]
