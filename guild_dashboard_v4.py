import os
import sqlite3


class GuildManager:

    def __init__(self, db_name="guild_simple.db"):
        """連線並初始化資料庫"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                name TEXT PRIMARY KEY,
                power INTEGER NOT NULL
            )
        """
        )
        self.conn.commit()

    def add_member(self, name, power):
        """1. 新增資料"""
        try:
            self.cursor.execute(
                "INSERT INTO members (name, power) VALUES (?, ?)", (name, power)
            )
            self.conn.commit()
            print(f"✅ 成功新增：{name} (戰力: {power})")
        except sqlite3.IntegrityError:
            print(f"❌ 錯誤：成員【{name}】已存在，請使用更新功能。")

    def update_power(self, name, new_power):
        """2. 戰力更新"""
        self.cursor.execute(
            "SELECT power FROM members WHERE name = ?", (name,)
        )
        row = self.cursor.fetchone()

        if row:
            old_power = row[0]
            diff = new_power - old_power
            self.cursor.execute(
                "UPDATE members SET power = ? WHERE name = ?", (new_power, name)
            )
            self.conn.commit()
            trend = f"🔺+{diff}" if diff >= 0 else f"🔻{diff}"
            print(f"🔄 戰力更新：{name} {old_power} ➡️ {new_power} ({trend})")
        else:
            print(f"❌ 找不到成員【{name}】，無法更新戰力。")

    def delete_member(self, name):
        """3. 刪除資料"""
        self.cursor.execute(
            "SELECT name FROM members WHERE name = ?", (name,)
        )
        if self.cursor.fetchone():
            self.cursor.execute("DELETE FROM members WHERE name = ?", (name,))
            self.conn.commit()
            print(f"🗑️  成功刪除成員：{name}")
        else:
            print(f"❌ 找不到成員【{name}】，無法刪除。")

    def show_all(self):
        """4. 顯示所有資料（依戰力由高到低排序）"""
        self.cursor.execute("SELECT name, power FROM members ORDER BY power DESC")
        rows = self.cursor.fetchall()

        print("\n" + "═" * 30)
        print(f"{'成員名稱':<12}{'當前戰力':<10}")
        print("─" * 30)
        if not rows:
            print(" 📭 目前公會空無一人。")
        for row in rows:
            # 修正中文字元排版寬度
            pad = 14 - (len(row[0].encode("big5")) - len(row[0]))
            print(f"{row[0]:<{pad}}{row[1]:<10,}")
        print("═" * 30 + "\n")

    def close(self):
        self.conn.close()


# ==================== 🛠️ 模擬公會操作流程 ====================
if __name__ == "__main__":
    # 清理舊檔案確保測試乾淨
    if os.path.exists("guild_simple.db"):
        os.remove("guild_simple.db")

    guild = GuildManager()

    print("--- 📌 測試 1：新增資料 ---")
    guild.add_member("亞瑟王", 150000)
    guild.add_member("梅林", 120000)
    guild.add_member("蘭斯洛特", 98000)
    guild.show_all()

    print("--- 📌 測試 2：戰力更新 ---")
    guild.update_power("蘭斯洛特", 135000)  # 戰力上升
    guild.update_power("亞瑟王", 148000)  # 戰力下降
    guild.show_all()

    print("--- 📌 測試 3：刪除資料 ---")
    guild.delete_member("梅林")  # 刪除已存在的成員
    guild.delete_member("不存在的玩家")  # 刪除測試
    guild.show_all()

    guild.close()
