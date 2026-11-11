#!/bin/sh
# Rebuild the Chinese v0.4.1 firmware from a clean upstream checkout.
#
#   ./patch/v041/build_zh.sh                       # -> build/out/DM40_v0.4.1.BIN
#   DM40_VERSION_SUFFIX=.02 ./patch/v041/build_zh.sh
#                                                  # -> build/out/DM40_v0.4.1.02.BIN
#                                                  #    (version string 0.4.1.02)
#
# The image is named the way the meter wants it on its USB volume
# (`DM40*.BIN`), so the build artifact can be copied over without renaming.
#
# Assumes build/worktree is a worktree of the upstream repo at tag v0.4.1
# (`git -C ../opendm40 worktree add build/worktree v0.4.1`), and that
# apply_dict.py / rebuild_fonts.py have already been run on it.
#
# Two path conventions (docs/刷机与构建记录.md): entries in PATH use the MSYS
# form (/c/...), RUSTUP_HOME and CARGO_HOME the Windows one (C:/...), because
# rustup.exe cannot read an MSYS path.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
TREE="${ZH_TREE:-$ROOT/build/worktree}"
export RUSTUP_HOME="${RUSTUP_HOME:-C:/Users/$USERNAME/.rustup}"
export CARGO_HOME="${CARGO_HOME:-C:/Users/$USERNAME/.cargo}"
export PATH="$HERE/bin:/c/Users/$USERNAME/.cargo/bin:$PATH"
export DM40_VERSION_SUFFIX="${DM40_VERSION_SUFFIX:-}"
export DM40_TDIR="${DM40_TDIR:-$ROOT/build/target-zh}"
VER=$(sed -n 's/^version[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "$TREE/firmware/Cargo.toml" | head -n 1)
[ -n "$VER" ] || { echo "build_zh.sh: cannot read version from $TREE/firmware/Cargo.toml" >&2; exit 1; }
export DM40_OUT="${DM40_OUT:-$ROOT/build/out/DM40_v${VER}${DM40_VERSION_SUFFIX}.BIN}"
mkdir -p "$ROOT/build/out" "$DM40_TDIR"

cd "$TREE/firmware"
python3 "$HERE/build_fix_windows.py" "$TREE/firmware"
exec ./build.sh "$@"
