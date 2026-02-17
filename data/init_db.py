import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    marks INTEGER
)
""")

# Insert sample data
cursor.execute("DELETE FROM students")

students = [
    (1, "Alice", 20, 85),
    (2, "Bob", 21, 70),
    (3, "Charlie", 22, 90),
    (4, "Dhatri", 20, 95)
]

cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?)", students)

conn.commit()
conn.close()

print("Database initialized successfully!")
