import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "geolocation.db"
MAX_POINTS = 10000

def dbm_to_intensity(dbm):
    if dbm is None:
        return 0.1
    
    if dbm > -50:
        dbm = -50
    elif dbm < -120:
        dbm = -120
    
    normalized = (dbm + 120) / 70
    intensity = 0.1 + normalized * 0.9
    
    return max(0.1, min(1.0, intensity))

async def check_and_cleanup():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM signal_data')
        count = (await cursor.fetchone())[0]
        
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

async def init_db():
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
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT latitude, longitude, signal
            FROM signal_data
            WHERE latitude IS NOT NULL
            AND longitude IS NOT NULL
            AND signal IS NOT NULL
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        rows = await cursor.fetchall()
        points = []
        
        for lat, lng, signal in rows:
            intensity = dbm_to_intensity(signal)
            points.append([lat, lng, intensity])
        
        return points

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM signal_data')
        total = (await cursor.fetchone())[0]
        
        return {"total": total}  