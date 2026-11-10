#!/bin/sh
# Run the host test suites (same environment as build_zh.sh).
set -e

export RUSTUP_HOME="C:/Users/xing'yan/.rustup"
export CARGO_HOME="C:/Users/xing'yan/.cargo"
LLVM="/c/Users/xing'yan/.rustup/toolchains/stable-x86_64-pc-windows-msvc/lib/rustlib/x86_64-pc-windows-msvc/bin"
export PATH="/f/desk/study/dm40/rtools/bin:$LLVM:/c/Users/xing'yan/.cargo/bin:$PATH"

cd /f/desk/study/dm40/build/opendm40-0.3.0/firmware
exec tools/ci-tests.sh "$@"
