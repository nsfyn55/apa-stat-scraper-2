#!/bin/bash
# APA Stat Scraper zsh completion installation script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 APA Stat Scraper - Zsh Completion Installer${NC}"
echo "=================================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SCRIPT="$SCRIPT_DIR/_apa-stat-scraper"

# Check if completion script exists
if [[ ! -f "$COMPLETION_SCRIPT" ]]; then
    echo -e "${RED}❌ Error: Completion script not found at $COMPLETION_SCRIPT${NC}"
    exit 1
fi

# User-specific installation (recommended)
COMPLETION_DIR="$HOME/.zsh/completions"
echo -e "${BLUE}📁 Installing to user directory: $COMPLETION_DIR${NC}"

# Create completion directory
mkdir -p "$COMPLETION_DIR"

# Copy completion script
cp "$COMPLETION_SCRIPT" "$COMPLETION_DIR/"
chmod +x "$COMPLETION_DIR/_apa-stat-scraper"

# Add to .zshrc if not already present
if [[ -f "$HOME/.zshrc" ]]; then
    if ! grep -q "apa-stat-scraper" "$HOME/.zshrc"; then
        echo "" >> "$HOME/.zshrc"
        echo "# APA Stat Scraper completion" >> "$HOME/.zshrc"
        echo "if [[ -d ~/.zsh/completions ]]; then" >> "$HOME/.zshrc"
        echo "    fpath=(~/.zsh/completions \$fpath)" >> "$HOME/.zshrc"
        echo "fi" >> "$HOME/.zshrc"
        echo -e "${GREEN}✅ Added completion loading to ~/.zshrc${NC}"
    else
        echo -e "${YELLOW}⚠️  Completion loading already present in ~/.zshrc${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  ~/.zshrc not found. You'll need to add completion loading manually.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Reload your zsh configuration:"
echo "   source ~/.zshrc"
echo ""
echo "2. Or restart your terminal"
echo ""
echo -e "${YELLOW}🧪 Test the completion:${NC}"
echo "1. Type: apa-stat-scraper <TAB>"
echo "   Should show: login  verify-session  clear-state  extract-player"
echo ""
echo "2. Type: apa-stat-scraper extract-player <TAB>"
echo "   Should show: --team-id  --member-id  --url  --output  --format  --headless  --no-terminal"
echo ""
echo "3. Type: apa-stat-scraper extract-player --format <TAB>"
echo "   Should show: json  csv"
