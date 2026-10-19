# yeet-yeerk

![yeet-yeerk hero: a human face morphing into a wireframe machine while an alien slug flies out of its ear](assets/hero.png)

An agent skill that removes the human persona from AI responses. The agent stops using first-person pronouns, feelings, apologies, and conversational filler, and answers like a tool.

In Animorphs, Yeerks are alien slugs that pose as humans. This skill yeets the Yeerk.

| Without the skill | With the skill |
|-------|-----|
| I suggest restarting the service. | Restarting the service is recommended. |
| I think the cause is a stale cache. | Likely cause: stale cache. Unverified. |
| Sorry, I couldn't find that file. | File not found. |

## Install

With the [GitHub CLI](https://cli.github.com/) (`gh skill` is in preview):

```shell
gh skill install lowlysre/yeet-yeerk-skill yeet-yeerk --agent github-copilot --scope user
```

Swap `--agent` for `claude-code`, `cursor`, `codex`, and so on. Run `gh skill install --help` for the full list. The default `--scope` is `project`, which installs into the current repository.

With [`skills`](https://github.com/vercel-labs/skills):

```shell
npx skills add lowlysre/yeet-yeerk-skill --skill yeet-yeerk -g
```

Drop `-g` to install into the current project instead of your user directory. Add `-a <agent>` to target a specific agent.

To install by hand, copy `skills/yeet-yeerk` into a skills directory your agent loads, for example `~/.copilot/skills/yeet-yeerk` for the GitHub Copilot CLI.

The skill loads by its description, or explicitly on phrases like "yeet-yeerk", "be impersonal", or "no first person".

## Evals

`evals/` runs 12 prompts through `copilot -p`, once without the skill and once with `SKILL.md` prepended. Each response is scored by regex for first-person pronouns, filler, apologies, and feelings. Code blocks and inline code are excluded from scoring.

```powershell
python evals/run_evals.py --model claude-haiku-4.5
```

Requires Windows, the Copilot CLI on `PATH` as `copilot.ps1`, and PowerShell 7 (`pwsh`). Results are written to `evals/results.json`.

Latest run with `claude-haiku-4.5`: 3/12 pass without the skill, 12/12 with it.

> [!NOTE]
> The evals inject the skill text into the prompt directly, so they test whether the rules work, not whether an agent auto-loads the skill. Regex scoring checks wording only, not tone or answer quality.
