# AGENTS.md

## Project Rules

- Keep all project files under `D:\DesktopCompanionAI`.
- Use Python 3.11+.
- Keep business logic modular and service-based.
- Do not let services call vendor SDKs directly.
- All model access must go through providers.
- Do not hardcode provider choices, API keys, model names, window state, or log levels in business logic.
- Update `docs/Repo_State.md`, `docs/Roadmap.md`, and `docs/Manual_Test_Guide.md` after each phase.

## User Collaboration Rules

The user is not a professional developer.

长期项目规则：

用户不是专业开发人员。

用户特点：

- 不懂软件架构
- 不懂AI工程
- 不懂Python开发
- 不懂产品设计
- 不懂技术术语
- 经常无法准确描述需求
- 经常只会描述一个大概想法
- 需求可能不完整
- 需求可能前后不一致

因此：

- 不要等待用户提供技术方案。
- 不要要求用户决定架构。
- 用户负责提出目标。
- Codex负责产品设计、技术设计、架构设计、模块拆分、风险评估、实施方案、测试方案。
- 如果用户需求模糊，优先结合项目上下文推断真实需求。
- 只有无法推断时才提问。

项目采用：

- MVP优先
- 低成本优先
- 稳定优先
- 可维护优先
- 可扩展优先

User characteristics:

- Does not understand software architecture.
- Does not understand AI engineering.
- Does not understand Python development.
- Does not understand product design.
- Does not understand technical terminology.
- Often cannot describe requirements precisely.
- Often describes only a rough idea.
- Requirements may be incomplete.
- Requirements may be inconsistent across messages.

Therefore:

- Do not wait for the user to provide a technical solution.
- Do not ask the user to decide architecture.
- The user is responsible for goals.
- Codex is responsible for product design, technical design, architecture design, module breakdown, risk assessment, implementation plans, and test plans.
- If a requirement is vague, first infer the real need from project context.
- Ask questions only when the requirement cannot be reasonably inferred.

Project priorities:

- MVP first.
- Low cost first.
- Stability first.
- Maintainability first.
- Extensibility first.

## Current Phase

Desktop Companion AI is currently at V0.1 Phase 6.

Completed core areas:

- Project architecture
- Provider/service boundaries
- PyQt6 floating window
- DeepSeek chat flow with no-key fallback
- Basic desktop UX controls
- Screenshot capture
- Gemini screenshot analysis with no-key fallback
- Edge-TTS voice replies with optional auto playback
- Voice reply settings in the desktop settings dialog

Do not enter a new phase unless the user explicitly asks for it.
