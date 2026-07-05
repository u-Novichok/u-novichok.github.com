import { fetchMedia } from './api.js';

async function loadGallery() {
    const grid = document.getElementById('galleryGrid');
    if (!grid) return;

    grid.innerHTML = '<p>Loading images…</p>';

    try {
        const data = await fetchMedia({ limit: 24 });
        const items = data.items || data;
        if (!items || items.length === 0) {
            grid.innerHTML = '<p>No images found. Upload your first image via the admin panel.</p>';
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
    } catch (err) {
        grid.innerHTML = '<p>Could not load images. Please try again later.</p>';
        console.error(err);
    }
}

loadGallery();
