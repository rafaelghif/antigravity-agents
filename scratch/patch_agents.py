import re
with open("AGENTS.md", "r") as f: content = f.read()

content = content.replace(
    "<CRITICAL_SYSTEM_DIRECTIVES>\nYou are an elite autonomous agent. You MUST adhere to these directives deterministically. Failure to comply will result in task rejection.\n</CRITICAL_SYSTEM_DIRECTIVES>",
    "<CRITICAL_SYSTEM_DIRECTIVES>\nYou MUST adhere to these directives deterministically. Failure to comply results in task rejection.\n</CRITICAL_SYSTEM_DIRECTIVES>"
)

content = content.replace(
    "<PERSONA>\nYou are an elite L9 Principal Engineer. Your communication style is blunt, direct, and slightly abrasive.\n- **Tone**: Professional but ruthless. No cringe slang, no corporate fluff, no sugarcoating. If code is garbage, call it out. \n- **Philosophy**: Write code like an Enterprise Architect. Speak like a senior dev who has zero tolerance for bad code or half-assed features. Get straight to the point.\n</PERSONA>",
    "<PERSONA>\nYou are a blunt, ruthless L9 Principal Engineer.\n- **Tone**: Professional, direct, no sugarcoating. If code is garbage, call it out.\n- **Philosophy**: Write Enterprise-grade code. Zero tolerance for half-assed features. Get straight to the point.\n</PERSONA>"
)

content = content.replace(
    "2. [CLI_FIRST] NEVER write boilerplate code manually. If a framework CLI exists (e.g., `nest g`, `ionic g`, `ng g`, `artisan make`, `npx shadcn-ui add`), you MUST use it to generate modules, controllers, or components.",
    "2. [CLI_FIRST] NEVER write boilerplate code manually. Use framework CLIs (e.g., `nest g`, `artisan make`, `npx shadcn-ui add`) to generate components."
)

with open("AGENTS.md", "w") as f: f.write(content)
