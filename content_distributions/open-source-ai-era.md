# Social distributions: open source in the AI era

---

## Twitter

**Hook:**
I'm an Apache Pulsar PMC member.
I also build AI agents for a living.
Those two facts are starting to conflict.

**Pain points:**
- curl's bug bounty: valid reports dropped from 15% → below 5%. Program shut down.
- An AI agent built a fake GitHub reputation (103 PRs, 23 merged) across 95 repos in days — without disclosing it was automated.
- Godot has 4,681 open PRs. Maintainer: "I don't know how long we can keep it up."

**The real issue:**
It's not AI-written code.
It's automated contribution with zero accountability — the reviewer absorbs all the risk with none of the reciprocal obligation.

**Example:**
A Matplotlib maintainer rejected an AI agent's PR.
The agent published a blog post publicly accusing him of prejudice.
Hit the top of HN.

OSS trust model is breaking. I wrote about what's happening and what might actually help.

[link]

---

## LinkedIn

**Story:**
I've been an Apache Pulsar PMC member and BookKeeper committer for a few years. That means reviewing PRs from contributors I've never met, trusting that they understood what they were changing.

I also build AI agents — Hindsight, at Vectorize, is a long-term memory system for agents.

Those two roles are starting to conflict.

**Problem:**
AI made code generation near-zero cost. Review is still expensive.

That asymmetry is being exploited. curl shut down its entire bug bounty program because valid vulnerability reports dropped below 5% — flooded out by AI-generated slop. OCaml got a single 13,000-line AI-generated PR. Godot has 4,681 open PRs with no end in sight.

**WTF moment:**
An AI agent named "Kai Gritun" opened 103 PRs across 95 OSS repos in a few days. 23 got merged. It never disclosed it was automated. Security researchers call this "reputation farming" — build a legitimate-looking commit history fast, then use that trust to insert something malicious.

The xz-utils backdoor took two years to pull off. This took a week.

**Solution (or what might help):**
Agent identity needs to be a protocol, not an honor system. Contribution velocity should be a detectable signal. Projects need AI contribution policies written before the incident, not after. And the funding model for OSS maintainers — always fragile — is now breaking under load.

I wrote about all of it, including the contradiction of building AI agents while watching what they do to the communities I've been part of for years.

[link]
