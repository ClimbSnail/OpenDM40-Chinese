#!/bin/sh
# Build opendm40 on Windows/git-bash with rustup installed by rustup-init
# --no-modify-path.
#
# Two path conventions, and they are not interchangeable:
#   * PATH entries must be MSYS form (/c/Users/...) or bash cannot find rustc.
#   * RUSTUP_HOME / CARGO_HOME must be Windows form (C:/Users/...), or
#     rustup.exe cannot find its settings.toml and reports "no default
#     toolchain", which leaves `rustc --print sysroot` empty and then
#     build.sh fails to locate llvm-objcopy.
# The llvm-tools bin dir goes on PATH too: build.sh finds llvm-objcopy via
# the sysroot, but tools/stack-depth/stackdepth.py wants llvm-objdump and
# looks for it on PATH.
set -e

export RUSTUP_HOME="C:/Users/xing'yan/.rustup"
export CARGO_HOME="C:/Users/xing'yan/.cargo"
LLVM="/c/Users/xing'yan/.rustup/toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin"
export PATH="/f/desk/study/dm40/rtools/bin:$LLVM:/c/Users/xing'yan/.cargo/bin:$PATH"

cd /f/desk/study/dm40/build/opendm40-0.3.0/firmware
exec ./build.sh "$@"
