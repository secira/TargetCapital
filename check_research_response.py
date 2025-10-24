import psycopg2
import os

conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

cur.execute("SELECT id, role, content FROM research_messages WHERE conversation_id = 12 ORDER BY created_at")
rows = cur.fetchall()

for row in rows:
    print(f"\n=== Message ID: {row[0]} ===")
    print(f"Role: {row[1]}")
    print(f"Content: {row[2][:500]}...")
    print(f"Contains BUY: {'BUY' in row[2].upper()}")
    print(f"Contains SELL: {'SELL' in row[2].upper()}")
    print(f"Contains TRADE: {'TRADE' in row[2].upper()}")
    print(f"Contains INVEST: {'INVEST' in row[2].upper()}")

cur.close()
conn.close()
