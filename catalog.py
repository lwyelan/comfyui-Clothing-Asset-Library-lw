"""Local, allow-listed clothing asset catalogue. No runtime network downloads.

原图内嵌于节点自带的 library/originals（WebP，由 scripts/import_assets.py 生成）；
缩略图来自 library/thumbs（由 scripts/build_library.py 生成）。
默认自包含；可用环境变量 COMFYUI_CLOTHING_GALLERY_SOURCE 覆盖为外部目录。
"""
import json
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# 内嵌原图目录（节点自带 WebP，由 scripts/import_assets.py 生成）；可用环境变量覆盖
_SOURCE_ENV = os.environ.get('COMFYUI_CLOTHING_GALLERY_SOURCE')
SOURCE = (Path(_SOURCE_ENV).resolve() if _SOURCE_ENV
          else (ROOT / 'library' / 'originals').resolve())
# 缩略图目录（节点自带，build_library.py 生成）
THUMBS = (ROOT / 'library' / 'thumbs').resolve()
# 数据清单
DATA = (ROOT / 'library' / 'data' / 'clothing-zh.json').resolve()

VALID_KINDS = ('img', 'thumbs')


@lru_cache(maxsize=1)
def records():
    if not DATA.is_file():
        raise FileNotFoundError(
            '服装资产数据尚未生成，请先运行 python scripts/build_library.py')
    return json.loads(DATA.read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def index():
    return {row['id']: row for row in records()}


def asset_row(asset_id):
    try:
        return index()[asset_id]
    except KeyError:
        raise ValueError(f'未知资产 ID：{asset_id}') from None


def asset(kind, relpath):
    """解析图库内资源路径，返回绝对路径。kind 为 'img'（原图）或 'thumbs'（缩略图）。"""
    if kind not in VALID_KINDS:
        raise ValueError('无效资源类型')
    rel = Path(str(relpath).replace('\\', '/'))
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('无效图片路径')
    base = SOURCE if kind == 'img' else THUMBS
    target = (base / rel).resolve()
    if base != target and base not in target.parents:
        raise ValueError('图片不在图库内')
    if not target.is_file():
        if kind == 'img':
            raise FileNotFoundError(
                f'原图缺失：{rel}。请确认 COMFYUI_CLOTHING_GALLERY_SOURCE 指向正确的服装资产图库目录。')
        raise FileNotFoundError(
            f'缩略图缺失：{rel}。请运行 python scripts/build_library.py 生成缩略图。')
    return target
