import os
import sqlite3
from datetime import datetime


class GuildDatabase:

    def __init__(self, db_name="guild.db"):
        """初始化資料庫連線並建立所需的資料表"""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """建立成員表與戰力歷史紀錄表"""
        # 1. 成員主要資料表
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                player_id TEXT PRIMARY KEY,
                player_name TEXT NOT NULL,
                current_power INTEGER NOT NULL,
                max_power INTEGER NOT NULL,
                job_title TEXT DEFAULT '一般成員',
                last_updated TEXT NOT NULL
            )
        """
        )

        # 2. 戰力變更歷史紀錄表 (方便追蹤誰在偷懶或爆發式成長)
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS power_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                old_power INTEGER,
                new_power INTEGER NOT NULL,
                change_amount INTEGER NOT NULL,
                update_time TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES members (player_id)
            )
        """
        )
        self.conn.commit()

    def add_member(self, player_id, player_name, current_power, job_title="一般成員"):
        """新增公會成員"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(
                """
                INSERT INTO members (player_id, player_name, current_power, max_power, job_title, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (player_id, player_name, current_power, current_power, job_title, now),
            )
            self.conn.commit()
            print(f"✅ 成功加入成員：[{job_title}] {player_name} (ID: {player_id})")
        except sqlite3.IntegrityError:
            print(f"❌ 錯誤：ID {player_id} 已經存在於公會中！")

    def update_power(self, player_id, new_power):
        """更新成員戰力（核心功能：自動計算歷史最高、幅度並寫入歷史紀錄）"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 先查詢舊資料
        self.cursor.execute(
            "SELECT player_name, current_power, max_power FROM members WHERE player_id = ?",
            (player_id,),
        )
        member = self.cursor.fetchone()

        if not member:
            print(f"❌ 找不到 ID 為 {player_id} 的公會成員。")
            return

        name, old_power, max_power = member
        change_amount = new_power - old_power
        updated_max_power = max(max_power, new_power)

        # 更新主要資料表
        self.cursor.execute(
            """
            UPDATE members 
            SET current_power = ?, max_power = ?, last_updated = ?
            WHERE player_id = ?
        """,
            (new_power, updated_max_power, now, player_id),
        )

        # 寫入歷史紀錄紀錄
        self.cursor.execute(
            """
            INSERT INTO power_history (player_id, old_power, new_power, change_amount, update_time)
            VALUES (?, ?, ?, ?, ?)
        """,
            (player_id, old_power, new_power, change_amount, now),
        )

        self.conn.commit()

        # 輸出友善提示
        trend = "🔺" if change_amount >= 0 else "🔻"
        print(
            f"🔄 戰力更新：{name} -> 當前戰力: {new_power} ({trend} {abs(change_amount)})"
        )
        if new_power > max_power:
            print(f"✨ 恭喜！{name} 突破了歷史最高戰力！")

    def show_guild_report(self):
        """顯示整體的公會成員名單與統計數據"""
        self.cursor.execute(
            "SELECT player_id, player_name, job_title, current_power, max_power FROM members ORDER BY current_power DESC"
        )
        rows = self.cursor.fetchall()

        if not rows:
            print("📭 目前公會資料庫沒有任何成員。")
            return

        print("\n" + "=" * 50)
        print(f"{'職位':<10}{'玩家名稱':<12}{'當前戰力':<10}{'歷史最高':<10}")
        print("-" * 50)
        total_power = 0
        for row in rows:
            print(f"[{row[2]}]{row[1]:<12}{row[3]:<14}{row[4]:<14}")
            total_power += row[3]
        print("-" * 50)
        print(f"📊 公會總戰力：{total_power} | 總人數：{len(rows)} 人")
        print("=" * 50)

    def close(self):
        """關閉資料庫連線"""
        self.conn.close()


# ==================== 🛠️ 測試執行示範 ====================
if __name__ == "__main__":
    # 建立/讀取公會資料庫
    guild = GuildDatabase()

    print("--- 1. 新增公會成員測試 ---")
    guild.add_member("A01", "亞瑟王", 150000, "會長")
    guild.add_member("A02", "梅林", 120000, "副會長")
    guild.add_member("A03", "蘭斯洛特", 98000, "一般成員")

    print("\n--- 2. 初始公會報表 ---")
    guild.show_guild_report()

    print("\n--- 3. 戰力更新測試 ---")
    # 蘭斯洛特大幅變強（超越歷史最高）
    guild.update_power("A03", 135000)
    # 亞瑟王更換裝備暫時降低戰力
    guild.update_power("A01", 148000)

    print("\n--- 4. 更新後的公會報表 ---")
    guild.show_guild_report()

    guild.close()
