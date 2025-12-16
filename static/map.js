// Глобальные переменные
let map = null;
let heatLayer = null;
const MAX_POINTS = 10000; // ← ДОБАВЬ ЭТО ЗДЕСЬ

// Инициализация карты
function initMap() {
    map = L.map('map').setView([54.9985, 83.0084], 17);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 19
    }).addTo(map);
}

// Загрузка данных и отрисовка
async function loadMap() {
    try {
        console.log("🔄 Загрузка данных...");
        
        // 1. Получаем статистику
        const statsRes = await fetch('/api/stats');
        const stats = await statsRes.json();
        
        // 2. Получаем точки
        const dataRes = await fetch('/api/data?limit=1000');
        const data = await dataRes.json();
        
        // 3. Вычисляем проценты (даже если API не вернул)
        const total = stats.total || 0;
        const percent = Math.round((total / MAX_POINTS) * 100 * 10) / 10;
        let color = "#4CAF50";
        if (percent > 90) color = "#FF5722";
        if (percent > 95) color = "#F44336";
        
        // 4. Обновляем статистику
        document.getElementById('stats').innerHTML = `
            <strong>База данных:</strong><br>
            📊 Всего записей: ${total}/${MAX_POINTS}<br>
            📍 С координатами: ${stats.with_coordinates || 0}<br>
            🎯 Показано: ${data.points?.length || 0} точек<br>
            📁 Заполнено: <span style="color: ${color}">${percent}%</span>
        `;
        
        // 5. Обновляем карту
        if (heatLayer) map.removeLayer(heatLayer);
        
        if (data.points && data.points.length > 0) {
            heatLayer = L.heatLayer(data.points, {
                radius: 25, blur: 15,
                gradient: {0.2: 'blue', 0.5: 'cyan', 0.7: 'lime', 1.0: 'red'}
            }).addTo(map);
        }
        
    } catch (error) {
        console.error("❌ Ошибка:", error);
        document.getElementById('stats').innerHTML = "❌ Ошибка загрузки";
    }
}

// Очистка карты
function clearMap() {
    if (heatLayer) {
        map.removeLayer(heatLayer);
        heatLayer = null;
        document.getElementById('stats').innerHTML = "Карта очищена";
    }
}

// Запуск
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadMap();
    setInterval(loadMap, 30000);
});