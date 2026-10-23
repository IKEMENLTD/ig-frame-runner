"""GitHub Actions の中で回す：動画の URL の一覧から、1本ごとにコマ一覧（画が変わった所・秒つき）を作る。

    python runner.py items.json out/

items.json：[{"id": "短い名前", "url": "動画の直リンク（CDN）か投稿のページ"}, ...]
出力：out/<id>_<n>.jpg（1枚 5列×2段＝10コマ・1コマ 312×555・1560×1130）、out/meta.json
コマは 3fps で取り、前のコマとの違いが大きい所だけ残す（最大 30コマ＝3枚）。テロップの色・書体・縁を読めるよう、
1コマを大きめにしている（208×370 では書体が潰れた）。
"""
import glob, json, os, shutil, subprocess, sys, time, urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CW, CH, COLS, ROWS, LAB = 312, 555, 5, 2, 20
PER = COLS * ROWS
MAXF = 30


def fetch(url, out):
    if "cdninstagram" in url or url.endswith(".mp4") or "fbcdn" in url:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
            shutil.copyfileobj(r, f)
    else:
        subprocess.run(["yt-dlp", "-q", "--no-warnings", "-f", "b[vcodec^=h264]/b", "-o", out, url], check=True,
                       timeout=300)
    return out


def blocks(p):
    a = np.asarray(Image.open(p).convert("L").resize((72, 128)), dtype=np.float32)
    return a.reshape(16, 8, 9, 8).mean(axis=(1, 3))


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", p],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    s = next((x for x in d.get("streams", []) if x.get("width")), {})
    return {"w": s.get("width"), "h": s.get("height"), "duration": float(d.get("format", {}).get("duration", 0))}


def sheets(vid, path, out):
    fd = f"tmp/{vid}"
    shutil.rmtree(fd, ignore_errors=True)
    os.makedirs(fd)
    subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf",
                    f"fps=3,scale={CW}:{CH}:force_original_aspect_ratio=decrease,pad={CW}:{CH}:(ow-iw)/2:(oh-ih)/2",
                    "-q:v", "3", f"{fd}/%05d.jpg"], check=True)
    fs = sorted(glob.glob(f"{fd}/*.jpg"))
    keep, prev = [], None
    for i, f in enumerate(fs):
        b = blocks(f)
        d = 999.0 if prev is None else float(np.abs(b - prev).max())
        if d > 14:
            keep.append((f, i / 3, d))
            prev = b
    if len(keep) > MAXF:
        keep = [keep[0]] + sorted(sorted(keep[1:], key=lambda k: -k[2])[:MAXF - 1], key=lambda k: k[1])
    font = ImageFont.load_default(16)
    n = 0
    for s in range(0, len(keep), PER):
        part = keep[s:s + PER]
        im = Image.new("RGB", (COLS * CW, ROWS * (CH + LAB)), "white")
        dr = ImageDraw.Draw(im)
        for k, (f, t, _) in enumerate(part):
            x, y = (k % COLS) * CW, (k // COLS) * (CH + LAB)
            im.paste(Image.open(f), (x, y))
            dr.text((x + 4, y + CH + 1), f"{t:.1f}s" + (f"  {vid}" if k == 0 else ""), fill="black", font=font)
        n += 1
        im.save(f"{out}/{vid}_{n}.jpg", quality=80)
    shutil.rmtree(fd, ignore_errors=True)
    return len(keep), n


def main(items_p, out):
    os.makedirs(out, exist_ok=True)
    os.makedirs("v", exist_ok=True)
    items = json.load(open(items_p, encoding="utf-8"))
    meta = {}
    for it in items:
        vid, url = it["id"], it["url"]
        t0 = time.time()
        try:
            p = fetch(url, f"v/{vid}.mp4")
            info = probe(p)
            frames, n = sheets(vid, p, out)
            info.update(frames=frames, sheets=n, secs=round(time.time() - t0, 1))
            os.remove(p)
        except Exception as e:
            info = {"error": str(e)[-300:]}
        meta[vid] = info
        print(vid, info, flush=True)
    json.dump(meta, open(f"{out}/meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
