#!/usr/bin/env python3
import argparse
import json
import pathlib
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate rust-project.json from GN target sources."
    )
    parser.add_argument(
        "--out-dir",
        default="out",
        help="GN output directory used by gn gen (default: out)",
    )
    parser.add_argument(
        "--target",
        default="//:hello",
        help="GN target label to inspect (default: //:hello)",
    )
    parser.add_argument(
        "--edition",
        default="2021",
        help="Rust edition to write into rust-project.json (default: 2021)",
    )
    parser.add_argument(
        "--output",
        default="rust-project.json",
        help="Output rust-project.json path (default: rust-project.json)",
    )
    return parser.parse_args()


def run_gn_desc(out_dir: str, target: str) -> dict:
    command = ["gn", "desc", out_dir, target, "sources", "--format=json"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        print("error: gn not found in PATH", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as error:
        print("error: gn desc failed", file=sys.stderr)
        if error.stderr:
            print(error.stderr.strip(), file=sys.stderr)
        sys.exit(error.returncode or 1)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        print(f"error: failed to parse gn json output: {error}", file=sys.stderr)
        sys.exit(1)


def normalize_gn_source_path(path: str) -> str:
    if path.startswith("//"):
        return path[2:]
    return path


def pick_root_module(rs_sources: list[str]) -> str:
    for candidate in rs_sources:
        if candidate.endswith("main.rs"):
            return candidate
    for candidate in rs_sources:
        if candidate.endswith("lib.rs"):
            return candidate
    return rs_sources[0]


def main() -> None:
    args = parse_args()
    gn_data = run_gn_desc(args.out_dir, args.target)

    if args.target not in gn_data:
        print(f"error: target {args.target} not found in gn output", file=sys.stderr)
        sys.exit(1)

    all_sources = gn_data[args.target].get("sources", [])
    rs_sources = [
        normalize_gn_source_path(source)
        for source in all_sources
        if source.endswith(".rs")
    ]

    if not rs_sources:
        print(
            f"error: no Rust sources found in target {args.target}",
            file=sys.stderr,
        )
        sys.exit(1)

    root_module = pick_root_module(rs_sources)
    display_name = args.target.split(":", maxsplit=1)[-1] if ":" in args.target else args.target

    rust_project = {
        "crates": [
            {
                "display_name": display_name,
                "root_module": root_module,
                "edition": args.edition,
                "deps": [],
                "is_workspace_member": True,
            }
        ]
    }

    output_path = pathlib.Path(args.output)
    output_path.write_text(
        json.dumps(rust_project, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"generated {output_path} from {args.target}")


if __name__ == "__main__":
    main()
