#!/usr/bin/env python3
"""
Regenerate gRPC stubs from protos/product.proto into app/grpc_gen/.

Run from the python/ directory:
  python scripts/gen_grpc.py

The generated product_pb2_grpc.py imports its companion module as a bare
`import product_pb2`, which only resolves if grpc_gen/ is on sys.path. This
script rewrites that line to a package-relative import so the stubs work when
imported as app.grpc_gen.*.
"""
import re
from pathlib import Path

from grpc_tools import protoc

PYTHON_DIR = Path(__file__).resolve().parent.parent
PROTO_DIR = PYTHON_DIR / "protos"
OUT_DIR = PYTHON_DIR / "app" / "grpc_gen"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "__init__.py").touch()

    proto_file = str(PROTO_DIR / "product.proto")
    rc = protoc.main([
        "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
        proto_file,
    ])
    if rc != 0:
        raise SystemExit(f"protoc failed with exit code {rc}")

    # Fix the bare import in the generated gRPC stub.
    grpc_stub = OUT_DIR / "product_pb2_grpc.py"
    text = grpc_stub.read_text(encoding="utf-8")
    text, n = re.subn(
        r"^import product_pb2 as product__pb2$",
        "from app.grpc_gen import product_pb2 as product__pb2",
        text,
        flags=re.MULTILINE,
    )
    if n != 1:
        raise SystemExit(
            f"Expected to rewrite exactly 1 import line in {grpc_stub.name}, "
            f"rewrote {n}. The generated import form may have changed — "
            "update the regex in scripts/gen_grpc.py."
        )
    grpc_stub.write_text(text, encoding="utf-8")

    print(f"Generated stubs in {OUT_DIR}")


if __name__ == "__main__":
    main()
