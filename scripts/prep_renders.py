#!/usr/bin/env python3
"""Prepare 3D renders (still or movie) for use as decorative page accents.

Keys out a neutral render backdrop (grey wall, white floor, shadows) to black so the
coloured cells sit on the site's dark background, then crops to the subject.

    python scripts/prep_renders.py image SRC NAME [--pale]
        -> images/renders/NAME.webp
    python scripts/prep_renders.py movie SRC NAME [--start SECONDS] [--keep-backdrop [--crop X0,X1]]
        -> assets/video/NAME.mp4 and NAME.webm, plus images/renders/NAME_start.webp and NAME_end.webp

--pale also keeps subjects lighter than the backdrop (e.g. beige cells on grey), which have
too little colour to key on alone. --keep-backdrop encodes a movie as rendered, at full
resolution, without keying or cropping. Movies need ffmpeg. Run once per new render and commit
the outputs; the regular build (main.py) does not run this.
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / 'images' / 'renders'
VIDEO = ROOT / 'assets' / 'video'


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def key(rgb, pale=False, backdrop=64):
    """Return (keyed RGB on black, alpha). Alpha comes from chroma, so grey and white drop out."""
    f = rgb.astype(np.float32)
    alpha = smoothstep(8, 34, f.max(2) - f.min(2))
    if pale:
        lum = f @ np.array([.2126, .7152, .0722], np.float32)
        alpha = np.maximum(alpha, smoothstep(backdrop + 18, backdrop + 60, lum))
    return (f * alpha[..., None]).astype(np.uint8), alpha


def bbox(alpha, margin=.04, thresh=.2):
    ys, xs = np.nonzero(alpha > thresh)
    h, w = alpha.shape
    my, mx = int(h * margin), int(w * margin)
    return max(xs.min() - mx, 0), max(ys.min() - my, 0), min(xs.max() + mx, w), min(ys.max() + my, h)


def image(src, name, pale=False):
    rgb = np.asarray(Image.open(src).convert('RGB'))
    out, alpha = key(rgb, pale)
    RENDERS.mkdir(parents=True, exist_ok=True)
    dest = RENDERS / f'{name}.webp'
    Image.fromarray(out).crop(bbox(alpha)).save(dest, 'WEBP', quality=90)
    print(dest.relative_to(ROOT))


def frames(src, start, w, h):
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(start), '-i', str(src),
                             '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    size = w * h * 3
    while chunk := proc.stdout.read(size):
        if len(chunk) < size:
            break
        yield np.frombuffer(chunk, np.uint8).reshape(h, w, 3)
    proc.wait()


def movie_as_rendered(src, name, start=0.0, crop=None):
    """Encode a movie at full resolution with its backdrop: MP4 (listed first) and a WebM fallback.
    crop=(x0, x1) keeps only that horizontal span, as fractions of the frame width."""
    vf = ['-vf', 'crop=trunc(iw*{w}/2)*2:ih:trunc(iw*{x}/2)*2:0'.format(w=crop[1] - crop[0], x=crop[0])] if crop else []
    VIDEO.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    codecs = {
        'mp4': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '27', '-movflags', '+faststart'],
        'webm': ['-c:v', 'libvpx-vp9', '-crf', '36', '-b:v', '0', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2'],
    }
    for ext, args in codecs.items():
        dest = VIDEO / f'{name}.{ext}'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-i', str(src)] + vf
                       + ['-pix_fmt', 'yuv420p', '-an'] + args + [str(dest)], check=True)
        print(dest.relative_to(ROOT), f'{dest.stat().st_size / 1e6:.1f} MB')
    for label, seek in (('start', ['-ss', str(start)]), ('end', ['-sseof', '-0.1'])):
        png = RENDERS / f'{name}_{label}.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + seek + ['-i', str(src)] + vf + ['-frames:v', '1', str(png)], check=True)
        Image.open(png).convert('RGB').save(RENDERS / f'{name}_{label}.webp', 'WEBP', quality=88)
        png.unlink()


def movie(src, name, start=0.0, max_w=960):
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height,r_frame_rate', '-of', 'csv=p=0', str(src)],
                           capture_output=True, text=True, check=True).stdout.strip().split(',')
    w, h, fps = int(probe[0]), int(probe[1]), probe[2]

    # Pass 1: crop box covering the subject in every frame.
    x0, y0, x1, y1 = w, h, 0, 0
    for rgb in frames(src, start, w, h):
        bx = bbox(key(rgb)[1])
        x0, y0, x1, y1 = min(x0, bx[0]), min(y0, bx[1]), max(x1, bx[2]), max(y1, bx[3])
    cw, ch = (x1 - x0) // 2 * 2, (y1 - y0) // 2 * 2
    scale = min(1.0, max_w / cw)
    ow, oh = int(cw * scale) // 2 * 2, int(ch * scale) // 2 * 2

    # Pass 2: key, crop, encode without audio: H.264 MP4 (smaller; the page lists it first) and a
    # VP9 WebM fallback for browsers built without H.264.
    VIDEO.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    raw = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{cw}x{ch}',
           '-r', fps, '-i', '-', '-vf', f'scale={ow}:{oh}', '-pix_fmt', 'yuv420p', '-an']
    codecs = {
        'webm': ['-c:v', 'libvpx-vp9', '-crf', '40', '-b:v', '0', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2'],
        'mp4': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '30', '-movflags', '+faststart'],
    }
    encoders = [subprocess.Popen(raw + args + [str(VIDEO / f'{name}.{ext}')], stdin=subprocess.PIPE)
                for ext, args in codecs.items()]
    first = last = None
    for rgb in frames(src, start, w, h):
        out = np.ascontiguousarray(key(rgb)[0][y0:y0 + ch, x0:x0 + cw])
        for enc in encoders:
            enc.stdin.write(out.tobytes())
        first = out if first is None else first
        last = out
    for enc in encoders:
        enc.stdin.close()
        enc.wait()
    for label, arr in (('start', first), ('end', last)):
        Image.fromarray(arr).resize((ow, oh), Image.LANCZOS).save(RENDERS / f'{name}_{label}.webp', 'WEBP', quality=88)
    for ext in codecs:
        dest = VIDEO / f'{name}.{ext}'
        print(dest.relative_to(ROOT), f'{dest.stat().st_size / 1e6:.1f} MB, {ow}x{oh}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('kind', choices=['image', 'movie'])
    ap.add_argument('src', type=Path)
    ap.add_argument('name')
    ap.add_argument('--pale', action='store_true', help='also keep subjects lighter than the backdrop')
    ap.add_argument('--start', type=float, default=0.0, help='movie: seconds to trim from the start')
    ap.add_argument('--keep-backdrop', action='store_true', help='movie: encode as rendered, full resolution')
    ap.add_argument('--crop', help='movie with --keep-backdrop: horizontal span to keep, e.g. 0.10,0.86')
    args = ap.parse_args()
    if args.kind == 'image':
        image(args.src, args.name, args.pale)
    elif args.keep_backdrop:
        movie_as_rendered(args.src, args.name, args.start,
                          tuple(float(v) for v in args.crop.split(',')) if args.crop else None)
    else:
        movie(args.src, args.name, args.start)


if __name__ == '__main__':
    main()
