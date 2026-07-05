import { fetchMediaById, fetchMedia } from './api.js';

const urlParams = new URLSearchParams(window.location.search);
const imageId = parseInt(urlParams.get('id')) || 1;

async function loadDetail() {
    try {
        const img = await fetchMediaById(imageId);
        document.title = `${img.title} — Novichok`;

        document.getElementById('detailImage').src = img.cloudinary_url;
        document.getElementById('detailImage').alt = img.title;
        document.getElementById('detailTitle').textContent = img.title;
        document.getElementById('detailDesc').textContent = img.description || '';
        document.getElementById('metaCategory').textContent = img.category || '—';
        document.getElementById('metaCountry').textContent = img.country || '—';
        document.getElementById('metaSource').textContent = img.source || '—';
        document.getElementById('metaDate').textContent = img.capture_date || img.uploaded_at || '—';
        document.getElementById('metaResolution').textContent = img.resolution || '—';

        // Download button
        document.getElementById('downloadBtn').addEventListener('click', () => {
            window.open(img.cloudinary_url, '_blank');
        });

        // Copy Link
        document.getElementById('copyLinkBtn').addEventListener('click', () => {
            navigator.clipboard.writeText(img.cloudinary_url);
            const btn = document.getElementById('copyLinkBtn');
            btn.textContent = 'Copied!';
            setTimeout(() => { btn.textContent = 'Copy Link'; }, 2000);
        });

        // Previous / Next navigation
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

        // Related images (4, excluding current)
        const related = (allData.items || allData).filter(i => i.id !== imageId).slice(0, 4);
        const relatedGrid = document.getElementById('relatedGrid');
        relatedGrid.innerHTML = '';
        related.forEach(r => {
            const card = document.createElement('article');
            card.className = 'gallery-card';
            card.innerHTML = `
                <a href="image.html?id=${r.id}" class="card-link">
                    <div class="card-img-wrap">
                        <img src="${r.cloudinary_url}" alt="${r.title}" loading="lazy" class="card-img">
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
