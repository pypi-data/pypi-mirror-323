# countmytokens

Ever wondered how big in tokens are your codebase? No? Well, too bad, because `countmytokens` is here to count them anyway. 

## Features

- **Token Counting**: Counts tokens in all your files.
- **Binary File Skipping**: Skipps binary files because counting tokens in those would be just silly.
- **CSV Reports**: Generates CSV reports so you can pretend to analyze the data.
- **Tree Reports**: Creates tree reports to visualize the token hierarchy.
- **Git Integration**: If it detects a Git repository, it uses `ls-files` to respect `.gitignore` and other exclude settings.


## Installation

```code
pip install countmytokens
```

For users who prefer to use `pipx`, you can install it globally:

```bash
pipx install countmytokens
```

If you are using `uv`, you can install it with:

```bash
uv tool install countmytokens
```

## Usage
```code
countmytokens /path/to/your/code/project
```

Options

- *--exclude**:
Paths to exclude. Because some files just don't deserve to be counted.
- *--include-binary**:
Include binary files in the token count. If you're into that sort of thing.
- *--max-files**:
Maximum concurrent file operations. Default is 100. Because why not?
- *--report**:
Choose your report format: `lines` or `tree`
- **--output**:
Output file for CSV report. Default is `token_report.csv`. Creative, huh?
- **--verbose**:
Increase output verbosity

### Example
```code
countmytokens /path/to/your/code/project --exclude venv --report tree --verbose
```

## Contributing
Feel free to contribute. Or don't. It's your life.

LICENSE
MIT License. Because sharing is caring.
