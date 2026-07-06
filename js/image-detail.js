import { fetchMediaById, fetchMedia } from './api.js';

const urlParams = new URLSearchParams(window.location.search);
const imageId = parseInt(urlParams.get('id')) || 1;

// URL helpers
function displayUrl(originalUrl, mediaType) {
    if (!originalUrl) return '';
    if (mediaType === 'video') return originalUrl;
    return originalUrl.replace('/upload/', '/upload/q_auto,f_auto,w_1200/');
}

function thumbnailUrl(originalUrl, mediaType) {
    if (!originalUrl) return '';
    if (mediaType === 'video') {
        return originalUrl.replace('/upload/', '/upload/so_1/').replace(/\.[^/.]+$/, '.jpg');
    }
    return originalUrl.replace('/upload/', '/upload/c_fill,w_400,h_267,q_auto,f_auto/');
}

function downloadUrl(originalUrl) { return originalUrl; }

// Popup
function showDownloadPopup(imageUrl, title, callback) {
    const existing = document.getElementById('downloadPopup');
    if (existing) existing.remove();
    const overlay = document.createElement('div');
    overlay.id = 'downloadPopup';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:10000;font-family:Arial,sans-serif;';
    const box = document.createElement('div');
    box.style.cssText = 'background:#fff;padding:30px 25px;border-radius:12px;max-width:450px;width:90%;box-shadow:0 10px 30px rgba(0,0,0,0.3);text-align:center;';
    box.innerHTML = `
        <h3 style="margin-bottom:15px;font-size:1.3rem;">💸 Hosting Costs</h3>
        <p style="margin-bottom:20px;color:#555;font-size:0.95rem;">
            Each download uses our limited bandwidth. You can help us by
            <strong>copying the link</strong> and sharing it instead.<br>
            The media will stay available online.
        </p>
        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
            <button id="popupCopyBtn" style="padding:10px 20px;border:2px solid #000;background:#fff;color:#000;font-weight:bold;border-radius:8px;cursor:pointer;">📋 Copy Link</button>
            <button id="popupDownloadBtn" style="padding:10px 20px;border:none;background:#d32f2f;color:#fff;font-weight:bold;border-radius:8px;cursor:pointer;">⬇️ Download Anyway</button>
        </div>
    `;
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
    document.getElementById('popupCopyBtn').addEventListener('click', () => {
        const shareUrl = `https://novichok-api.onrender.com/share/${imageId}`;
        navigator.clipboard.writeText(shareUrl);
        const btn = document.getElementById('popupCopyBtn');
        btn.textContent = '✅ Copied!';
        // Track share
        fetch('https://novichok-api.onrender.com/api/track/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ media_id: imageId })
        }).catch(()=>{});
        setTimeout(() => { btn.textContent = '📋 Copy Link'; overlay.remove(); }, 1500);
    });
    document.getElementById('popupDownloadBtn').addEventListener('click', () => {
        overlay.remove();
        if (callback) callback();
    });
}

async function performDownload(imageUrl, title) {
    try {
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const ext = (imageUrl.split('.').pop() || 'jpg').split('?')[0];
        const safeTitle = title.replace(/[^a-z0-9]/gi, '_').substring(0, 50);
        const filename = `${safeTitle}.${ext}`;
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
    } catch (err) {
        window.open(imageUrl, '_blank');
    }
}

function buildCarousel(mediaItems, currentId) {
    const detailWrap = document.querySelector('.detail-img-wrap');
    detailWrap.innerHTML = '';
    let currentIndex = mediaItems.findIndex(m => m.id === currentId);
    if (currentIndex < 0) currentIndex = 0;
    const oldStrip = document.getElementById('thumbStrip');
    if (oldStrip) oldStrip.remove();

    function showMedia(index) {
        const item = mediaItems[index];
        detailWrap.innerHTML = '';
        if (item.media_type === 'video') {
            const video = document.createElement('video');
            video.src = item.cloudinary_url;
            video.controls = true;
            video.className = 'detail-img';
            video.style.cssText = 'width:100%;max-height:560px;background:#000;';
            detailWrap.appendChild(video);
        } else {
            const img = document.createElement('img');
            img.src = displayUrl(item.cloudinary_url, item.media_type);
            img.alt = item.title;
            img.className = 'detail-img';
            img.loading = 'lazy';
            detailWrap.appendChild(img);
        }
    }

    showMedia(currentIndex);

    if (mediaItems.length > 1) {
        const thumbStrip = document.createElement('div');
        thumbStrip.id = 'thumbStrip';
        thumbStrip.style.cssText = 'display:flex;gap:8px;margin-top:12px;overflow-x:auto;padding:8px 0;';
        mediaItems.forEach((item, idx) => {
            const thumb = document.createElement('div');
            thumb.style.cssText = `width:80px;height:60px;flex-shrink:0;cursor:pointer;border:${idx===currentIndex?'3px solid #000':'2px solid transparent'};border-radius:6px;overflow:hidden;position:relative;`;
            const img = document.createElement('img');
            img.src = thumbnailUrl(item.cloudinary_url, item.media_type);
            img.alt = item.title;
            img.style.cssText = 'width:100%;height:100%;object-fit:cover;';
            thumb.appendChild(img);
            if (item.media_type === 'video') {
                const icon = document.createElement('div');
                icon.style.cssText = 'position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:#fff;font-size:18px;pointer-events:none;text-shadow:0 0 4px #000;';
                icon.textContent = '▶';
                thumb.appendChild(icon);
            }
            thumb.addEventListener('click', () => {
                showMedia(idx);
                document.querySelectorAll('#thumbStrip > div').forEach((t,i) => t.style.border = i===idx ? '3px solid #000' : '2px solid transparent');
            });
            thumbStrip.appendChild(thumb);
        });
        detailWrap.parentNode.insertBefore(thumbStrip, detailWrap.nextSibling);
    }
}

async function loadDetail() {
    try {
        const img = await fetchMediaById(imageId);
        document.title = `${img.title} — Novichok`;

        // Track media view
        fetch('https://novichok-api.onrender.com/api/track/media-view', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ media_id: imageId })
        }).catch(()=>{});

        let mediaItems = [img];
        if (img.parent_id) {
            try {
                const groupRes = await fetch(`https://novichok-api.onrender.com/groups/${img.parent_id}`);
                if (groupRes.ok) {
                    const groupData = await groupRes.json();
                    mediaItems = groupData.items;
                }
            } catch (e) {}
        }
        buildCarousel(mediaItems, imageId);

        document.getElementById('detailTitle').textContent = img.title;
        document.getElementById('detailDesc').textContent = img.description || '';
        document.getElementById('metaCategory').textContent = img.category || '—';
        document.getElementById('metaCountry').textContent = img.country || '—';
        document.getElementById('metaSource').textContent = img.source || '—';
        document.getElementById('metaDate').textContent = img.capture_date || img.uploaded_at || '—';
        document.getElementById('metaResolution').textContent = img.resolution || '—';

        document.getElementById('downloadBtn').addEventListener('click', () => {
            const mainItem = mediaItems[0];
            showDownloadPopup(downloadUrl(mainItem.cloudinary_url), mainItem.title, () => {
                performDownload(downloadUrl(mainItem.cloudinary_url), mainItem.title);
            });
        });

        document.getElementById('copyLinkBtn').addEventListener('click', () => {
            const shareUrl = `https://novichok-api.onrender.com/share/${imageId}`;
            navigator.clipboard.writeText(shareUrl);
            const btn = document.getElementById('copyLinkBtn');
            btn.textContent = '✅ Copied!';
            // Track share
            fetch('https://novichok-api.onrender.com/api/track/share', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ media_id: imageId })
            }).catch(()=>{});
            setTimeout(() => { btn.textContent = 'Copy Link'; }, 2000);
        });

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

        const related = (allData.items || allData).filter(i => i.id !== imageId && i.parent_id !== img.parent_id).slice(0, 4);
        const relatedGrid = document.getElementById('relatedGrid');
        relatedGrid.innerHTML = '';
        related.forEach(r => {
            const isVideo = r.media_type === 'video';
            const card = document.createElement('article');
            card.className = 'gallery-card';
            card.innerHTML = `
                <a href="image.html?id=${r.id}" class="card-link">
                    <div class="card-img-wrap" style="position:relative;">
                        <img src="${thumbnailUrl(r.cloudinary_url, r.media_type)}" alt="${r.title}" loading="lazy" class="card-img">
                        ${isVideo ? `<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.7);color:#fff;width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;pointer-events:none;">▶</div>` : ''}
                    </div>
                    <div class="card-body">
                        <h3 class="card-title">${isVideo ? '🎬 ' : ''}${r.title}</h3>
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
