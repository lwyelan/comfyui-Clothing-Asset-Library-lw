#!/usr/bin/env python3
"""从外部服装素材目录转 WebP 内嵌进节点（library/originals），保留分类子目录。

用法:
  python scripts/import_assets.py [源目录]

源目录默认取环境变量 COMFYUI_CLOTHING_GALLERY_SOURCE，
否则 F:/工作流/LwYelan/服装资产图库。
输出: <节点>/library/originals/<分类>/<名称>.webp

特性: 自动跳过已存在的 .webp（可断点续传）；排除 macOS 资源分叉(__MACOSX)。
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit('需要 Pillow：请使用 ComfyUI 的 python 运行本脚本（F:/ComfyUI/ComfyUI-V9.5/python/python.exe）')

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'library' / 'originals'
DEFAULT_SRC = os.environ.get(
    'COMFYUI_CLOTHING_GALLERY_SOURCE',
    r'F:/工作流/LwYelan/服装资产图库')
SKIP_DIRS = {'__MACOSX', '__pycache__', '.git'}
EXTS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
QUALITY = 90


def convert(src: Path, rel: Path):
    dst = OUT / rel.with_suffix('.webp')
    if dst.exists() and dst.stat().st_size > 0:
        return 'skip'
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im.convert('RGB').save(dst, 'WEBP', quality=QUALITY, method=6)
    return 'ok'


def main():
    src = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(DEFAULT_SRC).resolve()
    if not src.is_dir():
        sys.exit(f'源目录不存在: {src}')
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.lower().endswith(EXTS):
                p = Path(root) / f
                rel = p.relative_to(src)
                jobs.append((p, rel))
    print(f'源: {src}\n输出: {OUT}\n待转换: {len(jobs)} 个文件 (已存在者跳过)')
    ok = skip = err = 0
    with ThreadPoolExecutor(max_workers=max(2, (os.cpu_count() or 4))) as ex:
        futs = [ex.submit(convert, p, rel) for p, rel in jobs]
        for fut in as_completed(futs):
            try:
                st = fut.result()
            except Exception as e:
                err += 1
                print('  ERR', type(e).__name__, e)
                continue
            ok += st == 'ok'
            skip += st == 'skip'
            total = ok + skip + err
            if total % 200 == 0:
                print(f'  进度 {total}/{len(jobs)} (新增 {ok}, 跳过 {skip}, 失败 {err})')
    print(f'完成: 新增 {ok}, 跳过已存在 {skip}, 失败 {err}')


if __name__ == '__main__':
    main()
