"""
Template management for different output verbosity levels.

Uses Jinja2 templates to generate clean, customizable markdown output
for different verbosity levels and use cases.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

try:
    from jinja2 import Environment, BaseLoader, Template, select_autoescape
except ImportError:
    # Fallback if Jinja2 is not available
    Environment = None
    BaseLoader = None
    Template = None
    select_autoescape = None

from ..models.elements import Module, Class, Function, Parameter, ImportStatement
from ..models.index import CrossReferenceIndex
from ..utils.text_processing import (
    sanitize_anchor, generate_wikilink, format_inline_code,
    extract_summary_sentence, humanize_identifier
)

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manages Jinja2 templates for different verbosity levels and output formats.
    """
    
    def __init__(self, verbosity: str = "standard"):
        """
        Initialize the template manager.
        
        Args:
            verbosity: Output verbosity level (minimal, standard, detailed)
        """
        self.verbosity = verbosity
        self.env: Optional[Environment] = None # type: ignore
        self._setup_environment()
    
    def _setup_environment(self) -> None:
        """Setup Jinja2 environment with custom filters and functions."""
        if Environment is None:
            logger.warning("Jinja2 not available, falling back to string templates")
            return
        
        self.env = Environment(
            loader=TemplateLoader(),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters.update({
            'anchor': sanitize_anchor,
            'wikilink': generate_wikilink,
            'inline_code': format_inline_code,
            'summary': extract_summary_sentence,
            'humanize': humanize_identifier,
        })
        
        # Add custom functions
        self.env.globals.update({
            'range': range,
            'len': len,
            'enumerate': enumerate,
            'zip': zip,
        })
    
    def render_module(
        self, 
        module: Module, 
        index: CrossReferenceIndex,
        **kwargs
    ) -> str:
        """
        Render a complete module documentation.
        
        Args:
            module: Module to render
            index: Cross-reference index for linking
            **kwargs: Additional template variables
            
        Returns:
            Rendered markdown content
        """
        if self.env is None:
            return self._render_module_fallback(module, index, **kwargs)
        
        template_name = f"module_{self.verbosity}.md.j2"
        try:
            template = self.env.get_template(template_name)
        except Exception:
            # Fallback to default template
            template = self.env.get_template("module_standard.md.j2")
        
        context = {
            'module': module,
            'index': index,
            'verbosity': self.verbosity,
            **kwargs
        }
        
        return template.render(**context)
    
    def render_class(
        self, 
        cls: Class, 
        module: Module,
        index: CrossReferenceIndex,
        **kwargs
    ) -> str:
        """
        Render class documentation.
        
        Args:
            cls: Class to render
            module: Parent module
            index: Cross-reference index
            **kwargs: Additional template variables
            
        Returns:
            Rendered markdown content
        """
        if self.env is None:
            return self._render_class_fallback(cls, module, index, **kwargs)
        
        template_name = f"class_{self.verbosity}.md.j2"
        try:
            template = self.env.get_template(template_name)
        except Exception:
            template = self.env.get_template("class_standard.md.j2")
        
        context = {
            'class': cls,
            'module': module,
            'index': index,
            'verbosity': self.verbosity,
            **kwargs
        }
        
        return template.render(**context)
    
    def render_function(
        self, 
        func: Function, 
        module: Module,
        index: CrossReferenceIndex,
        is_method: bool = False,
        **kwargs
    ) -> str:
        """
        Render function documentation.
        
        Args:
            func: Function to render
            module: Parent module
            index: Cross-reference index
            is_method: Whether this is a class method
            **kwargs: Additional template variables
            
        Returns:
            Rendered markdown content
        """
        if self.env is None:
            return self._render_function_fallback(func, module, index, is_method, **kwargs)
        
        template_name = f"function_{self.verbosity}.md.j2"
        try:
            template = self.env.get_template(template_name)
        except Exception:
            template = self.env.get_template("function_standard.md.j2")
        
        context = {
            'function': func,
            'module': module,
            'index': index,
            'is_method': is_method,
            'verbosity': self.verbosity,
            **kwargs
        }
        
        return template.render(**context)
    
    # Fallback methods for when Jinja2 is not available
    
    def _render_module_fallback(
        self, 
        module: Module, 
        index: CrossReferenceIndex,
        **kwargs
    ) -> str:
        """Fallback module rendering without Jinja2."""
        lines = []
        
        # Title
        lines.append(f"# {module.name}")
        lines.append("")
        
        # Docstring
        if module.docstring:
            lines.append(f"> {module.docstring}")
            lines.append("")
        
        # Statistics
        if self.verbosity in ("standard", "detailed"):
            lines.append("## Overview")
            lines.append("")
            lines.append(f"- **Classes:** {len(module.classes)}")
            lines.append(f"- **Functions:** {len(module.functions)}")
            lines.append(f"- **Lines of Code:** {module.lines_of_code}")
            lines.append("")
        
        # Classes
        if module.classes:
            lines.append("## Classes")
            lines.append("")
            for cls in module.classes:
                class_content = self._render_class_fallback(cls, module, index)
                lines.append(class_content)
                lines.append("")
        
        # Functions
        if module.functions:
            lines.append("## Functions")
            lines.append("")
            for func in module.functions:
                func_content = self._render_function_fallback(func, module, index, False)
                lines.append(func_content)
                lines.append("")
        
        return "\n".join(lines)
    
    def _render_class_fallback(
        self, 
        cls: Class, 
        module: Module,
        index: CrossReferenceIndex,
        **kwargs
    ) -> str:
        """Fallback class rendering without Jinja2."""
        lines = []
        
        # Header
        anchor = sanitize_anchor(f"class-{cls.name}")
        if self.verbosity == "minimal":
            lines.append(f"### {cls.name}")
        elif self.verbosity == "standard":
            lines.append(f"### {cls.name} {{#{anchor}}}")
        else:  # detailed
            lines.append(f"### Class: {cls.name} {{#{anchor}}}")
        
        lines.append("")
        
        # Docstring
        if cls.docstring:
            if self.verbosity == "minimal":
                lines.append(extract_summary_sentence(cls.docstring))
            else:
                lines.append(f"> {cls.docstring}")
            lines.append("")
        
        # Base classes
        if cls.base_classes and self.verbosity in ("standard", "detailed"):
            base_links = [format_inline_code(base) for base in cls.base_classes]
            lines.append(f"**Inherits from:** {', '.join(base_links)}")
            lines.append("")
        
        # Methods
        if cls.methods and self.verbosity in ("standard", "detailed"):
            lines.append("#### Methods")
            lines.append("")
            for method in cls.methods:
                method_content = self._render_function_fallback(method, module, index, True)
                lines.append(method_content)
                lines.append("")
        
        return "\n".join(lines)
    
    def _render_function_fallback(
        self, 
        func: Function, 
        module: Module,
        index: CrossReferenceIndex,
        is_method: bool = False,
        **kwargs
    ) -> str:
        """Fallback function rendering without Jinja2."""
        lines = []
        
        # Header
        anchor = sanitize_anchor(f"{'method' if is_method else 'function'}-{func.name}")
        header_level = "####" if is_method else "###"
        
        if self.verbosity == "minimal":
            lines.append(f"{header_level} {func.name}")
        elif self.verbosity == "standard":
            lines.append(f"{header_level} {func.name} {{#{anchor}}}")
        else:  # detailed
            prefix = "Method" if is_method else "Function"
            lines.append(f"{header_level} {prefix}: {func.name} {{#{anchor}}}")
        
        lines.append("")
        
        # Signature
        if self.verbosity in ("standard", "detailed"):
            lines.append(f"**Signature:** {format_inline_code(func.signature)}")
            lines.append("")
        
        # Docstring
        if func.docstring:
            if self.verbosity == "minimal":
                lines.append(extract_summary_sentence(func.docstring))
            else:
                lines.append(f"> {func.docstring}")
            lines.append("")
        
        return "\n".join(lines)


class TemplateLoader(BaseLoader):
    """
    Custom Jinja2 template loader that provides built-in templates.
    """
    
    def __init__(self):
        self.templates = self._get_builtin_templates()
    
    def get_source(self, environment, template):
        if template not in self.templates:
            raise FileNotFoundError(f"Template {template} not found")
        
        source = self.templates[template]
        return source, None, lambda: True
    
    def list_templates(self):
        return list(self.templates.keys())
    
    def _get_builtin_templates(self) -> Dict[str, str]:
        """Get built-in template definitions."""
        return {
            "module_minimal.md.j2": """# {{ module.name }}

{% if module.docstring %}
{{ module.docstring | summary }}
{% endif %}

{% if module.classes %}
## Classes
{% for class in module.classes %}
- [[#{{ class.name | anchor }}|{{ class.name }}]]
{% endfor %}
{% endif %}

{% if module.functions %}
## Functions  
{% for function in module.functions %}
- [[#{{ function.name | anchor }}|{{ function.name }}]]
{% endfor %}
{% endif %}""",

            "module_standard.md.j2": """# {{ module.name }}

{% if module.docstring %}
> {{ module.docstring }}
{% endif %}

## Overview

- **Classes:** {{ module.classes | length }}
- **Functions:** {{ module.functions | length }}
- **Lines of Code:** {{ module.lines_of_code }}

{% if module.imports %}
## Imports
{% for import in module.imports %}
{% if import.module %}
- **from** {{ import.module | inline_code }} **import** {{ import.names | map('first') | join(', ') | inline_code }}
{% else %}
- **import** {{ import.names | map('first') | join(', ') | inline_code }}
{% endif %}
{% endfor %}
{% endif %}

{% if module.classes %}
## Classes
{% for class in module.classes %}
### {{ class.name }} {#{{ ('class-' + class.name) | anchor }}}

{% if class.docstring %}
> {{ class.docstring }}
{% endif %}

{% if class.base_classes %}
**Inherits from:** {{ class.base_classes | map('inline_code') | join(', ') }}
{% endif %}

{% if class.methods %}
#### Methods
{% for method in class.methods %}
##### {{ method.name }} {#{{ ('method-' + method.name) | anchor }}}

{% if method.docstring %}
> {{ method.docstring | summary }}
{% endif %}

**Signature:** {{ method.signature | inline_code }}
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}

{% if module.functions %}
## Functions
{% for function in module.functions %}
### {{ function.name }} {#{{ ('function-' + function.name) | anchor }}}

{% if function.docstring %}
> {{ function.docstring }}
{% endif %}

**Signature:** {{ function.signature | inline_code }}
{% endfor %}
{% endif %}""",

            "module_detailed.md.j2": """---
title: {{ module.name }}
type: module
file_path: {{ module.file_path }}
stats:
  classes: {{ module.classes | length }}
  functions: {{ module.functions | length }}
  lines_of_code: {{ module.lines_of_code }}
tags:
  - python
  - module
---

# {{ module.name }}

{% if module.docstring %}
> [!info] Module Documentation
> {{ module.docstring }}
{% endif %}

## Overview

- **Classes:** {{ module.classes | length }}
- **Functions:** {{ module.functions | length }}  
- **Lines of Code:** {{ module.lines_of_code }}
- **Complexity:** {{ module.classes | map(attribute='methods') | map('length') | sum + module.functions | length }}

{% if module.imports %}
## Imports

{% for import in module.imports %}
{% if import.module %}
- **from** {{ import.module | inline_code }} **import** 
{% for name, alias in import.names %}
  - {{ name | inline_code }}{% if alias %} as {{ alias | inline_code }}{% endif %}
{% endfor %}
{% else %}
- **import**
{% for name, alias in import.names %}
  - {{ name | inline_code }}{% if alias %} as {{ alias | inline_code }}{% endif %}
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}

{% if module.classes %}
## Classes

{% for class in module.classes %}
### Class: {{ class.name }} {#{{ ('class-' + class.name) | anchor }}}

{% if class.docstring %}
> [!note] Class Documentation
> {{ class.docstring }}
{% endif %}

{% if class.base_classes %}
**Inherits from:** {{ class.base_classes | map('inline_code') | join(', ') }}
{% endif %}

**Metrics:**
- Methods: {{ class.methods | length }}
- Lines of Code: {{ class.lines_of_code }}

{% if class.methods %}
#### Methods

{% for method in class.methods %}
##### {{ method.name }} {#{{ ('method-' + method.name) | anchor }}}

{% if method.docstring %}
> {{ method.docstring }}
{% endif %}

**Signature:** {{ method.signature | inline_code }}

{% if method.parameters %}
**Parameters:**
{% for param in method.parameters %}
- **{{ param.name }}**{% if param.type_ref %}: {{ param.type_ref.name | inline_code }}{% endif %}{% if param.default_value %} = {{ param.default_value | inline_code }}{% endif %}
{% endfor %}
{% endif %}

{% if method.return_type %}
**Returns:** {{ method.return_type.name | inline_code }}
{% endif %}

{% if method.complexity > 1 %}
**Complexity:** {{ method.complexity }}
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}

{% if module.functions %}
## Functions

{% for function in module.functions %}
### Function: {{ function.name }} {#{{ ('function-' + function.name) | anchor }}}

{% if function.docstring %}
> [!note] Function Documentation  
> {{ function.docstring }}
{% endif %}

**Signature:** {{ function.signature | inline_code }}

{% if function.parameters %}
**Parameters:**
{% for param in function.parameters %}
- **{{ param.name }}**{% if param.type_ref %}: {{ param.type_ref.name | inline_code }}{% endif %}{% if param.default_value %} = {{ param.default_value | inline_code }}{% endif %}
{% endfor %}
{% endif %}

{% if function.return_type %}
**Returns:** {{ function.return_type.name | inline_code }}
{% endif %}

{% if function.complexity > 1 %}
**Complexity:** {{ function.complexity }}
{% endif %}

{% if function.calls %}
**Calls:**
{% for call in function.calls[:10] %}
- {{ call.call_chain | join('.') | inline_code }}
{% endfor %}
{% if function.calls | length > 10 %}
- ... and {{ function.calls | length - 10 }} more
{% endif %}
{% endif %}
{% endfor %}
{% endif %}""",
        }


def create_template_manager(verbosity: str = "standard") -> TemplateManager:
    """
    Create a template manager for the specified verbosity level.
    
    Args:
        verbosity: Output verbosity level
        
    Returns:
        Configured template manager
    """
    return TemplateManager(verbosity)