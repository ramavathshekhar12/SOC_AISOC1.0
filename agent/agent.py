import argparse, time, hashlib, json, os, sys, platform, requests

def tail_file(path):
    with open(path, "r", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line.rstrip("\n")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manager", required=True, help="Manager base URL, e.g., http://localhost:8000")
    p.add_argument("--token", required=True, help="Shared agent token")
    p.add_argument("--watch", action="append", help="File(s) to tail for logs")
    p.add_argument("--fim", action="append", help="File(s) to hash and watch for changes")
    args = p.parse_args()

    host = platform.node()
    sess = requests.Session()
    headers = {"x-agent-token": args.token}

    # FIM baseline
    fim_hashes = {}
    if args.fim:
        for path in args.fim:
            if os.path.isfile(path):
                fim_hashes[path] = sha256_file(path)

    # Start tailers
    streams = []
    if args.watch:
        for w in args.watch:
            if os.path.isfile(w):
                streams.append(tail_file(w))

    while True:
        # Send tailed logs
        for s in streams:
            line = next(s)
            ev = {
                "source": "agent",
                "host": host,
                "@raw": line
            }
            try:
                r = sess.post(f"{args.manager}/intake", json=ev, headers=headers, timeout=5)
                r.raise_for_status()
            except Exception as e:
                print("intake error:", e, file=sys.stderr)

        # Simple FIM check
        if args.fim:
            for path, old_hash in list(fim_hashes.items()):
                if not os.path.exists(path):
                    continue
                new_hash = sha256_file(path)
                if new_hash != old_hash:
                    fim_hashes[path] = new_hash
                    ev = {
                        "source": "agent",
                        "host": host,
                        "@raw": json.dumps({"ai_soc_fim": True, "event": "modified", "path": path, "sha256": new_hash})
                    }
                    try:
                        r = sess.post(f"{args.manager}/intake", json=ev, headers=headers, timeout=5)
                        r.raise_for_status()
                    except Exception as e:
                        print("intake error:", e, file=sys.stderr)

        time.sleep(0.25)

if __name__ == "__main__":
    main()
