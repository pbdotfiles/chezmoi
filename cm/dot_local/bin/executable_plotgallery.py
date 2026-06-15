#!/usr/bin/env python3

import argparse
import json
import os
import tempfile
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PLOT_DIR = Path("/tmp/ipython_plots")


class GalleryHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PLOT_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/api/clear":
            for f in os.listdir(PLOT_DIR):
                if f.endswith((".png", ".html")):
                    try:
                        os.remove(os.path.join(PLOT_DIR, f))
                    except OSError:
                        pass
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Plot Gallery</title>
                <style>
                    body { display: flex; height: 100vh; margin: 0; font-family: sans-serif; background: #1e1e1e; color: #d4d4d4; overflow: hidden;}
                    #sidebar { width: 300px; display: flex; flex-direction: column; background: #252526; flex-shrink: 0; }
                    #resizer { width: 5px; background: #3c3c3c; cursor: col-resize; flex-shrink: 0; transition: background 0.2s; }
                    #resizer:hover, #resizer.active { background: #007acc; }
                    #sidebar-header { padding: 15px; background: #2d2d30; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #3c3c3c; font-weight: bold;}
                    #clear-btn { background: #c53b3b; color: white; border: none; padding: 6px 12px; cursor: pointer; border-radius: 4px; font-weight: bold;}
                    #clear-btn:hover { background: #e04a4a; }
                    #file-list { flex-grow: 1; overflow-y: auto; padding: 10px; scroll-behavior: auto;}

                    .file-item { display: flex; flex-direction: column; padding: 10px; cursor: pointer; border: 1px solid transparent; border-bottom: 1px solid #3c3c3c; border-radius: 6px; margin-bottom: 8px; background: #2a2d2e;}
                    .file-item.active { background: #094771; border-color: #007acc; box-shadow: 0 0 8px rgba(0, 122, 204, 0.4);}

                    .thumb-container { width: 100%; aspect-ratio: 4 / 3; display: flex; justify-content: center; align-items: center; margin-bottom: 8px; background: #1e1e1e; border-radius: 4px; overflow: hidden; pointer-events: none;}
                    .thumb-img { max-width: 100%; max-height: 100%; object-fit: contain; background: white;}
                    .plotly-placeholder { width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #1e1e1e; color: #4ec9b0; font-weight: bold; border: 1px dashed #3c3c3c;}

                    .file-label { font-size: 13px; color: #cccccc; text-align: center; font-family: monospace;}
                    .file-timestamp { font-size: 11px; color: #808080; text-align: center; margin-top: 4px; }

                    #filename-overlay { position: absolute; top: 0; left: 0; right: 0; z-index: 10; background: rgba(37,37,38,0.85); padding: 8px 16px; display: none; justify-content: space-between; align-items: center; font-size: 13px; font-family: monospace; border-bottom: 1px solid #3c3c3c; }
                    #filename-overlay .filename-text { color: #4ec9b0; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
                    #filename-overlay .file-timestamp { color: #808080; margin-top: 0; white-space: nowrap; }

                    .file-item.updated { animation: flash-update 0.5s ease-in-out 3; }
                    @keyframes flash-update { 0%, 100% { border-color: transparent; } 50% { border-color: #4ec9b0; box-shadow: 0 0 8px rgba(78,201,176,0.5); } }
                    #main-content.updated-border { animation: flash-border 0.5s ease-in-out 3; }
                    @keyframes flash-border { 0%, 100% { box-shadow: none; } 50% { box-shadow: inset 0 0 20px rgba(78,201,176,0.3); } }

                    /* Main & Zoom Styles */
                    #main { flex-grow: 1; display: flex; position: relative; overflow: hidden; background: #1e1e1e; min-width: 0; }
                    #main-content { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; padding: 20px; box-sizing: border-box; position: relative;}
                    #main-content img { max-width: 100%; max-height: 100%; object-fit: contain; background: white; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); cursor: grab; transform-origin: center; }
                    #main-content img:active { cursor: grabbing; }
                    #main-content iframe { width: 100%; height: 100%; border: none; background: white; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);}

                    #zoom-controls { position: absolute; bottom: 30px; right: 30px; display: none; gap: 8px; background: rgba(37, 37, 38, 0.85); padding: 8px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); z-index: 10; }
                    .icon-btn { background: #3c3c3c; color: #fff; border: 1px solid #555; width: 32px; height: 32px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 18px; display: flex; justify-content: center; align-items: center; transition: background 0.1s;}
                    .icon-btn:hover { background: #007acc; border-color: #007acc; }

                    .loader-text { color: #808080; font-size: 1.2em; font-weight: bold; }
                </style>
            </head>
            <body>
                <div id="sidebar">
                    <div id="sidebar-header">
                        <span>Plot Gallery</span>
                        <button id="clear-btn" onclick="clearGallery()">Clear All</button>
                    </div>
                    <div id="file-list"></div>
                </div>
                <div id="resizer"></div>
                <div id="main">
                    <div id="filename-overlay">
                        <span class="filename-text"></span>
                        <span class="file-timestamp"></span>
                    </div>
                    <div id="zoom-controls">
                        <button class="icon-btn" onclick="changeZoom(0.25)" title="Zoom In">+</button>
                        <button class="icon-btn" onclick="changeZoom(-0.25)" title="Zoom Out">-</button>
                        <button class="icon-btn" onclick="resetZoom()" title="Reset Zoom">⟲</button>
                    </div>
                    <div id="main-content"><div class="loader-text">Waiting for plots...</div></div>
                </div>

                <script>
                    let currentFiles = [];
                    let activeFileName = null;
                    let renderTimer = null;
                    let flashTimer = null;

                    // --- Zoom & Pan Variables ---
                    let imgScale = 1;
                    let imgTranslateX = 0;
                    let imgTranslateY = 0;
                    let isPanning = false;
                    let startX, startY;

                    function timeAgo(mtime) {
                        const diff = Date.now() / 1000 - mtime;
                        if (diff < 10) return 'just now';
                        if (diff < 60) return Math.floor(diff) + 's ago';
                        if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
                        if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
                        return Math.floor(diff / 86400) + 'd ago';
                    }

                    function formatLabel(filename) {
                        const match = filename.match(/^plot_(\\d{2})(\\d{2})(\\d{2})_(\\d+)\\.(png|html)$/);
                        if (match) {
                            return match[1] + ':' + match[2] + ':' + match[3];
                        }
                        let name = filename.replace(/\\.[^.]+$/, '');
                        if (name.length > 28) name = name.substring(0, 28) + '\u2026';
                        return name;
                    }

                    function refreshActiveFile(f) {
                        const viewer = document.getElementById('main-content');
                        const sideEl = document.getElementById('item-' + f.name);

                        if (sideEl) {
                            sideEl.classList.add('updated');
                        }
                        viewer.classList.add('updated-border');

                        if (flashTimer) clearTimeout(flashTimer);
                        flashTimer = setTimeout(() => {
                            if (sideEl) sideEl.classList.remove('updated');
                            viewer.classList.remove('updated-border');
                        }, 1500);

                        if (f.type === 'plotly') {
                            const iframe = viewer.querySelector('iframe');
                            if (iframe) {
                                let overlay = document.createElement('div');
                                overlay.id = 'temp-overlay';
                                overlay.style = 'position: absolute; inset: 20px; display: flex; justify-content: center; align-items: center; z-index: 5;';
                                if (f.thumb) {
                                    overlay.innerHTML = `<img src="/${f.thumb}?t=${Date.now()}" style="max-width: 100%; max-height: 100%; object-fit: contain; opacity: 0.3; filter: blur(0px); pointer-events: none;"><div class="loader-text" style="position: absolute; color: #fff; text-shadow: 0px 2px 6px rgba(0,0,0,1);">Refreshing...</div>`;
                                } else {
                                    overlay.innerHTML = '<div class="loader-text">Refreshing...</div>';
                                }
                                viewer.appendChild(overlay);
                                iframe.style.visibility = 'hidden';
                                iframe.src = `/${f.name}?t=${Date.now()}`;
                                iframe.onload = () => {
                                    overlay.remove();
                                    iframe.style.visibility = 'visible';
                                };
                            }
                        } else {
                            const img = viewer.querySelector('img');
                            if (img) {
                                img.src = `/${f.name}?t=${Date.now()}`;
                            }
                        }

                        updateAllTimestamps();
                    }

                    function updateAllTimestamps() {
                        currentFiles.forEach(f => {
                            const el = document.getElementById('item-' + f.name);
                            if (!el) return;
                            const ts = el.querySelector('.file-timestamp');
                            if (ts) ts.textContent = timeAgo(f.mtime);
                        });
                        const overlay = document.getElementById('filename-overlay');
                        if (overlay && activeFileName) {
                            const f = currentFiles.find(x => x.name === activeFileName);
                            if (f) {
                                overlay.querySelector('.filename-text').textContent = f.name;
                                const tsEl = overlay.querySelector('.file-timestamp');
                                if (tsEl) tsEl.textContent = 'Updated ' + timeAgo(f.mtime);
                            }
                        }
                    }

                    function loadFiles() {
                        fetch('/api/files')
                            .then(r => r.json())
                            .then(newFiles => {
                                if (JSON.stringify(newFiles) !== JSON.stringify(currentFiles)) {
                                    const wasEmpty = currentFiles.length === 0;
                                    const oldNewestName = !wasEmpty ? currentFiles[currentFiles.length - 1].name : null;
                                    const isAtNewest = !wasEmpty && activeFileName === oldNewestName;

                                    if (!wasEmpty && activeFileName) {
                                        const oldFile = currentFiles.find(cf => cf.name === activeFileName);
                                        const newFile = newFiles.find(nf => nf.name === activeFileName);
                                        if (oldFile && newFile && newFile.mtime > oldFile.mtime) {
                                            refreshActiveFile(newFile);
                                        }
                                    }

                                    syncSidebar(newFiles);

                                    if (newFiles.length > 0) {
                                        const newestFile = newFiles[newFiles.length - 1];
                                        const isNewFileAdded = oldNewestName !== newestFile.name;

                                        if (wasEmpty || (isAtNewest && isNewFileAdded)) {
                                            showFile(newestFile.name);
                                            scrollToBottom();
                                        } else if (activeFileName && !newFiles.find(f => f.name === activeFileName)) {
                                            showFile(newestFile.name);
                                        } else {
                                            let activeFileObj = currentFiles.find(f => f.name === activeFileName);
                                            let overlay = document.getElementById('temp-overlay');
                                            if (activeFileObj && activeFileObj.thumb && overlay && !overlay.querySelector('img')) {
                                                overlay.innerHTML = `
                                                    <img src="/${activeFileObj.thumb}?t=${Date.now()}" style="max-width: 100%; max-height: 100%; object-fit: contain; opacity: 0.3; filter: blur(0px); pointer-events: none;">
                                                    <div class="loader-text" style="position: absolute; color: #fff; text-shadow: 0px 2px 6px rgba(0,0,0,1);">Loading Interactive Plot...</div>
                                                `;
                                            }
                                        }
                                    } else {
                                        activeFileName = null;
                                        document.getElementById('main-content').innerHTML = '<div class="loader-text">Waiting for plots...</div>';
                                        document.getElementById('zoom-controls').style.display = 'none';
                                        document.getElementById('filename-overlay').style.display = 'none';
                                    }

                                    updateAllTimestamps();
                                }
                            });
                    }

                    function syncSidebar(newFiles) {
                        const fl = document.getElementById('file-list');
                        const newNames = newFiles.map(f => f.name);

                        currentFiles.forEach(f => {
                            if (!newNames.includes(f.name)) {
                                let el = document.getElementById('item-' + f.name);
                                if (el) el.remove();
                            }
                        });

                        newFiles.forEach(newFile => {
                            let existingFile = currentFiles.find(cf => cf.name === newFile.name);

                            if (!existingFile) {
                                fl.appendChild(createSidebarItem(newFile));
                            } else if (existingFile.thumb !== newFile.thumb) {
                                let el = document.getElementById('item-' + newFile.name);
                                if (el) {
                                    let thumbContainer = el.querySelector('.thumb-container');
                                    if (thumbContainer) {
                                        if (newFile.thumb) {
                                            thumbContainer.innerHTML = `<img class="thumb-img" src="/${newFile.thumb}?t=${Date.now()}" loading="lazy">`;
                                        } else {
                                            thumbContainer.innerHTML = `<div class="plotly-placeholder">📈<br>Plotly</div>`;
                                        }
                                    }
                                }
                            }
                        });

                        currentFiles = newFiles;

                        newFiles.forEach(f => {
                            let el = document.getElementById('item-' + f.name);
                            if (el) fl.appendChild(el);
                        });
                        scrollToActive();
                    }

                    function createSidebarItem(f) {
                        let div = document.createElement('div');
                        div.className = 'file-item';
                        div.id = 'item-' + f.name;
                        div.onclick = () => showFile(f.name);

                        let thumbHtml = '';
                        if (f.type === 'plotly') {
                            if (f.thumb) {
                                thumbHtml = `<div class="thumb-container"><img class="thumb-img" src="/${f.thumb}?t=${Date.now()}" loading="lazy"></div>`;
                            } else {
                                thumbHtml = `<div class="thumb-container"><div class="plotly-placeholder">📈<br>Plotly</div></div>`;
                            }
                        } else {
                            thumbHtml = `<div class="thumb-container"><img class="thumb-img" src="/${f.name}?t=${Date.now()}" loading="lazy"></div>`;
                        }

                        div.innerHTML = thumbHtml;

                        let label = document.createElement('div');
                        label.className = 'file-label';
                        label.title = f.name;
                        label.textContent = formatLabel(f.name);
                        div.appendChild(label);

                        let timestamp = document.createElement('div');
                        timestamp.className = 'file-timestamp';
                        timestamp.textContent = timeAgo(f.mtime);
                        div.appendChild(timestamp);

                        return div;
                    }

                    function showFile(fileName) {
                        let f = currentFiles.find(x => x.name === fileName);
                        if (!f) return;

                        activeFileName = f.name;

                        const overlay = document.getElementById('filename-overlay');
                        overlay.style.display = 'flex';
                        overlay.querySelector('.filename-text').textContent = f.name;
                        overlay.querySelector('.file-timestamp').textContent = 'Updated ' + timeAgo(f.mtime);

                        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
                        let activeEl = document.getElementById('item-' + f.name);
                        if (activeEl) activeEl.classList.add('active');

                        const viewer = document.getElementById('main-content');
                        const zoomControls = document.getElementById('zoom-controls');

                        if (f.type === 'plotly' && f.thumb) {
                            viewer.innerHTML = `
                                <div id="temp-overlay" style="position: absolute; inset: 20px; display: flex; justify-content: center; align-items: center; z-index: 5;">
                                    <img src="/${f.thumb}?t=${Date.now()}" style="max-width: 100%; max-height: 100%; object-fit: contain; opacity: 0.3; filter: blur(0px); pointer-events: none;">
                                    <div class="loader-text" style="position: absolute; color: #fff; text-shadow: 0px 2px 6px rgba(0,0,0,1);">Loading Interactive Plot...</div>
                                </div>
                            `;
                        } else {
                            viewer.innerHTML = `
                                <div id="temp-overlay" style="position: absolute; inset: 20px; display: flex; justify-content: center; align-items: center; z-index: 5;">
                                    <div class="loader-text">Loading Graph...</div>
                                </div>
                            `;
                        }

                        if (renderTimer) clearTimeout(renderTimer);

                        renderTimer = setTimeout(() => {
                            resetZoom();

                            if (f.type === 'plotly') {
                                zoomControls.style.display = 'none';

                                let iframe = document.createElement('iframe');
                                iframe.src = `/${f.name}`;
                                iframe.setAttribute('sandbox', 'allow-scripts');

                                iframe.style.visibility = 'hidden';

                                iframe.onload = () => {
                                    let overlay = document.getElementById('temp-overlay');
                                    if (overlay) overlay.remove();
                                    iframe.style.visibility = 'visible';
                                };
                                viewer.appendChild(iframe);
                            } else {
                                zoomControls.style.display = 'flex';

                                let img = document.createElement('img');
                                img.src = `/${f.name}?t=${Date.now()}`;
                                img.ondragstart = () => false;

                                let overlay = document.getElementById('temp-overlay');
                                if (overlay) overlay.remove();

                                viewer.appendChild(img);
                            }
                        }, 50);
                    }

                    function clearGallery() {
                        if (confirm("Are you sure you want to clear all plots? This action cannot be undone.")) {
                            fetch('/api/clear', { method: 'POST' }).then(() => {
                                currentFiles = [];
                                activeFileName = null;
                                document.getElementById('file-list').innerHTML = '';
                                document.getElementById('main-content').innerHTML = '<div class="loader-text">Waiting for plots...</div>';
                                document.getElementById('zoom-controls').style.display = 'none';
                                document.getElementById('filename-overlay').style.display = 'none';
                            });
                        }
                    }

                    function scrollToBottom() {
                        const list = document.getElementById('file-list');
                        setTimeout(() => list.scrollTop = list.scrollHeight, 50);
                    }

                    function scrollToActive() {
                        const activeEl = document.querySelector('.file-item.active');
                        if (activeEl) {
                            activeEl.scrollIntoView({ behavior: "auto", block: "nearest" });
                        }
                    }

                    // --- Zoom & Pan Event Listeners ---
                    function updateImageTransform() {
                        const img = document.querySelector('#main-content img');
                        if (img) {
                            img.style.transform = `translate(${imgTranslateX}px, ${imgTranslateY}px) scale(${imgScale})`;
                        }
                    }
                    function changeZoom(delta, mouseX = null, mouseY = null) {
                        const oldScale = imgScale;
                        imgScale += delta;

                        if (imgScale < 0.25) imgScale = 0.25;
                        if (imgScale > 10) imgScale = 10;

                        const ratio = imgScale / oldScale;

                        const mainRect = document.getElementById('main').getBoundingClientRect();
                        const centerX = mainRect.left + mainRect.width / 2;
                        const centerY = mainRect.top + mainRect.height / 2;

                        const targetX = mouseX !== null ? mouseX : centerX;
                        const targetY = mouseY !== null ? mouseY : centerY;

                        imgTranslateX = imgTranslateX * ratio + (targetX - centerX) * (1 - ratio);
                        imgTranslateY = imgTranslateY * ratio + (targetY - centerY) * (1 - ratio);

                        updateImageTransform();
                    }
                    function resetZoom() {
                        imgScale = 1;
                        imgTranslateX = 0;
                        imgTranslateY = 0;
                        updateImageTransform();
                    }
                    document.getElementById('main').addEventListener('wheel', (e) => {
                        if (e.target.tagName === 'IMG') {
                            e.preventDefault();
                            const delta = e.deltaY < 0 ? 0.15 : -0.15;
                            changeZoom(delta, e.clientX, e.clientY);
                        }
                    }, { passive: false });

                    const mainArea = document.getElementById('main');
                    mainArea.addEventListener('mousedown', (e) => {
                        if (e.target.tagName === 'IMG') {
                            isPanning = true;
                            startX = e.clientX - imgTranslateX;
                            startY = e.clientY - imgTranslateY;
                        }
                    });

                    window.addEventListener('mousemove', (e) => {
                        if (!isPanning) return;
                        imgTranslateX = e.clientX - startX;
                        imgTranslateY = e.clientY - startY;
                        updateImageTransform();
                    });

                    window.addEventListener('mouseup', () => {
                        isPanning = false;
                    });

                    // --- Keyboard Navigation ---
                    document.addEventListener('keydown', (e) => {
                        if (!activeFileName || currentFiles.length === 0) return;
                        let idx = currentFiles.findIndex(f => f.name === activeFileName);

                        if (e.key === 'ArrowUp') {
                            e.preventDefault();
                            if (idx > 0) { showFile(currentFiles[idx - 1].name); scrollToActive(); }
                        } else if (e.key === 'ArrowDown') {
                            e.preventDefault();
                            if (idx < currentFiles.length - 1) { showFile(currentFiles[idx + 1].name); scrollToActive(); }
                        }
                    });

                    // --- Sidebar Resizer Logic ---
                    const resizer = document.getElementById('resizer');
                    const sidebar = document.getElementById('sidebar');
                    let isResizing = false;

                    resizer.addEventListener('mousedown', (e) => {
                        isResizing = true;
                        resizer.classList.add('active');
                        document.body.style.cursor = 'col-resize';
                        e.preventDefault();
                    });

                    document.addEventListener('mousemove', (e) => {
                        if (!isResizing) return;

                        let newWidth = e.clientX;
                        if (newWidth < 150) newWidth = 150;
                        if (newWidth > window.innerWidth - 200) newWidth = window.innerWidth - 200;

                        sidebar.style.width = newWidth + 'px';
                    });

                    document.addEventListener('mouseup', () => {
                        if (isResizing) {
                            isResizing = false;
                            resizer.classList.remove('active');
                            document.body.style.cursor = 'default';
                        }
                    });

                    setInterval(loadFiles, 1000);
                    setInterval(updateAllTimestamps, 10000);
                    loadFiles();
                    setTimeout(updateAllTimestamps, 200);
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/api/files":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            all_files = os.listdir(PLOT_DIR)
            pngs = set(f for f in all_files if f.endswith(".png"))
            htmls = set(f for f in all_files if f.endswith(".html"))

            def get_mtime(name):
                try:
                    return os.path.getmtime(os.path.join(PLOT_DIR, name))
                except OSError:
                    return 0

            result = []

            for h in htmls:
                expected_thumb = h.replace(".html", ".png")
                has_thumb = expected_thumb in pngs
                result.append(
                    {
                        "name": h,
                        "type": "plotly",
                        "thumb": expected_thumb if has_thumb else None,
                        "mtime": get_mtime(h),
                    }
                )
                if has_thumb:
                    pngs.remove(expected_thumb)

            for p in pngs:
                result.append(
                    {
                        "name": p,
                        "type": "image",
                        "thumb": None,
                        "mtime": get_mtime(p),
                    }
                )

            result.sort(key=lambda item: item["mtime"])

            self.wfile.write(json.dumps(result).encode("utf-8"))

        else:
            self.path = self.path.split("?")[0]
            super().do_GET()


def main():
    global PLOT_DIR

    parser = argparse.ArgumentParser(description="Plot Gallery")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(tempfile.gettempdir()) / "ipython_plots",
        help="Directory to track",
    )
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")

    args = parser.parse_args()

    PLOT_DIR = args.path
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\U0001f680 Monitoring: {PLOT_DIR}")
    print(f"\U0001f310 Gallery: http://localhost:{args.port}")

    if not args.no_browser:
        webbrowser.open(f"http://localhost:{args.port}")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), GalleryHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\U0001f44b Shutting down gallery...")
        server.server_close()


if __name__ == "__main__":
    main()
