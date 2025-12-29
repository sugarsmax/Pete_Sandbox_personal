#!/Users/maxfiep/.python-venvs/pdms-shared/bin/python3
"""
Sync projects.json to projects.js for local preview

This script reads projects.json and generates projects.js so the showcase
can be previewed locally without a web server.

Usage:
    ./sync_projects_20251124.py
"""

import json
from pathlib import Path

def sync_projects():
    script_dir = Path(__file__).parent
    json_path = script_dir / 'projects.json'
    js_path = script_dir / 'projects.js'
    
    # Read JSON
    with open(json_path, 'r') as f:
        projects = json.load(f)
    
    # Generate JS file
    js_content = f"""// Auto-generated from projects.json
// This file allows local preview without a server
const PROJECTS_DATA = {json.dumps(projects, indent=4)};
"""
    
    with open(js_path, 'w') as f:
        f.write(js_content)
    
    print(f"✓ Synced {len(projects)} projects from projects.json to projects.js")
    print(f"  You can now open index.html directly in your browser!")

if __name__ == '__main__':
    sync_projects()

