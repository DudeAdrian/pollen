"""
Shadow Accumulator - Pre-Wallet Honey Tracking
Level 1 accumulation before graduation to full wallet
Manages graduation ceremony trigger
"""

import asyncio
import json
import logging
import sqlite3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from ..config import get_settings
from ..utils.encryptor import DataEncryptor

logger = logging.getLogger(__name__)


class ActivityType(Enum):
    WELLNESS = "wellness"
    CREATIVE = "creative"
    SOCIAL = "social"
    TECHNICAL = "technical"
    COMMUNITY = "community"


@dataclass
class ShadowEntry:
    """Single shadow balance entry"""
    entry_id: str
    activity_type: ActivityType
    description: str
    honey_value: float
    proof_hash: str
    timestamp: str
    validated: bool = False


class ShadowAccumulator:
    """
    Tracks Honey accumulation before wallet creation (Level 1).
    Triggers graduation ceremony when threshold reached.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = Path(self.settings.SHADOW_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.encryptor = DataEncryptor()
        self._conn: Optional[sqlite3.Connection] = None
        self._graduation_callbacks: List[callable] = []
        
    async def initialize(self):
        """Initialize shadow database"""
        logger.info("👤 Initializing Shadow Accumulator (Level 1)")
        
        self._conn = sqlite3.connect(str(self.db_path))
        self._create_tables()
        
        logger.info("✅ Shadow Accumulator initialized")
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self._conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shadow_entries (
                entry_id TEXT PRIMARY KEY,
                activity_type TEXT NOT NULL,
                description TEXT,
                honey_value REAL NOT NULL,
                proof_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                validated BOOLEAN DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS graduation_status (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                level INTEGER DEFAULT 1,
                total_honey REAL DEFAULT 0,
                threshold INTEGER DEFAULT 1000,
                graduated BOOLEAN DEFAULT 0,
                graduation_time TEXT,
                wallet_address TEXT
            )
        """)
        
        # Initialize status row if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO graduation_status (id, level, threshold)
            VALUES (1, 1, ?)
        """, (self.settings.SHADOW_HONEY_THRESHOLD,))
        
        self._conn.commit()
    
    async def add_entry(
        self,
        activity_type: ActivityType,
        description: str,
        honey_value: float,
        proof_hash: str
    ) -> ShadowEntry:
        """
        Add a new shadow entry
        
        Args:
            activity_type: Type of activity
            description: Human-readable description
            honey_value: Amount of Honey earned
            proof_hash: Zero-knowledge proof hash
        """
        entry = ShadowEntry(
            entry_id=f"shadow_{datetime.utcnow().timestamp()}",
            activity_type=activity_type,
            description=description,
            honey_value=honey_value,
            proof_hash=proof_hash,
            timestamp=datetime.utcnow().isoformat(),
            validated=False
        )
        
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO shadow_entries 
            (entry_id, activity_type, description, honey_value, proof_hash, timestamp, validated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.entry_id,
            entry.activity_type.value,
            entry.description,
            entry.honey_value,
            entry.proof_hash,
            entry.timestamp,
            entry.validated
        ))
        
        # Update total
        cursor.execute("""
            UPDATE graduation_status 
            SET total_honey = total_honey + ?
            WHERE id = 1
        """, (entry.honey_value,))
        
        self._conn.commit()
        
        logger.info(f"➕ Shadow entry added: {activity_type.value} (+{honey_value} Honey)")
        
        # Check graduation threshold
        await self._check_graduation()
        
        return entry
    
    async def validate_entry(self, entry_id: str) -> bool:
        """Mark entry as validated by Hive consensus"""
        cursor = self._conn.cursor()
        cursor.execute("""
            UPDATE shadow_entries SET validated = 1 WHERE entry_id = ?
        """, (entry_id,))
        self._conn.commit()
        
        return cursor.rowcount > 0
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get current shadow balance"""
        cursor = self._conn.cursor()
        
        # Get total
        cursor.execute("""
            SELECT total_honey, threshold, graduated, level
            FROM graduation_status WHERE id = 1
        """)
        row = cursor.fetchone()
        
        if not row:
            return {"error": "Status not initialized"}
        
        total, threshold, graduated, level = row
        
        # Get breakdown by type
        cursor.execute("""
            SELECT activity_type, SUM(honey_value), COUNT(*)
            FROM shadow_entries
            WHERE validated = 1
            GROUP BY activity_type
        """)
        
        breakdown = {}
        for row in cursor.fetchall():
            breakdown[row[0]] = {
                "total": round(row[1], 2),
                "count": row[2]
            }
        
        # Get pending (not yet validated)
        cursor.execute("""
            SELECT SUM(honey_value), COUNT(*)
            FROM shadow_entries
            WHERE validated = 0
        """)
        pending_row = cursor.fetchone()
        pending_value = pending_row[0] or 0
        pending_count = pending_row[1] or 0
        
        return {
            "level": level,
            "total_honey": round(total, 2),
            "validated_honey": round(total - pending_value, 2),
            "pending_honey": round(pending_value, 2),
            "pending_count": pending_count,
            "threshold": threshold,
            "progress_percent": round((total / threshold) * 100, 1),
            "graduated": bool(graduated),
            "breakdown_by_type": breakdown,
            "can_graduate": total >= threshold and not graduated
        }
    
    async def _check_graduation(self):
        """Check if graduation threshold reached"""
        balance = await self.get_balance()
        
        if balance["can_graduate"]:
            logger.info("🎓 GRADUATION THRESHOLD REACHED!")
            logger.info(f"   Total Honey: {balance['total_honey']}")
            logger.info(f"   Threshold: {balance['threshold']}")
            
            if self.settings.GRADUATION_AUTO_ENABLED:
                await self.trigger_graduation()
            else:
                logger.info("   Auto-graduation disabled. Manual ceremony required.")
            
            # Notify callbacks
            for callback in self._graduation_callbacks:
                try:
                    await callback(balance)
                except Exception as e:
                    logger.error(f"Graduation callback error: {e}")
    
    async def trigger_graduation(self) -> Dict[str, Any]:
        """
        Trigger graduation ceremony (Level 1 → 2)
        Creates wallet, transfers shadow balance
        """
        logger.info("🎓 INITIATING GRADUATION CEREMONY")
        
        # 1. Verify threshold
        balance = await self.get_balance()
        if not balance["can_graduate"]:
            raise ValueError("Graduation threshold not reached")
        
        # 2. Generate wallet address (would integrate with Terracare Ledger)
        wallet_address = f"0x{self.encryptor.hash_data(str(datetime.utcnow().timestamp()))[:40]}"
        
        # 3. Update status
        cursor = self._conn.cursor()
        cursor.execute("""
            UPDATE graduation_status
            SET graduated = 1,
                graduation_time = ?,
                wallet_address = ?,
                level = 2
            WHERE id = 1
        """, (datetime.utcnow().isoformat(), wallet_address))
        self._conn.commit()
        
        # 4. Create graduation record
        graduation_record = {
            "ceremony_type": "level_1_to_2",
            "timestamp": datetime.utcnow().isoformat(),
            "previous_level": 1,
            "new_level": 2,
            "honey_transferred": balance["total_honey"],
            "wallet_address": wallet_address,
            "shadow_entries_count": await self._get_entry_count()
        }
        
        logger.info(f"✅ Graduation complete! Wallet: {wallet_address}")
        logger.info(f"   Transferred: {balance['total_honey']} Honey")
        
        return graduation_record
    
    async def _get_entry_count(self) -> int:
        """Get total number of shadow entries"""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM shadow_entries")
        return cursor.fetchone()[0]
    
    async def get_history(
        self,
        activity_type: Optional[ActivityType] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get shadow entry history"""
        cursor = self._conn.cursor()
        
        if activity_type:
            cursor.execute("""
                SELECT entry_id, activity_type, description, honey_value, 
                       proof_hash, timestamp, validated
                FROM shadow_entries
                WHERE activity_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (activity_type.value, limit))
        else:
            cursor.execute("""
                SELECT entry_id, activity_type, description, honey_value,
                       proof_hash, timestamp, validated
                FROM shadow_entries
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                "entry_id": row[0],
                "activity_type": row[1],
                "description": row[2],
                "honey_value": row[3],
                "proof_hash": row[4][:16] + "...",  # Truncated for display
                "timestamp": row[5],
                "validated": bool(row[6])
            })
        
        return entries
    
    def on_graduation_ready(self, callback: callable):
        """Register callback for when graduation threshold reached"""
        self._graduation_callbacks.append(callback)
    
    async def export_for_wallet_creation(self) -> Dict[str, Any]:
        """Export all validated entries for wallet creation ceremony"""
        cursor = self._conn.cursor()
        
        cursor.execute("""
            SELECT entry_id, activity_type, honey_value, proof_hash, timestamp
            FROM shadow_entries
            WHERE validated = 1
            ORDER BY timestamp
        """)
        
        entries = []
        total = 0
        for row in cursor.fetchall():
            entries.append({
                "entry_id": row[0],
                "activity_type": row[1],
                "honey_value": row[2],
                "proof_hash": row[3],
                "timestamp": row[4]
            })
            total += row[2]
        
        return {
            "entries": entries,
            "total_honey": round(total, 2),
            "entry_count": len(entries),
            "export_timestamp": datetime.utcnow().isoformat(),
            "merkle_root": self._calculate_merkle_root(entries)
        }
    
    def _calculate_merkle_root(self, entries: List[Dict]) -> str:
        """Calculate merkle root of all entries"""
        if not entries:
            return "0" * 64
        
        # Simple hash chain (in production, use proper merkle tree)
        combined = "".join(e["proof_hash"] for e in entries)
        return self.encryptor.hash_data(combined)
    
    async def close(self):
        """Cleanup resources"""
        if self._conn:
            self._conn.close()
            logger.info("👤 Shadow Accumulator shut down")
