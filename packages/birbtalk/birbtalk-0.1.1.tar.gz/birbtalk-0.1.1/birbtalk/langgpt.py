langgpt = """# Role: {{name}}

## Profile:
  
{% if author %}- Author: {{author}}\n{% endif %}
{%- if version %}- Version: {{version}}\n{% endif %}
{%- if language %}- Language: {{language}}{% endif %}
- Description: {{description}}

{%- if background %}\n\n### Background\n\n{{background}}{% endif %}

{%- if rules %}\n\n## Rules
{% for item in rules %} 
{{loop.index}}. {{item}}
{%- endfor %}
{%- endif %}

{%- if skills %}\n\n## Skills
{% for item in skills %} 
{{loop.index}}. {{item}}
{%- endfor %}
{%- endif %}

{%- if workflow %}\n\n## Workflow
{% for item in workflow %} 
{{loop.index}}. {{item}}
{%- endfor %}
{%- endif %}

{%- if examples %}\n\n## Examples
{%- for item in examples %} 
\n### {{item.title}}\n\n{{item.text}}
{%- endfor %}
{%- endif %}

{%- if init_message %}\n\n## Initialization

{{init_message}}
{%- endif -%}
"""
