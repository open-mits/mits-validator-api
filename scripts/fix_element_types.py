#!/usr/bin/env python3
"""
Script to fix ET.Element type hints to use Element from xml.etree.ElementTree.
"""

from pathlib import Path

def fix_file(file_path: Path) -> bool:
    """Fix Element type hints in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        
        # Add Element import if not present and ET.Element is used
        if "ET.Element" in content and "from xml.etree.ElementTree import Element" not in content:
            # Find the imports section and add Element import
            lines = content.split("\n")
            import_added = False
            for i, line in enumerate(lines):
                if line.startswith("from defusedxml import ElementTree as ET"):
                    # Add the Element import before defusedxml import
                    lines.insert(i, "from xml.etree.ElementTree import Element")
                    import_added = True
                    break
            
            if import_added:
                content = "\n".join(lines)
        
        # Replace all ET.Element type hints with Element
        content = content.replace(": ET.Element", ": Element")
        content = content.replace("-> ET.Element", "-> Element")
        content = content.replace("[ET.Element]", "[Element]")
        content = content.replace("(ET.Element)", "(Element)")
        content = content.replace(" ET.Element,", " Element,")
        content = content.replace(" ET.Element)", " Element)")
        
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix all validator files."""
    base_path = Path(__file__).parent.parent
    validators_path = base_path / "app" / "validators" / "mits"
    
    files_updated = 0
    
    # Update all Python files in validators
    for py_file in validators_path.glob("*.py"):
        if py_file.name != "__init__.py":
            if fix_file(py_file):
                files_updated += 1
                print(f"Fixed: {py_file.name}")
    
    print(f"\nTotal files updated: {files_updated}")


if __name__ == "__main__":
    main()

