import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from countmytokens.main import TokenCounter


@pytest.fixture
def token_counter(tmp_path: Path) -> TokenCounter:
    # Create a temporary directory and some files for testing
    (tmp_path / "file1.py").write_text("print('Hello, world!')")
    (tmp_path / "file2.py").write_text("def foo():\n    return 42")
    (tmp_path / "binary_file").write_bytes(b"\x00\x01\x02\x03")
    return TokenCounter(tmp_path)


@pytest.mark.asyncio
async def test_count_tokens_in_file(token_counter: TokenCounter) -> None:
    file_path = token_counter.path / "file1.py"
    token_count = await token_counter.count_tokens_in_file(file_path)
    assert token_count > 0


@pytest.mark.asyncio
async def test_count_tokens(token_counter: TokenCounter) -> None:
    file_tokens = await token_counter.count_tokens(skip_binary=True)
    assert len(file_tokens) == 2  # Only the two .py files should be counted
    assert all(tokens > 0 for tokens in file_tokens.values())


def test_generate_csv_report(token_counter: TokenCounter, tmp_path: Path) -> None:
    file_tokens = {"file1.py": 5, "file2.py": 10}
    output_file = tmp_path / "report.csv"
    token_counter.generate_csv_report(file_tokens, output_file)
    assert output_file.exists()
    with output_file.open() as f:
        lines = f.readlines()
    assert len(lines) == 3  # Header + 2 file entries


def test_generate_tree_report(
    token_counter: TokenCounter, capsys: pytest.CaptureFixture[str]
) -> None:
    file_tokens = {"file1.py": 5, "file2.py": 10}
    token_counter.generate_tree_report(file_tokens)
    captured = capsys.readouterr()
    assert "Root: 15 tokens" in captured.out
    assert "file1.py: 5 tokens" in captured.out
    assert "file2.py: 10 tokens" in captured.out
