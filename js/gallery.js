import { fetchMedia } from './api.js';

let autoRefreshInterval = null;

// Helper: generate a transformed thumbnail URL
function thumbnailUrl(originalUrl, mediaType) {
    if (!originalUrl) return '';
    if (mediaType === 'video') {
        // For videos: use the first frame as thumbnail
        return originalUrl.replace('/upload/', '/upload/so_1/')
            .replace(/\.[^/.]+$/, '.jpg');
    }
    return originalUrl.replace('/upload/', '/upload/c_fill,w_400,h_267,q_auto,f_auto/');
}

async function loadGallery() {
    const grid = document.getElementById('galleryGrid');
    if (!grid) return;

    grid.innerHTML = '<p>Loading images…</p>';

    try {
        const data = await fetchMedia({ limit: 24 });
        const items = data.items || data;
        if (!items || items.length === 0) {
            grid.innerHTML = '<p>No media found. Upload your first image via the admin panel.</p>';
            updateTimestamp();
            return;
        }

        grid.innerHTML = '';
        items.forEach(img => {
            const isVideo = img.media_type === 'video';
            const card = document.createElement('article');
            card.className = 'gallery-card';
            card.innerHTML = `
                <a href="image.html?id=${img.id}" class="card-link">
                    <div class="card-img-wrap" style="position:relative;">
                        <img src="${thumbnailUrl(img.cloudinary_url, img.media_type)}" 
                             alt="${img.title}" 
                             loading="lazy" 
                             class="card-img">
                        ${isVideo ? `
                        <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); 
                                    background:rgba(0,0,0,0.7); color:#fff; width:48px; height:48px; 
                                    border-radius:50%; display:flex; align-items:center; justify-content:center;
                                    font-size:20px; pointer-events:none;">
                            ▶
                        </div>` : ''}
                    </div>
                    <div class="card-body">
                        <h3 class="card-title">${isVideo ? '🎬 ' : ''}${img.title}</h3>
                        <p class="card-sub">${img.country || ''} ${img.source ? '• ' + img.source : ''}</p>
                    </div>
                </a>`;
            grid.appendChild(card);
        });
        updateTimestamp();
    } catch (err) {
        grid.innerHTML = '<p>Could not load media. Please try again later.</p>';
        updateTimestamp();
        console.error(err);
    }
}

function updateTimestamp() {
    let refreshBar = document.getElementById('refreshBar');
    if (!refreshBar) {
        refreshBar = document.createElement('div');
        refreshBar.id = 'refreshBar';
        refreshBar.style.cssText = 'text-align:center; margin-top:24px; display:flex; justify-content:center; gap:20px; align-items:center;';
        const grid = document.getElementById('galleryGrid');
        grid.parentNode.insertBefore(refreshBar, grid.nextSibling);
    }
    const now = new Date().toLocaleTimeString();
    refreshBar.innerHTML = `
        <span style="color:#666; font-size:0.85rem;">Last updated: ${now}</span>
        <button id="manualRefreshBtn" style="background:#000; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:bold;">Refresh Now</button>
    `;
    document.getElementById('manualRefreshBtn').addEventListener('click', loadGallery);
}

function startAutoRefresh() {
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
    autoRefreshInterval = setInterval(loadGallery, 60000); // 60 seconds
}

window.addEventListener('beforeunload', () => {
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
});

loadGallery();
startAutoRefresh();
