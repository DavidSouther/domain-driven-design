# Per-Phase Model Selection

Each phase of the Ailly developer loop has a different cost and capability profile. Research gathers and filters broadly. Design synthesizes and judges. Planning and implementation follow structure over long context. Cleanup tidies. The strongest reasoner is wasted on cleanup, and the cheapest model is a liability for design. This reference holds the full phase by provider mapping and the shared switch protocol, so each phase skill carries only a one-line pointer. A skill cannot change the model itself. It announces the recommended model on entry, invites a `/model` switch, and continues on the current model either way.

## Phase by Provider table

| Phase | Anthropic | OpenAI | Open Source |
| --- | --- | --- | --- |
| Research | Haiku 4.5 (thinking) | o4-mini | Qwen3-30B-A3B |
| Design | Opus 4.8 (max effort) | o3 | DeepSeek-R1 671B |
| Planning | Sonnet 4.6 (high effort) | GPT-4.1 | Llama 3.3 70B |
| Implementation | Sonnet 4.6 (high effort, 1M context) | GPT-4.1 | Llama 4 Scout |
| Cleanup | Haiku 4.5 | o4-mini | Qwen3-4B |

The effort and thinking qualifiers (`thinking`, `max effort`, `high effort`, `1M context`) are additional controls the developer sets in their UI. They are not part of the model name. The phase skill names them verbatim so the developer knows what to set.

Cleanup appears for completeness. The cleanup and refactor support phases inherit the active model and carry no announce-line recommendation.

## Detecting the active provider

The running model identity is stated in the skill's environment context, which the harness injects at session start (for example, "You are powered by the model named Opus 4.8"). The skill reads that identity and maps it to a provider column:

- A name like Opus, Sonnet, Haiku, or any `claude-*` identity maps to the **Anthropic** column.
- A name like o3, o4-mini, or any `gpt-*` identity maps to the **OpenAI** column.
- A name like Qwen, DeepSeek, or Llama maps to the **Open Source** column.

If no identity is present or the model is unrecognized, the skill falls back to the **Anthropic** column and says so. The developer can confirm the active model with `/model`.

## Switch protocol

The skill announces the recommended model for the detected provider and the current phase, then invites a switch:

- Switch with `/model`. Press `s` in the picker to switch for the current session only, leaving the saved default unchanged.
- The phase continues on the current model if the developer does not switch. There is no gate. The loop never stalls waiting for a model switch.
