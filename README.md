# Clothing Asset Library 服装资产图库（ComfyUI 节点）

参照 `comfyui-pose-gallery` 架构实现的本地服装资产节点。**资产已内嵌**，是一个自包含、可直接上传 GitHub 的节点包。浏览本地服装参考图库，选择后输出为 `IMAGE`，可直接接入 IPAdapter / 垫图 / 局部重绘等节点。

## 资源（已内嵌，无需外部文件）

全部 1407 张服装参考图已转 **WebP（质量 90）** 内嵌于节点，clone 即用：

- 原图：`library/originals/<分类>/<名称>.webp`（约 129MB，由原 PNG 压缩至约 1/10）
- 缩略图：`library/thumbs/<分类>/<名称>.jpg`（约 28MB，画廊浏览用）

分类：内衣 / 冬 / 夏 / 性感 / 春 / 泳装 / 派对 / 秋。

> 默认从节点内 `library/originals` 读取；如需改用外部目录，设置环境变量 `COMFYUI_CLOTHING_GALLERY_SOURCE` 指向「含上述分类子目录」的目录即可。

## 目录结构

```
comfyui-Clothing Asset Library-lw/
├── __init__.py               # ClothingGallery 节点 + HTTP 路由
├── catalog.py                # 数据层：扫描内嵌资源、防目录穿越
├── pyproject.toml
├── README.md
├── scripts/
│   ├── import_assets.py      # 从外部素材目录转 WebP 内嵌（更新资产用）
│   └── build_library.py      # 扫描内嵌 webp 生成数据清单 + 缩略图
├── web/
│   ├── gallery.html          # 服装画廊前端
│   └── clothing_gallery.js   # ComfyUI 前端扩展（按钮弹窗、回写 asset_id）
└── library/
    ├── data/clothing-zh.json # 1407 条资产清单
    ├── originals/            # 内嵌原图（WebP）
    └── thumbs/               # 缩略图（JPG）
```

## 使用

1. 把本目录放入 ComfyUI 的 `custom_nodes/`，**重启 ComfyUI**。
2. 节点列表的 `image / Clothing Asset Library` 下找到 `Clothing Asset Library 服装资产图库`。
3. 节点 `asset_id` 输入框旁有「浏览服装资产图库」按钮 → 弹窗搜索 / 筛选 / 选图 → 点「使用此资产 → ComfyUI」回填 ID，节点内实时预览。
4. 输出 `IMAGE` 可直接接 IPAdapter / 垫图 / 局部重绘等。

## 重建 / 更新资产

用 ComfyUI 自带的 Python：

```bash
# 从外部素材目录转 WebP 内嵌（首次构建或补充/替换素材；已存在自动跳过）
F:/ComfyUI/ComfyUI-V9.5/python/python.exe scripts/import_assets.py [外部素材目录]

# 扫描 library/originals 生成数据清单与缩略图
F:/ComfyUI/ComfyUI-V9.5/python/python.exe scripts/build_library.py
```

## HTTP 路由（节点内部）

- `/clothing_gallery/catalog`：资产清单 JSON
- `/clothing_gallery/asset/{kind}/{path}`：原图（kind=img）或缩略图（kind=thumbs）
- `/clothing_gallery/gallery`：画廊页面

## 上传 GitHub

本包完全自包含，单文件均 < 1MB，总体积约 157MB（原图 129MB + 缩略图 28MB），**可直接 `git add` 推送，无需 Git LFS**：

```bash
git init
git add -A
git commit -m "Clothing Asset Library: 1407 内嵌 WebP 服装资产 + ComfyUI 节点"
git remote add origin <你的仓库地址>
git push -u origin main
```

资产图片版权归原作者所有；节点代码以 MIT 许可发布。
