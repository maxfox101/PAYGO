import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import aiofiles
import json

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, backup_dir: str = "/app/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    async def create_database_backup(self, database_url: str) -> Optional[str]:
        """Создание резервной копии базы данных"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"paygo_db_backup_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            # Команда для создания дампа PostgreSQL
            cmd = f"pg_dump {database_url} > {backup_path}"
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ Резервная копия создана: {backup_filename}")
                
                # Создание метаданных
                metadata = {
                    "filename": backup_filename,
                    "created_at": datetime.now().isoformat(),
                    "size_bytes": backup_path.stat().st_size,
                    "type": "database_backup"
                }
                
                metadata_path = backup_path.with_suffix('.json')
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
                
                return str(backup_path)
            else:
                logger.error(f"❌ Ошибка создания резервной копии: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка при создании резервной копии: {e}")
            return None
    
    async def cleanup_old_backups(self, keep_days: int = 30):
        """Удаление старых резервных копий"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("*.sql"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    
                    # Удаляем метаданные
                    metadata_file = backup_file.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    deleted_count += 1
                    logger.info(f"🗑️ Удалена старая резервная копия: {backup_file.name}")
            
            logger.info(f"🧹 Удалено {deleted_count} старых резервных копий")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при очистке старых резервных копий: {e}")
    
    async def schedule_backup(self, interval_hours: int = 24):
        """Планировщик автоматического резервного копирования"""
        while True:
            try:
                await self.create_database_backup("postgresql://paygo_user:paygo_password@database:5432/paygo_db")
                await self.cleanup_old_backups()
                
                # Ждем до следующего бэкапа
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в планировщике резервного копирования: {e}")
                await asyncio.sleep(3600)  # Ждем час при ошибке
    
    def get_backup_list(self) -> list:
        """Получение списка доступных резервных копий"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("*.sql"), key=lambda x: x.stat().st_mtime, reverse=True):
            metadata_file = backup_file.with_suffix('.json')
            
            backup_info = {
                "filename": backup_file.name,
                "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            }
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        backup_info.update(metadata)
                except:
                    pass
            
            backups.append(backup_info)
        
        return backups

