#! /bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        echo "Installing required packages..."
        python3 -m pip install --upgrade pip build twine
    fi
}

# Check for required commands
check_command "python3"
check_command "pip"

# Get current version from pyproject.toml
current_version=$(grep "version = " ../pyproject.toml | cut -d'"' -f2)
echo -e "${BLUE}Current version:${NC} $current_version"

# Ask which version number to update
echo -e "\n${GREEN}Which version number would you like to update?${NC}"
echo "1) Major (x.0.0)"
echo "2) Minor (0.x.0)"
echo "3) Patch (0.0.x)"
read -p "Enter choice [1-3]: " version_choice

# Split current version
IFS='.' read -r major minor patch <<< "$current_version"

# Update version based on choice
case $version_choice in
    1)
        major=$((major + 1))
        minor=0
        patch=0
        ;;
    2)
        minor=$((minor + 1))
        patch=0
        ;;
    3)
        patch=$((patch + 1))
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

new_version="$major.$minor.$patch"
echo -e "${BLUE}New version will be:${NC} $new_version"

# Confirm update
read -p "Continue with update? [y/N] " confirm
if [[ $confirm != [yY] ]]; then
    echo "Cancelled. Exiting."
    exit 1
fi

# Move to root directory
cd ..

# Clean any existing builds
echo -e "\n${GREEN}Cleaning old build artifacts...${NC}"
rm -rf build/ dist/ *.egg-info/

# Update version in pyproject.toml
sed -i '' "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml

# Update version in version.yaml
echo "version: \"$new_version\"" > src/dbforge/version.yaml

# Check if README.md exists
if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: README.md not found${NC}"
    exit 1
fi

# Build the package
echo -e "\n${GREEN}Building package...${NC}"
python3 -m build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo -e "${RED}Build failed! No dist directory created${NC}"
    exit 1
fi

# Upload to PyPI
echo -e "\n${GREEN}Uploading to PyPI...${NC}"
if python3 -m twine upload --config-file scripts/.pypirc dist/*; then
    echo -e "\n${GREEN}Success!${NC} Version $new_version has been uploaded to PyPI"
else
    echo -e "\n${RED}Upload failed!${NC}"
    exit 1
fi

# Clean up
echo -e "\n${GREEN}Cleaning up build artifacts...${NC}"
rm -rf build/ dist/ *.egg-info/

echo -e "\n${GREEN}All done!${NC} You can now install version $new_version with: pip install dbforge==$new_version" 