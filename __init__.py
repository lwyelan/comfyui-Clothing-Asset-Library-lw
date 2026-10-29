"""comfyui-Clothing-Asset-Library-lw: browse local clothing assets and output an IMAGE."""
import hashlib
import numpy as np
import torch
from PIL import Image, ImageOps
from aiohttp import web
from server import PromptServer
from .catalog import records, asset_row, asset, ROOT

class ClothingGallery:
    @classmethod
    def INPUT_TYPES(cls):
        default_id = ''
        try:
            recs = records()
            if recs:
                default_id = recs[0]['id']
        except Exception:
            pass
        return {'required': {'asset_id': ('STRING', {
            'default': default_id,
            'multiline': False,
            'tooltip': '点击「浏览服装资产图库」选择；也可直接输入资产 ID（形如 内衣/LNG-0001.webp）。'
        })}}

    RETURN_TYPES = ('IMAGE', 'INT', 'INT', 'STRING', 'STRING')
    RETURN_NAMES = ('image', 'width', 'height', 'asset_id', 'description')
    FUNCTION = 'load_clothing'
    CATEGORY = 'image/Clothing Asset Library'
    DESCRIPTION = '本地中文服装资产图库：按季节 / 场景 / 品类筛选、搜索、预览。选择原图输出为 IMAGE，可直接接入 IPAdapter / 垫图 / 局部重绘等节点。'

    @classmethod
    def VALIDATE_INPUTS(cls, asset_id):
        try:
            row = asset_row(asset_id)
            asset('img', row['原图'])
        except (ValueError, FileNotFoundError) as exc:
            return str(exc)
        return True

    @classmethod
    def IS_CHANGED(cls, asset_id):
        row = asset_row(asset_id)
        return hashlib.sha256(asset('img', row['原图']).read_bytes()).hexdigest()

    def load_clothing(self, asset_id):
        row = asset_row(asset_id)
        with Image.open(asset('img', row['原图'])) as source:
            img = ImageOps.exif_transpose(source).convert('RGBA')
            background = Image.new('RGBA', img.size, 'white')
            img = Image.alpha_composite(background, img).convert('RGB')
            width, height = img.size
            tensor = torch.from_numpy(np.asarray(img).astype(np.float32) / 255.0).unsqueeze(0)
        description = ' / '.join(row.get(k, '') for k in ('分类', '名称'))
        return (tensor, width, height, asset_id, description)

routes = PromptServer.instance.routes

@routes.get('/clothing_gallery/catalog')
async def catalog_route(request):
    try:
        return web.json_response(records())
    except (ValueError, FileNotFoundError) as exc:
        return web.json_response({'error': str(exc)}, status=503)

@routes.get('/clothing_gallery/asset/{kind}/{path:.*}')
async def asset_route(request):
    try:
        kind = request.match_info['kind']
        target = asset(kind, request.match_info['path'])
        return web.FileResponse(target, headers={'Cache-Control': 'private, max-age=3600'})
    except (ValueError, FileNotFoundError):
        raise web.HTTPNotFound()

@routes.get('/clothing_gallery/gallery')
async def gallery_route(request):
    return web.FileResponse(ROOT / 'web' / 'gallery.html', headers={'Cache-Control': 'no-cache'})

NODE_CLASS_MAPPINGS = {'ClothingGallery': ClothingGallery}
NODE_DISPLAY_NAME_MAPPINGS = {'ClothingGallery': 'Clothing Asset Library 服装资产图库'}
WEB_DIRECTORY = './web'
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
