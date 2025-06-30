# MDVis - Python Codebase Documentation Generator

Transform your Python codebases into rich, navigable Obsidian-compatible documentation with smart cross-references, type information, and dependency visualizations.

## ✨ Features

- 🔗 **Smart Cross-References** - Automatic linking between modules, classes, functions, and types
- 📊 **Dependency Visualization** - Mermaid diagrams showing module relationships  
- 🎯 **Multiple Verbosity Levels** - From clean minimal to detailed cross-referenced output
- ⚡ **Async Processing** - Fast concurrent processing of large codebases
- 🔍 **Type-Aware Linking** - Links type hints to their definitions automatically
- 🎭 **Async Pattern Detection** - Highlights factory methods, create_task calls, async context managers
- 📡 **Event System Mapping** - Tracks event publishers/subscribers with configurable patterns
- 🎨 **Obsidian Optimized** - Clean TOCs, wikilinks, frontmatter, and graph view integration
- ⚙️ **Highly Configurable** - Multi-layer configuration (CLI → Project → User → Defaults)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/luxia/mdvis.git
cd mdvis

# Install with uv (recommended)
uv sync
uv pip install -e .

# Or with pip
pip install -e .
```

### Basic Usage

```bash
# Generate documentation for your src directory
mdvis scan ./src

# Specify output directory and verbosity
mdvis scan ./src --output ./docs --verbosity detailed

# Use custom configuration
mdvis scan ./src --config ./my-config.yaml

# Watch mode for continuous updates
mdvis scan ./src --output ./docs --watch
```

### Advanced Examples

```bash
# Exclude test files and use minimal verbosity
mdvis scan ./src --verbosity minimal --exclude "**/test_*.py" --exclude "**/tests/**"

# Generate without event detection
mdvis scan ./src --no-events

# Include private methods and disable diagrams
mdvis scan ./src --include-private --no-diagrams

# Dry run to see what would be processed
mdvis scan ./src --dry-run
```

## 📋 CLI Reference

### Commands

- `mdvis scan <source>` - Generate documentation
- `mdvis init` - Create default configuration  
- `mdvis validate` - Validate configuration
- `mdvis clean <output>` - Remove generated files

### Options

- `--output, -o` - Output directory
- `--config, -c` - Configuration file path
- `--verbosity` - Detail level (minimal/standard/detailed)
- `--include-private/--no-private` - Include private methods
- `--events/--no-events` - Enable/disable event detection
- `--diagrams/--no-diagrams` - Enable/disable visualizations
- `--exclude` - Exclude patterns (can be used multiple times)
- `--watch, -w` - Watch for changes and regenerate
- `--dry-run` - Show what would be processed

## 📖 Documentation Structure

MDVis generates clean, navigable documentation that mirrors your source structure:

```
docs/
├── README.md                    # Project dashboard with overview
├── src/
│   ├── myproject/
│   │   ├── core/
│   │   │   ├── database.md      # Individual module docs
│   │   │   └── auth.md
│   │   └── utils/
│   │       └── helpers.md
└── _processing_status.md        # Generation statistics
```

### Generated Content

Each module gets comprehensive documentation:

- **Smart Cross-References** - `[[database#class-user]]` links directly to class definitions
- **Type Linking** - `param: YourCustomClass` automatically links to the class
- **Function Calls** - Shows where functions are called with links to definitions
- **Inheritance Trees** - Base classes link to their definitions
- **Import Resolution** - `from utils import helpers` links to `[[helpers]]`
- **Rich Frontmatter** - YAML metadata for Obsidian features
- **Clean TOCs** - Optimized for Obsidian's outline view

## ⚙️ Configuration

### Quick Setup

```bash
# Create a default configuration file
mdvis init --project-name "MyProject"

# Creates docs/mdvis.yaml with sensible defaults
```

### Configuration Layers

MDVis uses a priority-based configuration system:

1. **CLI Arguments** (highest priority)
2. **Project Config** (`./docs/mdvis.yaml`)  
3. **User Config** (`~/.config/mdvis/config.yaml`)
4. **Built-in Defaults** (lowest priority)

### Example Configuration

```yaml
# docs/mdvis.yaml
verbosity: standard

project:
  name: MyProject
  source_paths:
    - src
    - lib
  exclude_patterns:
    - '**/test_*.py'
    - '**/tests/**'
    - '**/__pycache__/**'

output:
  structure: mirror        # mirror source structure
  include_private: false   # exclude _private methods
  source_position: bottom  # source code at bottom

events:
  enabled: true
  auto_detect: true        # detect common patterns
  patterns: []             # custom regex patterns

analysis:
  detect_async_patterns: true
  detect_type_hints: true
  calculate_complexity: true

visualization:
  generate_dependency_graph: true
  generate_event_flow: true
```

## 🎯 Verbosity Levels

Control the detail level of generated documentation:

### Minimal
- Clean headers without anchor clutter
- Basic signatures and docstrings
- Essential cross-references only
- Perfect for quick overviews

### Standard (Default)
- Balanced detail with anchors
- Parameter information
- Function calls and inheritance
- Good for daily development

### Detailed  
- Complete cross-reference anchors
- Full complexity metrics
- Comprehensive call tracking
- Ideal for architectural analysis

## 📡 Event System Detection

MDVis automatically detects event patterns in your code:

### Built-in Patterns
- **Generic Dispatchers**: `dispatch_event()`, `emit()`, `publish()`
- **FastAPI Routes**: `@app.post()`, `@app.get()`
- **Django Signals**: `signal.send()`, `@receiver`

### Custom Patterns

```yaml
events:
  patterns:
    - name: my_events
      publisher_patterns:
        - "my_emit\\("
        - "fire_event\\("
      subscriber_patterns:
        - "on_\\w+\\("
        - "handle_\\w+\\("
      extract_event_type: '[\'"]([^\'\"]+)[\'"]'
```

## 🔍 Advanced Features

### Type-Aware Cross-Referencing

```python
async def process_user(user: User) -> UserResult:
    """Process a user and return results."""
    return user.process()
```

Generates:
- `user: [[models#class-user|User]]` - Links to User class definition
- `UserResult` - Links to return type definition
- `user.process()` - Links to User.process method

### Async Pattern Detection

Automatically highlights:
- **Factory Methods**: `@classmethod async def create()`
- **Task Creation**: `asyncio.create_task()`
- **Async Context**: `async with connection:`
- **Async Generators**: `async def stream_data():`

### Dependency Visualization

Generates Mermaid diagrams showing:
- Module import relationships
- Class inheritance hierarchies  
- Event flow networks
- Call dependency graphs

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by [Pydantic](https://pydantic.dev/) for configuration validation
- Generated documentation optimized for [Obsidian](https://obsidian.md/)

---

**Made with ❤️ for Python developers who want better documentation**