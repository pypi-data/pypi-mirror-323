import argparse
import asyncio
import csv
import logging
import sys
from pathlib import Path

import aiofiles
import tiktoken  # type: ignore
import treelib  # type: ignore
from git import InvalidGitRepositoryError, Repo


def setup_logging(verbosity: int) -> logging.Logger:
    log_levels = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    logging.basicConfig(level=log_levels.get(verbosity, logging.WARNING), format="%(message)s")
    return logging.getLogger(__name__)


class TokenCounter:
    def __init__(
        self, path: Path, encoding_name: str = "cl100k_base", max_concurrent_files: int = 100
    ) -> None:
        self.path = path.resolve()
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.semaphore = asyncio.Semaphore(max_concurrent_files)

    def _is_binary(self, file_path: Path) -> bool:
        try:
            with file_path.open("rb") as f:
                chunk = f.read(1024)
                return any(byte < 32 and byte not in (9, 10, 13) for byte in chunk)
        except Exception:
            return True

    def _get_files(self, exclude_paths: list[Path]) -> list[Path]:

        try:
            repo = Repo(self.path)
            files = [self.path / file for file in repo.git.ls_files().split("\n") if file]
        except InvalidGitRepositoryError:
            files = list(self.path.rglob("*"))

        return [
            f
            for f in files
            if f.is_file()
            and not any(f.resolve().is_relative_to(exclude) for exclude in exclude_paths)
        ]

    async def count_tokens_in_file(self, file_path: Path, skip_binary: bool = True) -> int:
        if skip_binary and self._is_binary(file_path):
            return 0

        async with self.semaphore, aiofiles.open(file_path) as f:
            content = await f.read()
            tokens = self.encoding.encode(content)
            return len(tokens)

    async def count_tokens(
        self, exclude_paths: list[str] | None = None, skip_binary: bool = True
    ) -> dict[str, int]:
        exclude_paths_resolved = [Path(p).resolve() for p in (exclude_paths or [])]
        files = self._get_files(exclude_paths_resolved)

        file_tokens = {}
        for file in files:
            tokens = await self.count_tokens_in_file(file, skip_binary)
            if tokens > 0:
                file_tokens[str(file.relative_to(self.path))] = tokens

        return file_tokens

    def generate_csv_report(self, file_tokens: dict[str, int], output_file: Path) -> None:
        with output_file.open("w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["File Path", "Token Count"])
            for path, tokens in sorted(file_tokens.items(), key=lambda x: x[1], reverse=True):
                writer.writerow([path, tokens])

    def generate_tree_report(self, file_tokens: dict[str, int]) -> None:
        """
        Generate a tree report of token counts.

        Args:
            file_tokens (Dict[str, int]): Dictionary mapping file paths to token counts.
        """
        tree = treelib.Tree()
        tree.create_node("Root", "root", data=0)

        def add_to_tree(path: str, tokens: int) -> None:
            parts = Path(path).parts
            for i, part in enumerate(parts):
                current_path = Path(*parts[: i + 1])
                parent_path = Path(*parts[:i]) if i > 0 else Path("root")

                if not tree.contains(str(parent_path)):
                    tree.create_node(str(parent_path), str(parent_path), parent="root", data=0)

                if not tree.contains(str(current_path)):
                    tree.create_node(part, str(current_path), parent=str(parent_path), data=0)

                current_node = tree.get_node(str(current_path))
                current_node.data += tokens

        for path, tokens in file_tokens.items():
            add_to_tree(path, tokens)
            tree.get_node("root").data += tokens  # Update root with total tokens

        def print_tree(node_id: str, depth: int = 0) -> None:
            node = tree.get_node(node_id)
            indent = "  " * depth
            sys.stdout.write(f"{indent}{node.tag}: {node.data} tokens\n")

            for child in tree.children(node_id):
                print_tree(child.identifier, depth + 1)

        print_tree("root")


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Count tokens in files or Git repository.")
    parser.add_argument("path", type=Path, help="Path to directory or Git repository")
    parser.add_argument("--exclude", type=str, nargs="*", default=[], help="Paths to exclude")
    parser.add_argument(
        "--include-binary", action="store_true", help="Include binary files in token count"
    )
    parser.add_argument(
        "--max-files", type=int, default=100, help="Maximum concurrent file operations"
    )
    parser.add_argument("--report", choices=["lines", "tree"], help="Report output format")
    parser.add_argument(
        "--output", type=Path, default=Path("token_report.csv"), help="Output file for CSV report"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase output verbosity"
    )

    args = parser.parse_args()

    logger = setup_logging(args.verbose)

    if not args.path.exists():
        logger.error("Path '%s' does not exist.", args.path)
        sys.exit(1)

    token_counter = TokenCounter(args.path, max_concurrent_files=args.max_files)
    file_tokens = await token_counter.count_tokens(
        exclude_paths=args.exclude, skip_binary=not args.include_binary
    )

    total_tokens = sum(file_tokens.values())
    logger.info("Total tokens: %d", total_tokens)
    sys.stdout.write(f"Total tokens: {total_tokens}\n")

    if args.report == "lines":
        token_counter.generate_csv_report(file_tokens, args.output)
    elif args.report == "tree":
        token_counter.generate_tree_report(file_tokens)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
