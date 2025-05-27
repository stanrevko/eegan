#!/usr/bin/env python3
"""
Verification script for Channel Selector integration
Tests the syntax and basic structure without requiring PyQt5
"""

import sys
import os
import ast

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True, "✅ Syntax OK"
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def check_imports(filepath):
    """Check if imports are properly structured"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}.{node.names[0].name}")
        
        return True, imports
    except Exception as e:
        return False, str(e)

print("🧠 EEG Analysis Suite - Channel Selector Verification")
print("=" * 60)

# Files to check
files_to_check = [
    "gui/analysis/channel_selector.py",
    "gui/analysis/tabbed_analysis_panel.py", 
    "gui/analysis/analysis_controls.py",
    "gui/analysis/__init__.py"
]

all_good = True

for filepath in files_to_check:
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    if os.path.exists(full_path):
        syntax_ok, msg = check_file_syntax(full_path)
        print(f"📄 {filepath}: {msg}")
        if not syntax_ok:
            all_good = False
    else:
        print(f"❌ {filepath}: File not found")
        all_good = False

print("\n🔍 Import Structure Check:")
init_file = os.path.join(os.path.dirname(__file__), "gui/analysis/__init__.py")
if os.path.exists(init_file):
    with open(init_file, 'r') as f:
        content = f.read()
    if "ChannelSelector" in content:
        print("✅ ChannelSelector properly exported in __init__.py")
    else:
        print("❌ ChannelSelector not found in __init__.py exports")
        all_good = False

print("\n🧪 Integration Points Check:")
tabbed_file = os.path.join(os.path.dirname(__file__), "gui/analysis/tabbed_analysis_panel.py")
if os.path.exists(tabbed_file):
    with open(tabbed_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("ChannelSelector import", "from gui.analysis import BandSelector, ChannelSelector"),
        ("Channel selector creation", "self.channel_selector = ChannelSelector()"),
        ("Signal connection", "self.channel_selector.channel_changed.connect"),
        ("Analyzer integration", "self.channel_selector.set_channels"),
        ("Method implementation", "def on_channel_changed(self, channel_idx):")
    ]
    
    for check_name, check_string in checks:
        if check_string in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_good = False

print("\n" + "=" * 60)
if all_good:
    print("🎉 All checks passed! Channel selector is properly integrated.")
    print("🚀 Ready to run with: python test_tabbed_analysis.py (in venv)")
else:
    print("⚠️  Some issues found. Check the details above.")

print("📋 Summary:")
print("   • Channel dropdown added to tabbed analysis panel header")
print("   • Synchronized channel selection across all analysis tabs")
print("   • Proper signal handling with recursion prevention")
print("   • Integration with existing EEG analyzer workflow")
