#!/usr/bin/env python3
"""生成 comfyui-Clothing Asset Library-lw 的数据清单与缩略图。

默认扫描节点内已内嵌的 WebP 原图目录 library/originals（由 scripts/import_assets.py 生成），
写入 library/data/clothing-zh.json 与 library/data/meta-zh.json，
并生成 library/thumbs/<分类>/<名称>.jpg 缩略图（已存在则跳过）。

可用环境变量 COMFYUI_CLOTHING_GALLERY_SOURCE 覆盖为外部素材目录。
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit('需要 Pillow：请使用 ComfyUI 的 python 运行本脚本（F:/ComfyUI/ComfyUI-V9.5/python/python.exe）')

ROOT = Path(__file__).resolve().parent.parent  # 节点根目录（scripts/ 的上一级）
_SOURCE_ENV = os.environ.get('COMFYUI_CLOTHING_GALLERY_SOURCE')
SOURCE = (Path(_SOURCE_ENV).resolve() if _SOURCE_ENV
          else (ROOT / 'library' / 'originals').resolve())
DATA_DIR = ROOT / 'library' / 'data'
THUMBS_DIR = ROOT / 'library' / 'thumbs'
THUMB_SIZE = (384, 576)      # 长边不超过 384px
THUMB_QUALITY = 82
EXTS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')


def list_categories(src):
    return sorted(d.name for d in src.iterdir()
                  if d.is_dir() and not d.name.startswith(('__', '.')))


def make_thumb(src_path, dst_path):
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if dst_path.is_file() and dst_path.stat().st_size > 0:
        return
    with Image.open(src_path) as im:
        im = im.convert('RGB')
        im.thumbnail(THUMB_SIZE, Image.LANCZOS)
        im.save(dst_path, 'JPEG', quality=THUMB_QUALITY, optimize=True)


def main():
    if not SOURCE.is_dir():
        sys.exit(f'素材目录不存在：{SOURCE}')
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

    cats = list_categories(SOURCE)
    print(f'素材根目录: {SOURCE}')
    print(f'发现分类: {cats}')

    records = []
    thumb_jobs = []
    for cat in cats:
        folder = SOURCE / cat
        files = sorted(f for f in folder.iterdir()
                       if f.is_file() and f.suffix.lower() in EXTS)
        for f in files:
            stem = f.stem
            aid = f'{cat}/{f.name}'          # 资产 ID 即相对路径，便于前端重建 URL
            rel_orig = aid
            rel_thumb = f'{cat}/{stem}.jpg'
            records.append({
                'id': aid,
                '分类': cat,
                '名称': stem,
                '文件名': f.name,
                '原图': rel_orig,
                '缩略图': rel_thumb,
                '检索': f'{aid} {cat} {stem} {f.name}'.lower(),
            })
            thumb_jobs.append((f, THUMBS_DIR / rel_thumb))

    print(f'共 {len(records)} 个资产，开始生成缩略图...')
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for _ in ex.map(lambda j: make_thumb(*j), thumb_jobs):
            done += 1
            if done % 200 == 0:
                print(f'  缩略图 {done}/{len(thumb_jobs)}')
    print(f'缩略图完成：{done}')

    (DATA_DIR / 'clothing-zh.json').write_text(
        json.dumps(records, ensure_ascii=False, indent=0), encoding='utf-8')
    (DATA_DIR / 'meta-zh.json').write_text(
        json.dumps({'分类': cats, '总数': len(records)}, ensure_ascii=False, indent=2),
        encoding='utf-8')
    print(f'数据写入: {DATA_DIR / "clothing-zh.json"} ({len(records)} 条)')


if __name__ == '__main__':
    main()
