import { fetchMediaById, fetchMedia } from './api.js';

const urlParams = new URLSearchParams(window.location.search);
const imageId = parseInt(urlParams.get('id')) || 1;

// Helper: optimized display version
function displayUrl(originalUrl) {
    return originalUrl.replace('/upload/', '/upload/q_auto,f_auto,w_1200/');
}

// Helper: thumbnail for related images
function thumbnailUrl(originalUrl) {
    return originalUrl.replace('/upload/', '/upload/c_fill,w_400,h_267,q_auto,f_auto/');
}

// Helper: download version (original)
function downloadUrl(originalUrl) {
    return originalUrl;
}

// ──────────────────────────────────────────────
// MODAL POPUP – shown before actual download
// ──────────────────────────────────────────────
function showDownloadPopup(imageUrl, title, callback) {
    // Remove any existing popup
    const existing = document.getElementById('downloadPopup');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'downloadPopup';
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); display: flex; align-items: center;
        justify-content: center; z-index: 10000; font-family: Arial, sans-serif;
    `;

    const box = document.createElement('div');
    box.style.cssText = `
        background: #fff; padding: 30px 25px; border-radius: 12px;
        max-width: 450px; width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        text-align: center;
    `;

    box.innerHTML = `
        <h3 style="margin-bottom: 15px; font-size: 1.3rem;">Hosting costs 💸</h3>
        <p style="margin-bottom: 20px; color: #555; font-size: 0.95rem;">
            Each download uses our free bandwidth. You can help us by <strong>copying the link</strong>
            and sharing the page instead. The image stays available online.
        </p>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <button id="popupCopyBtn" style="
                padding: 10px 20px; border: 2px solid #000; background: #fff;
                color: #000; font-weight: bold; border-radius: 8px; cursor: pointer;
                transition: 0.2s;
            ">📋 Copy Link</button>
            <button id="popupDownloadBtn" style="
                padding: 10px 20px; border: none; background: #d32f2f;
                color: #fff; font-weight: bold; border-radius: 8px; cursor: pointer;
                transition: 0.2s;
            ">⬇️ Download Anyway</button>
        </div>
    `;

    overlay.appendChild(box);
    document.body.appendChild(overlay);

    // Close overlay if clicked outside box
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    });

    // Popup Copy Link → copies the page URL
    document.getElementById('popupCopyBtn').addEventListener('click', () => {
        navigator.clipboard.writeText(window.location.href);
        // Brief visual feedback
        const btn = document.getElementById('popupCopyBtn');
        btn.textContent = '✅ Copied!';
        setTimeout(() => {
            btn.textContent = '📋 Copy Link';
            overlay.remove();
        }, 1500);
    });

    // Popup Download → run actual download and close popup
    document.getElementById('popupDownloadBtn').addEventListener('click', () => {
        overlay.remove();
        if (callback) callback();
    });
}

// ──────────────────────────────────────────────
// ACTUAL DOWNLOAD LOGIC
// ──────────────────────────────────────────────
async function performDownload(imageUrl, title) {
    try {
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);

        const extension = (imageUrl.split('.').pop() || 'jpg').split('?')[0];
        const safeTitle = title.replace(/[^a-z0-9]/gi, '_').substring(0, 50);
        const filename = `${safeTitle}.${extension}`;

        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
    } catch (err) {
        // Fallback – open in new tab
        window.open(imageUrl, '_blank');
    }
}

// ──────────────────────────────────────────────
// MAIN PAGE LOAD
// ──────────────────────────────────────────────
async function loadDetail() {
    try {
        const img = await fetchMediaById(imageId);
        document.title = `${img.title} — Novichok`;

        document.getElementById('detailImage').src = displayUrl(img.cloudinary_url);
        document.getElementById('detailImage').alt = img.title;
        document.getElementById('detailTitle').textContent = img.title;
        document.getElementById('detailDesc').textContent = img.description || '';
        document.getElementById('metaCategory').textContent = img.category || '—';
        document.getElementById('metaCountry').textContent = img.country || '—';
        document.getElementById('metaSource').textContent = img.source || '—';
        document.getElementById('metaDate').textContent = img.capture_date || img.uploaded_at || '—';
        document.getElementById('metaResolution').textContent = img.resolution || '—';

        // ── DOWNLOAD BUTTON (with popup) ──
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.addEventListener('click', () => {
            showDownloadPopup(downloadUrl(img.cloudinary_url), img.title, () => {
                performDownload(downloadUrl(img.cloudinary_url), img.title);
            });
        });

        // ── COPY LINK BUTTON (copies page URL, not image URL) ──
        const copyBtn = document.getElementById('copyLinkBtn');
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(window.location.href);
            copyBtn.textContent = '✅ Copied!';
            setTimeout(() => { copyBtn.textContent = 'Copy Link'; }, 2000);
        });

        // ── PREVIOUS / NEXT ──
        const allData = await fetchMedia({ limit: 100 });
        const ids = allData.items ? allData.items.map(i => i.id) : allData.map(i => i.id);
        const currentIndex = ids.indexOf(imageId);

        document.getElementById('prevBtn').addEventListener('click', () => {
            const newIndex = currentIndex > 0 ? currentIndex - 1 : ids.length - 1;
            window.location.href = `image.html?id=${ids[newIndex]}`;
        });
        document.getElementById('nextBtn').addEventListener('click', () => {
            const newIndex = currentIndex < ids.length - 1 ? currentIndex + 1 : 0;
            window.location.href = `image.html?id=${ids[newIndex]}`;
        });

        // ── RELATED IMAGES ──
        const related = (allData.items || allData).filter(i => i.id !== imageId).slice(0, 4);
        const relatedGrid = document.getElementById('relatedGrid');
        relatedGrid.innerHTML = '';
        related.forEach(r => {
            const card = document.createElement('article');
            card.className = 'gallery-card';
            card.innerHTML = `
                <a href="image.html?id=${r.id}" class="card-link">
                    <div class="card-img-wrap">
                        <img src="${thumbnailUrl(r.cloudinary_url)}" alt="${r.title}" loading="lazy" class="card-img">
                    </div>
                    <div class="card-body">
                        <h3 class="card-title">${r.title}</h3>
                        <p class="card-sub">${r.country || ''} ${r.source ? '• ' + r.source : ''}</p>
                    </div>
                </a>`;
            relatedGrid.appendChild(card);
        });

    } catch (err) {
        console.error('Error loading image:', err);
        document.body.innerHTML += '<p style="text-align:center">Could not load image details.</p>';
    }
}

loadDetail();
