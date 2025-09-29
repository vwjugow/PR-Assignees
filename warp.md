# Warp Terminal Documentation

## Overview

Warp is a modern, Rust-based terminal built for speed and productivity. It reimagines the terminal experience with features like AI assistance, collaborative workflows, and a modern interface.

## Key Features

### 🚀 Performance
- Built in Rust for maximum speed and efficiency
- GPU-accelerated rendering
- Fast startup times and responsive interface

### 🤖 AI Integration
- AI command suggestions and explanations
- Natural language to command translation
- Contextual help and error explanations
- Agent Mode for complex task automation

### 📝 Modern Text Editing
- Block-based command editing
- Multi-cursor support
- Rich text formatting
- Syntax highlighting for commands

### 🔄 Collaborative Features
- Share terminal sessions with team members
- Live collaboration on commands
- Session recording and playback

## Installation

### macOS
```bash
brew install --cask warp
```

Or download directly from [warp.dev](https://warp.dev)

### Linux
```bash
# Using package managers
sudo apt install warp-terminal  # Ubuntu/Debian
sudo dnf install warp-terminal  # Fedora
```

## Getting Started

### Basic Navigation
- **New tab**: `Cmd + T` (macOS) / `Ctrl + Shift + T` (Linux)
- **Close tab**: `Cmd + W` (macOS) / `Ctrl + Shift + W` (Linux)
- **Switch tabs**: `Cmd + 1-9` (macOS) / `Ctrl + 1-9` (Linux)
- **Split pane**: `Cmd + D` (macOS) / `Ctrl + Shift + D` (Linux)

### Command Blocks
Commands in Warp are organized into blocks that you can:
- Edit independently
- Copy and share
- Navigate between using arrow keys
- Execute with `Enter`

### AI Features

#### AI Command Search
- Press `Ctrl + Shift + R` to open AI command search
- Type natural language descriptions
- Get command suggestions with explanations

#### Agent Mode
- Access via `Cmd + Shift + A` (macOS) or `Ctrl + Shift + A` (Linux)
- Perform complex multi-step tasks
- Automated error handling and corrections

## Configuration

### Settings Location
- **macOS**: `~/.warp/`
- **Linux**: `~/.config/warp/`

### Custom Themes
```json
{
  "theme": {
    "name": "Custom",
    "background": "#1e1e1e",
    "foreground": "#ffffff",
    "cursor": "#00ff00"
  }
}
```

### Key Bindings
Edit keybindings in `Settings > Keyboard Shortcuts`

Common customizations:
```json
{
  "keybindings": {
    "copy": "Cmd+C",
    "paste": "Cmd+V",
    "clear_screen": "Cmd+K",
    "new_tab": "Cmd+T"
  }
}
```

## Workflows and Features

### Workflow Management
- Save frequently used command sequences
- Create custom workflows for project-specific tasks
- Share workflows with team members

### Session Management
- Automatically save and restore sessions
- Named sessions for different projects
- Session templates for quick setup

### Git Integration
- Visual git status indicators
- Inline diff viewing
- Branch switching with autocomplete

## Productivity Tips

### 1. Command History with Context
- Use `Ctrl + R` for intelligent command search
- History is contextual to your current directory
- Filter by command type or frequency

### 2. Smart Autocomplete
- Tab completion with rich previews
- File and directory suggestions with icons
- Command flag documentation inline

### 3. Custom Aliases and Functions
```bash
# Add to your shell profile
alias ll='ls -la'
alias gs='git status'
alias gp='git push origin'

# Custom functions
mkcd() {
  mkdir -p "$1" && cd "$1"
}
```

### 4. Environment Variables
```bash
# Quick environment setup
export EDITOR=vim
export PATH="$HOME/bin:$PATH"
export PYTHON_PATH="$HOME/.local/bin"
```

## Advanced Features

### SSH Integration
- Visual SSH connection management
- Saved connection profiles
- Key management interface

### Docker Support
- Container status indicators
- Easy container shell access
- Docker command suggestions

### Cloud Integration
- AWS CLI integration
- Kubernetes context switching
- Google Cloud Platform support

## Troubleshooting

### Common Issues

#### Slow Performance
1. Check GPU acceleration settings
2. Reduce history size in settings
3. Disable unnecessary plugins

#### Font Issues
1. Install recommended fonts (Fira Code, SF Mono)
2. Check font rendering settings
3. Adjust font size and spacing

#### Shell Integration
```bash
# Add to ~/.zshrc or ~/.bashrc
eval "$(warp --shell-integration)"
```

### Getting Help
- In-terminal help: `warp --help`
- Community: [Warp Discord](https://discord.gg/warp)
- Documentation: [docs.warp.dev](https://docs.warp.dev)

## Keyboard Shortcuts Reference

### General
- `Cmd/Ctrl + ,`: Settings
- `Cmd/Ctrl + K`: Clear screen
- `Cmd/Ctrl + L`: Clear current line
- `Cmd/Ctrl + U`: Clear line to beginning

### Navigation
- `Cmd/Ctrl + ↑/↓`: Navigate command blocks
- `Cmd/Ctrl + ←/→`: Move between panes
- `Cmd/Ctrl + Shift + ↑/↓`: Select blocks

### Editing
- `Cmd/Ctrl + A`: Select all in current block
- `Cmd/Ctrl + C`: Copy selection
- `Cmd/Ctrl + V`: Paste
- `Cmd/Ctrl + Z`: Undo

## Integration Examples

### VS Code Integration
```bash
# Open current directory in VS Code
code .

# Open specific file
code filename.txt
```

### Git Workflows
```bash
# Common git commands with Warp enhancements
git status          # Shows visual indicators
git log --oneline   # Enhanced formatting
git diff           # Syntax highlighted diffs
```

### Development Setup
```bash
# Node.js project setup
npm init -y
npm install express
npm run dev

# Python project setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Best Practices

1. **Use Workflows**: Save repetitive command sequences
2. **Leverage AI**: Ask for help with complex commands
3. **Customize Themes**: Choose themes that reduce eye strain
4. **Organize Sessions**: Use named sessions for different projects
5. **Share Knowledge**: Use collaborative features for team learning

## Resources

- **Official Website**: [warp.dev](https://warp.dev)
- **Documentation**: [docs.warp.dev](https://docs.warp.dev)
- **GitHub**: [github.com/warpdotdev/warp](https://github.com/warpdotdev/warp)
- **Community**: [Discord](https://discord.gg/warp) | [Reddit](https://reddit.com/r/warp)
- **Blog**: [warp.dev/blog](https://warp.dev/blog)

## Version Information

This documentation covers Warp version 0.2024.x and later. Features may vary between versions.

---

*Last updated: September 2024*
