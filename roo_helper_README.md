# Roo Helper for VSCode

This utility script helps work around issues with Roo Code operations in VSCode, particularly the `apply-diff` operation which often fails with similarity score errors.

## Problem

When using Roo Code in VSCode, you might encounter these issues:
- `apply-diff` operations fail with "No sufficiently similar match found" errors
- Insertions happen in the wrong location
- No visible errors appear, but nothing is changed

## Solution

This helper script provides utilities to:
1. Convert `apply-diff` operations to `search_and_replace` operations
2. Format `insert_content` operations correctly
3. Create properly formatted operations for common file modifications

## Installation

1. Save the `roo_helper.py` script to your project directory
2. Make it executable: `chmod +x roo_helper.py`

## Usage

### Convert apply-diff to search_and_replace

If you have an `apply-diff` operation that's failing, you can convert it to a `search_and_replace` operation:

```bash
python roo_helper.py convert-diff-to-search your_diff_file.xml
```

This will output a `search_and_replace` operation that you can use instead.

### Format insert_content operations

If you're having issues with `insert_content` operations, you can format them correctly:

```bash
python roo_helper.py format-insert your_insert_file.xml
```

### Create search_and_replace operations

You can create a properly formatted `search_and_replace` operation:

```bash
python roo_helper.py create-search file.py "def old_function():" "def new_function():"
```

### Create insert_content operations

You can create a properly formatted `insert_content` operation:

```bash
python roo_helper.py create-insert file.py 10 "def new_function():\n    return True"
```

## Examples

### Example 1: Convert an apply-diff operation

1. Save your apply-diff operation to a file:
```xml
<apply_diff>
<path>file.py</path>
<diff>
<<<<<<< SEARCH
:start_line:1
:end_line:3
-------
def old_function():
    return False
=======
def new_function():
    return True
>>>>>>> REPLACE
</diff>
</apply_diff>
```

2. Convert it to a search_and_replace operation:
```bash
python roo_helper.py convert-diff-to-search apply_diff.xml
```

3. Use the output in Roo Code:
```xml
<search_and_replace>
<path>file.py</path>
<operations>
[
  {
    "search": "def old_function():\n    return False",
    "replace": "def new_function():\n    return True",
    "use_regex": false
  }
]
</operations>
</search_and_replace>
```

### Example 2: Create an insert_content operation

```bash
python roo_helper.py create-insert file.py 10 "def new_function():\n    return True"
```

Output:
```xml
<insert_content>
<path>file.py</path>
<operations>
[
  {
    "start_line": 10,
    "content": "def new_function():\n    return True"
  }
]
</operations>
</insert_content>
```

## Troubleshooting

If you're still having issues:

1. Check VSCode settings:
   - Ensure "Files: EOL" setting is set to "\n" (LF) for consistency
   - Disable any auto-formatting extensions that might interfere

2. Check the VSCode Developer Tools console for any error messages:
   - Open Developer Tools (`Help > Toggle Developer Tools`)
   - Check Console tab for any errors related to Roo or file operations

3. Try using the `--output` flag to save the operation to a file, then copy-paste it into Roo Code:
   ```bash
   python roo_helper.py convert-diff-to-search apply_diff.xml --output search_replace.xml
   ```

## Contributing

Feel free to enhance this script with additional features or improvements!