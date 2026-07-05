import { fetchMedia } from './api.js';

let autoRefreshInterval = null;

async function loadGallery() {
    const grid = document.getElementById('galleryGrid');
    if (!grid) return;

    grid.innerHTML = '<p>Loading images…</p>';

    try {
        const data = await fetchMedia({ limit: 24 });
        const items = data.items || data;
        if (!items || items.length === 0) {
            grid.innerHTML = '<p>No images found. Upload your first image via the admin panel.</p>';
            updateTimestamp();
            return;
        }

        grid.innerHTML = '';
        items.forEach(img => {
            const card = document.createElement('article');
            card.className = 'gallery-card';
            card.innerHTML = `
                <a href="image.html?id=${img.id}" class="card-link">
                    <div class="card-img-wrap">
                        <img src="${img.cloudinary_url || img.thumbnail_url}" 
                             alt="${img.title}" 
                             loading="lazy" 
                             class="card-img">
                    </div>
                    <div class="card-body">
                        <h3 class="card-title">${img.title}</h3>
                        <p class="card-sub">${img.country || ''} ${img.source ? '• ' + img.source : ''}</p>
                    </div>
                </a>`;
            grid.appendChild(card);
        });
        updateTimestamp();
    } catch (err) {
        grid.innerHTML = '<p>Could not load images. Please try again later.</p>';
        updateTimestamp();
        console.error(err);
    }
}

// Create / update the timestamp + refresh button area
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

    document.getElementById('manualRefreshBtn').addEventListener('click', () => {
        loadGallery();
    });
}

// Start auto-refresh (every 30 seconds)
function startAutoRefresh() {
    // Clear any existing interval
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
    autoRefreshInterval = setInterval(loadGallery, 30000); // 30 seconds
}

// Stop auto-refresh when leaving the page
window.addEventListener('beforeunload', () => {
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
});

// Initial load
loadGallery();
startAutoRefresh();
