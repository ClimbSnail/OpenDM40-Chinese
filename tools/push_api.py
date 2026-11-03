#!/usr/bin/env python3
"""Push a directory to GitHub through the REST API.

Why not `git push`: on this machine github.com:443 is reset (only
api.github.com and codeload.github.com answer), so the git wire protocol
cannot be used. The API can still create blobs, a tree, a commit and the ref.

    set GITHUB_TOKEN=...
    python push_api.py --repo OWNER/NAME --dir DIR --branch main \\
        --message-file MSG.txt | --message "单行说明"

curl is used for the HTTP calls: .NET's TLS stack is blocked here but curl
works. The token is handed to curl through a temporary config file (-K) so it
never shows up in the process table or in argv.
"""

import base64
import json
import os
import subprocess
import sys
import tempfile

API = "https://api.github.com"


class Ctx:
    def __init__(self, token):
        fd, self.cfg = tempfile.mkstemp(suffix=".curlrc")
        os.close(fd)
        with open(self.cfg, "w", encoding="utf-8") as f:
            f.write('header = "Authorization: Bearer %s"\n' % token)

    def close(self):
        try:
            os.unlink(self.cfg)
        except OSError:
            pass

    def call(self, method, url, body=None):
        cmd = ["curl.exe", "-sS", "-m", "180", "-K", self.cfg, "-X", method, url,
               "-H", "Accept: application/vnd.github+json",
               "-H", "X-GitHub-Api-Version: 2022-11-28",
               "-H", "User-Agent: opendm40-zh-push",
               "-w", "\n__HTTP__%{http_code}"]
        tmp = None
        if body is not None:
            fd, tmp = tempfile.mkstemp(suffix=".json")
            os.close(fd)
            with open(tmp, "wb") as f:
                f.write(json.dumps(body).encode())
            cmd += ["-H", "Content-Type: application/json", "--data-binary", "@" + tmp]
        try:
            out = subprocess.run(cmd, capture_output=True)
            raw = out.stdout.decode("utf-8", "replace")
            if not raw:
                raise RuntimeError(out.stderr.decode("utf-8", "replace"))
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass

        if "__HTTP__" not in raw:
            raise RuntimeError("no status: %r" % raw[:300])
        payload, code = raw.rsplit("__HTTP__", 1)
        return int(code), payload.strip()


def main():
    argv = sys.argv[1:]

    def opt(n, d=None):
        return argv[argv.index(n) + 1] if n in argv else d

    repo, root = opt("--repo"), opt("--dir")
    branch = opt("--branch", "main")
    msg_file = opt("--message-file")
    token = os.environ.get("GITHUB_TOKEN")
    if not (repo and root and token):
        sys.exit("need --repo, --dir and GITHUB_TOKEN in the environment")

    msg_inline = opt("--message")
    if msg_file:
        message = open(msg_file, encoding="utf-8").read()
    elif msg_inline:
        message = msg_inline
    else:
        message = "update"

    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            files.append((os.path.relpath(full, root).replace("\\", "/"), full))
    files.sort()
    sys.stderr.write("%d files\n" % len(files))

    ctx = Ctx(token)
    try:
        code, payload = ctx.call("GET", "%s/repos/%s/git/ref/heads/%s" % (API, repo, branch))
        parents = [] if code in (404, 409) else [json.loads(payload)["object"]["sha"]]
        sys.stderr.write("parents: %s\n" % (parents or "none (first commit)"))

        tree = []
        for i, (rel, full) in enumerate(files, 1):
            data = open(full, "rb").read()
            code, payload = ctx.call(
                "POST", "%s/repos/%s/git/blobs" % (API, repo),
                {"content": base64.b64encode(data).decode(), "encoding": "base64"})
            if code != 201:
                sys.exit("\nblob %s: HTTP %d %s" % (rel, code, payload[:400]))
            tree.append({"path": rel, "mode": "100644", "type": "blob",
                         "sha": json.loads(payload)["sha"]})
            sys.stderr.write("\r  [%d/%d] %-46s %8d B" % (i, len(files), rel[:46], len(data)))
            sys.stderr.flush()
        sys.stderr.write("\n")

        code, payload = ctx.call("POST", "%s/repos/%s/git/trees" % (API, repo), {"tree": tree})
        if code != 201:
            sys.exit("tree: HTTP %d %s" % (code, payload[:400]))
        tree_sha = json.loads(payload)["sha"]

        code, payload = ctx.call("POST", "%s/repos/%s/git/commits" % (API, repo),
                                 {"message": message, "tree": tree_sha, "parents": parents})
        if code != 201:
            sys.exit("commit: HTTP %d %s" % (code, payload[:400]))
        commit_sha = json.loads(payload)["sha"]
        sys.stderr.write("commit %s\n" % commit_sha)

        if parents:
            code, payload = ctx.call("PATCH", "%s/repos/%s/git/refs/heads/%s" % (API, repo, branch),
                                     {"sha": commit_sha, "force": False})
        else:
            code, payload = ctx.call("POST", "%s/repos/%s/git/refs" % (API, repo),
                                     {"ref": "refs/heads/" + branch, "sha": commit_sha})
        if code not in (200, 201):
            sys.exit("ref: HTTP %d %s" % (code, payload[:400]))

        code, payload = ctx.call("GET", "%s/repos/%s/git/ref/heads/%s" % (API, repo, branch))
        print("OK  %s @ %s" % (repo, json.loads(payload)["object"]["sha"]))
    finally:
        ctx.close()


main()
