import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
  name: "comfyui-Clothing Asset Library-lw.browser",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "ClothingGallery") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      created?.apply(this, arguments);
      const node = this;
      const value = node.widgets.find(w => w.name === "asset_id");
      let dialog, frame;
      const close = () => {
        window.removeEventListener("message", receive);
        dialog?.remove(); dialog = null; frame = null;
      };
      const previewBox = document.createElement("div");
      previewBox.style.cssText = "position:relative;width:100%;height:100%;background:#f8f7f3;border-radius:8px;overflow:hidden;";
      const preview = document.createElement("img");
      preview.alt = "所选服装资产预览";
      preview.style.cssText = "display:block;width:100%;height:100%;object-fit:contain;";
      const previewError = document.createElement("div");
      previewError.setAttribute("role", "status");
      previewError.setAttribute("aria-live", "polite");
      previewError.style.cssText = "display:none;position:absolute;inset:16px;place-items:center;color:#8b2e2e;font:14px/1.6 sans-serif;text-align:left;overflow-wrap:anywhere;";
      previewBox.append(preview, previewError);
      let previewRequest = 0;
      const update = () => {
        const request = ++previewRequest;
        const assetId = String(value.value || '');
        const parts = assetId.split('/');
        if (parts.length < 2) {
          preview.style.display = "none";
          previewError.textContent = `资产 ID 格式应为「分类/文件名.png」，当前为：${assetId || '（空）'}`;
          previewError.style.display = "grid";
          return;
        }
        const [cat, file] = parts;
        preview.style.display = "block";
        previewError.style.display = "none";
        preview.onload = () => { if (request !== previewRequest) return; preview.style.display = "block"; previewError.style.display = "none"; };
        preview.onerror = () => {
          if (request !== previewRequest) return;
          preview.style.display = "none";
          previewError.textContent = `原图加载失败：${assetId}。请确认 COMFYUI_CLOTHING_GALLERY_SOURCE 指向正确的服装资产图库目录，且文件存在。`;
          previewError.style.display = "grid";
        };
        preview.src = api.apiURL(`/clothing_gallery/asset/img/${encodeURIComponent(cat)}/${encodeURIComponent(file)}`);
        preview.title = assetId;
      };
      const previousCallback = value.callback;
      value.callback = function () { previousCallback?.apply(this, arguments); update(); };
      const receive = event => {
        if (event.origin !== location.origin || event.source !== frame?.contentWindow) return;
        if (event.data?.type === "clothing-gallery-ready") {
          frame.contentWindow.postMessage({ type: "clothing-gallery-current", id: value.value }, location.origin);
        }
        if (event.data?.type !== "clothing-gallery-select" || typeof event.data.id !== "string") return;
        value.value = event.data.id;
        value.callback?.(value.value);
        node.setDirtyCanvas(true, true);
        app.graph.change();
        close();
      };
      node.addWidget("button", "浏览服装资产图库 · 搜索 / 分类 / 预览", null, () => {
        if (dialog) return;
        dialog = document.createElement("dialog");
        dialog.style.cssText = "width:96vw;height:94vh;max-width:1800px;max-height:96vh;padding:0;border:1px solid #777;border-radius:12px;background:#f7f5ef;";
        const header = document.createElement("div");
        header.style.cssText = "height:48px;display:flex;align-items:center;justify-content:space-between;padding:0 20px;background:#f4e9f0;color:#5e2b4c;font:14px sans-serif;";
        const label = document.createElement("strong"); label.textContent = "Clothing Gallery · 选择资产后，点击「使用此资产」";
        const done = document.createElement("button"); done.textContent = "关闭";
        done.style.cssText = "cursor:pointer;padding:6px 16px;border-radius:6px;border:1px solid #e0b8d4;background:white;color:#5e2b4c;";
        done.onclick = close; header.append(label, done);
        frame = document.createElement("iframe");
        frame.src = api.apiURL("/clothing_gallery/gallery");
        frame.title = "服装资产参考图库";
        frame.style.cssText = "width:100%;height:calc(100% - 48px);border:0;";
        dialog.append(header, frame);
        window.addEventListener("message", receive);
        dialog.addEventListener("cancel", event => { event.preventDefault(); close(); });
        dialog.addEventListener("click", event => { if (event.target === dialog) close(); });
        document.body.append(dialog); dialog.showModal();
      }, { serialize: false });
      node.addDOMWidget("clothing_preview", "image", previewBox, { serialize: false, hideOnZoom: false, getMinHeight: () => 300, getMaxHeight: () => 500 });
      const configured = node.onConfigure;
      node.onConfigure = function () { configured?.apply(this, arguments); update(); };
      const removed = node.onRemoved;
      node.onRemoved = function () { close(); removed?.apply(this, arguments); };
      node.setSize([360, 510]); update();
    };
  },
});
