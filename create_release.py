#!/usr/bin/env python3
"""
Create a GitHub release with automated changelog
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def get_version():
    """Get current version from git tags"""
    stdout, stderr, code = run_command("git describe --tags --abbrev=0")
    if code == 0 and stdout:
        # Increment patch version
        version_parts = stdout.lstrip('v').split('.')
        if len(version_parts) == 3:
            version_parts[2] = str(int(version_parts[2]) + 1)
            return '.'.join(version_parts)
    return "1.0.0"

def get_changelog():
    """Generate changelog from recent commits"""
    stdout, stderr, code = run_command("git log --oneline -10")
    if code == 0:
        lines = stdout.split('\n')
        changelog = "## Recent Changes\n\n"
        for line in lines:
            if line.strip():
                changelog += f"- {line}\n"
        return changelog
    return "## Recent Changes\n\n- Initial release"

def create_release():
    """Create a GitHub release"""
    version = get_version()
    tag = f"v{version}"
    
    print(f"🚀 Creating release {tag}")
    
    # Create and push tag
    changelog = get_changelog()
    
    # Create tag
    run_command(f"git tag -a {tag} -m 'Release {tag}'")
    run_command(f"git push origin {tag}")
    
    print(f"✅ Created and pushed tag {tag}")
    print(f"📝 Changelog:\n{changelog}")
    
    # Instructions for manual release creation
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("="*60)
    print("1. Go to: https://github.com/PeachyBuffalo/MARABTCTracking/releases")
    print("2. Click 'Create a new release'")
    print(f"3. Select tag: {tag}")
    print(f"4. Release title: Bitcoin Tracker {tag}")
    print("5. Copy the changelog above into the description")
    print("6. Check 'Set as the latest release'")
    print("7. Click 'Publish release'")
    print("\n🎉 Your release will be live and downloadable!")

if __name__ == "__main__":
    create_release()
