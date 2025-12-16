import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "geolocation.db"
MAX_POINTS = 10000  

async def check_and_cleanup():
    """Проверяем и удаляем старые точки если больше MAX_POINTS"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Считаем сколько всего
        cursor = await db.execute('SELECT COUNT(*) FROM signal_data')
        count = (await cursor.fetchone())[0]
        
        # Если больше лимита - удаляем старые
        if count > MAX_POINTS:
            to_delete = count - MAX_POINTS
            await db.execute(f'''
                DELETE FROM signal_data
                WHERE id IN (
                    SELECT id FROM signal_data
                    ORDER BY timestamp ASC
                    LIMIT {to_delete}
                )
            ''')
            await db.commit()
            print(f"🗑️ Удалено {to_delete} старых точек")

async def init_db():
    """Создание таблицы если нет"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS signal_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp BIGINT NOT NULL,
                signal INTEGER,
                latitude REAL,
                longitude REAL,
                accuracy REAL,
                speed REAL,
                device TEXT,
                android_version INTEGER,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def save_point(data: dict):
    """Сохранение точки в БД"""
    # ДОБАВЛЯЕМ ОЧИСТКУ ПЕРЕД СОХРАНЕНИЕМ
    await check_and_cleanup()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO signal_data
            (timestamp, signal, latitude, longitude, accuracy, speed, device, android_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp'),
            data.get('signal'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('accuracy'),
            data.get('speed'),
            data.get('device'),
            data.get('android_version')
        ))
        await db.commit()
        return True

async def get_points(limit: int = 1000):
    """Получение точек для карты"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT latitude, longitude, signal
            FROM signal_data
            WHERE latitude IS NOT NULL
            AND longitude IS NOT NULL
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        rows = await cursor.fetchall()
        points = []
        
        for lat, lng, signal in rows:
            intensity = (signal or 1) / 5.0  # 0.2 - 1.0
            points.append([lat, lng, intensity])
        
        return points

async def get_stats():
    """Статистика по данным"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM signal_data')
        total = (await cursor.fetchone())[0]
        
        cursor = await db.execute('SELECT COUNT(*) FROM signal_data WHERE latitude IS NOT NULL')
        with_coords = (await cursor.fetchone())[0]
        
        # ВЫЧИСЛЯЕМ ПРОЦЕНТ ЗАПОЛНЕНИЯ
        if MAX_POINTS > 0:
            percent_full = round((total / MAX_POINTS) * 100, 1)
        else:
            percent_full = 0
        
        return {
            "total": total,
            "with_coordinates": with_coords,
            "max_points": MAX_POINTS,  # ← ВОТ ЭТО ВАЖНО!
            "percent_full": percent_full,  # ← И ЭТО!
            "database_file": str(DB_PATH.name)
        }