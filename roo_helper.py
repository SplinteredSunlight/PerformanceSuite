#!/usr/bin/env python3
"""
Roo Helper - Utilities for working with Roo Code in VSCode

This script provides utilities to work around issues with Roo Code operations in VSCode:
1. Convert apply-diff operations to search_and_replace operations
2. Format insert_content operations correctly
3. Provide a wrapper for common file operations

Usage:
    python roo_helper.py convert-diff-to-search <diff_file> [--output <output_file>]
    python roo_helper.py format-insert <insert_file> [--output <output_file>]
    python roo_helper.py create-search <file_path> <search_text> <replace_text> [--output <output_file>]
    python roo_helper.py create-insert <file_path> <line_number> <content> [--output <output_file>]
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Tuple, Union


def parse_apply_diff(diff_content: str) -> Tuple[Optional[str], Optional[List[Dict]]]:
    """
    Parse an apply-diff operation and convert it to search_and_replace operations.
    
    Args:
        diff_content: The content of the apply-diff operation
        
    Returns:
        Tuple of (file_path, operations list for search_and_replace)
    """
    # Extract path from apply-diff
    path_match = re.search(r'<path>(.*?)</path>', diff_content)
    if not path_match:
        print("Error: Could not find path in apply-diff content")
        return None, None
    
    path = path_match.group(1)
    
    # Extract diff content
    diff_match = re.search(r'<diff>(.*?)</diff>', diff_content, re.DOTALL)
    if not diff_match:
        print("Error: Could not find diff content in apply-diff")
        return None, None
    
    diff = diff_match.group(1)
    
    # Parse diff blocks
    operations = []
    
    # Split by diff blocks
    blocks = re.findall(r'<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE', diff, re.DOTALL)
    
    for search_block, replace_block in blocks:
        # Extract search content (skip the start_line and end_line metadata)
        search_content_match = re.search(r':start_line:\d+\n:end_line:\d+\n-------\n(.*)', search_block, re.DOTALL)
        if not search_content_match:
            print("Warning: Could not parse search content in a block, skipping")
            continue
        
        search_content = search_content_match.group(1)
        replace_content = replace_block.strip()
        
        operations.append({
            "search": search_content,
            "replace": replace_content,
            "use_regex": False
        })
    
    return path, operations


def parse_insert_content(insert_content: str) -> Tuple[Optional[str], Optional[List[Dict]]]:
    """
    Parse an insert-content operation and format it correctly.
    
    Args:
        insert_content: The content of the insert-content operation
        
    Returns:
        Tuple of (file_path, operations list for insert_content)
    """
    # Extract path from insert-content
    path_match = re.search(r'<path>(.*?)</path>', insert_content)
    if not path_match:
        print("Error: Could not find path in insert-content")
        return None, None
    
    path = path_match.group(1)
    
    # Extract operations content
    operations_match = re.search(r'<operations>(.*?)</operations>', insert_content, re.DOTALL)
    if not operations_match:
        print("Error: Could not find operations in insert-content")
        return None, None
    
    operations_text = operations_match.group(1).strip()
    
    # Check if operations is already in JSON format
    if operations_text.startswith('[') and operations_text.endswith(']'):
        try:
            operations = json.loads(operations_text)
            return path, operations
        except json.JSONDecodeError:
            print("Warning: Operations is not valid JSON, trying to parse as YAML")
    
    # Try to parse as YAML-style operations
    operations = []
    
    # Match YAML-style operations
    yaml_ops = re.findall(r'- start_line: (\d+)\s+content: \|?\s+(.*?)(?=\n- start_line:|\Z)', 
                         operations_text, re.DOTALL)
    
    for line_num, content in yaml_ops:
        operations.append({
            "start_line": int(line_num),
            "content": content.strip()
        })
    
    if not operations:
        print("Error: Could not parse operations in insert-content")
        return None, None
    
    return path, operations


def convert_to_search_and_replace(path: str, operations: List[Dict]) -> str:
    """
    Convert operations to a search_and_replace XML format.
    
    Args:
        path: File path
        operations: List of search/replace operations
        
    Returns:
        Formatted search_and_replace XML
    """
    operations_json = json.dumps(operations, indent=2)
    
    return f"""<search_and_replace>
<path>{path}</path>
<operations>
{operations_json}
</operations>
</search_and_replace>"""


def convert_to_insert_content(path: str, operations: List[Dict]) -> str:
    """
    Convert operations to an insert_content XML format.
    
    Args:
        path: File path
        operations: List of insert operations
        
    Returns:
        Formatted insert_content XML
    """
    operations_json = json.dumps(operations, indent=2)
    
    return f"""<insert_content>
<path>{path}</path>
<operations>
{operations_json}
</operations>
</insert_content>"""


def create_search_replace(path: str, search_text: str, replace_text: str) -> str:
    """
    Create a search_and_replace operation.
    
    Args:
        path: File path
        search_text: Text to search for
        replace_text: Text to replace with
        
    Returns:
        Formatted search_and_replace XML
    """
    operations = [{
        "search": search_text,
        "replace": replace_text,
        "use_regex": False
    }]
    
    return convert_to_search_and_replace(path, operations)


def create_insert_content(path: str, line_number: int, content: str) -> str:
    """
    Create an insert_content operation.
    
    Args:
        path: File path
        line_number: Line number to insert at
        content: Content to insert
        
    Returns:
        Formatted insert_content XML
    """
    operations = [{
        "start_line": line_number,
        "content": content
    }]
    
    return convert_to_insert_content(path, operations)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Roo Helper Tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Convert diff to search command
    convert_parser = subparsers.add_parser("convert-diff-to-search", 
                                          help="Convert apply-diff to search_and_replace")
    convert_parser.add_argument("diff_file", help="File containing apply-diff XML")
    convert_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    # Format insert content command
    format_insert_parser = subparsers.add_parser("format-insert",
                                               help="Format insert_content operations correctly")
    format_insert_parser.add_argument("insert_file", help="File containing insert_content XML")
    format_insert_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    # Create search and replace command
    create_search_parser = subparsers.add_parser("create-search",
                                               help="Create a search_and_replace operation")
    create_search_parser.add_argument("file_path", help="File path to modify")
    create_search_parser.add_argument("search_text", help="Text to search for")
    create_search_parser.add_argument("replace_text", help="Text to replace with")
    create_search_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    # Create insert content command
    create_insert_parser = subparsers.add_parser("create-insert",
                                               help="Create an insert_content operation")
    create_insert_parser.add_argument("file_path", help="File path to modify")
    create_insert_parser.add_argument("line_number", type=int, help="Line number to insert at")
    create_insert_parser.add_argument("content", help="Content to insert")
    create_insert_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    try:
        result = None
        
        if args.command == "convert-diff-to-search":
            with open(args.diff_file, 'r') as f:
                diff_content = f.read()
            
            path, operations = parse_apply_diff(diff_content)
            if not path or not operations:
                sys.exit(1)
            
            result = convert_to_search_and_replace(path, operations)
            
        elif args.command == "format-insert":
            with open(args.insert_file, 'r') as f:
                insert_content = f.read()
            
            path, operations = parse_insert_content(insert_content)
            if not path or not operations:
                sys.exit(1)
            
            result = convert_to_insert_content(path, operations)
            
        elif args.command == "create-search":
            result = create_search_replace(args.file_path, args.search_text, args.replace_text)
            
        elif args.command == "create-insert":
            result = create_insert_content(args.file_path, args.line_number, args.content)
            
        else:
            print("Please specify a command. Use --help for more information.")
            sys.exit(1)
        
        if result:
            if hasattr(args, 'output') and args.output:
                with open(args.output, 'w') as f:
                    f.write(result)
                print(f"Output written to {args.output}")
            else:
                print(result)
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()