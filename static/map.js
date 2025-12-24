let map = null;
let heatLayer = null;

function initMap() {
    map = L.map('map').setView([54.9985, 83.0084], 17);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 19
    }).addTo(map);
}

async function loadMap() {
    try {
        const dataRes = await fetch('/api/data?limit=1000');
        const data = await dataRes.json();
        
        const statsRes = await fetch('/api/stats');
        const stats = await statsRes.json();
        
        document.getElementById('stats').innerHTML = `Точек: ${stats.total || 0}`;
        
        if (heatLayer) map.removeLayer(heatLayer);
        
        if (data.points && data.points.length > 0) {
            heatLayer = L.heatLayer(data.points, {
                radius: 25,
                blur: 15,
                maxZoom: 17,
                gradient: {
                    0.1: '#FF0000',
                    0.3: '#FF5500',
                    0.5: '#FFAA00',
                    0.7: '#FFFF00',
                    0.85: '#AAFF00',
                    1.0: '#00FF00'
                }
            }).addTo(map);
        }
        
    } catch (error) {
        document.getElementById('stats').innerHTML = "Ошибка";
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadMap();
});