const API_BASE = 'https://novichok-api.onrender.com';

export async function fetchMedia({ category, search, skip, limit } = {}) {
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    if (search) params.set('search', search);
    if (skip) params.set('skip', skip);
    if (limit) params.set('limit', limit);
    const res = await fetch(`${API_BASE}/media?${params}`);
    if (!res.ok) throw new Error('Failed to fetch media');
    return res.json();
}

export async function fetchMediaById(id) {
    const res = await fetch(`${API_BASE}/media/${id}`);
    if (!res.ok) throw new Error('Media not found');
    return res.json();
}
