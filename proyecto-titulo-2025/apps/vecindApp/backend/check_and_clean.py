import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings

async def check_and_clean_database():
    """Verificar y limpiar la base de datos completamente."""
    
    engine = create_async_engine(settings.database.async_url)
    
    try:
        async with engine.begin() as conn:
            # Verificar qué tablas existen
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'vecindapp'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"📋 Tablas encontradas en schema vecindapp: {tables}")
                
                # Eliminar COMPLETAMENTE el schema
                await conn.execute(text("DROP SCHEMA IF EXISTS vecindapp CASCADE"))
                print("✅ Schema vecindapp eliminado completamente")
            else:
                print("✅ No hay tablas en el schema vecindapp")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_and_clean_database())