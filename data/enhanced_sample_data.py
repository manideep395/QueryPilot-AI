"""
Enhanced Sample Data Generator for NeuroSQL Testing
Creates comprehensive database with multiple tables and relationships
"""

import sqlite3
import random
from datetime import datetime, timedelta
import json

class EnhancedSampleDataGenerator:
    """Generate comprehensive sample data for testing"""
    
    def __init__(self, db_path="enhanced_database.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Sample data
        self.departments = [
            "Computer Science", "Mathematics", "Physics", "Chemistry", "Biology",
            "Engineering", "Business", "Economics", "Psychology", "Literature"
        ]
        
        self.first_names = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
            "Iris", "Jack", "Kate", "Liam", "Maya", "Noah", "Olivia"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"
        ]
        
        self.course_names = {
            "Computer Science": ["Data Structures", "Algorithms", "Database Systems", "Machine Learning", "Web Development"],
            "Mathematics": ["Calculus", "Linear Algebra", "Statistics", "Discrete Math", "Differential Equations"],
            "Physics": ["Mechanics", "Electromagnetism", "Quantum Physics", "Thermodynamics", "Optics"],
            "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Analytical Chemistry", "Biochemistry"],
            "Biology": ["Cell Biology", "Genetics", "Ecology", "Microbiology", "Anatomy"],
            "Engineering": ["Circuit Design", "Thermodynamics", "Fluid Mechanics", "Materials Science", "Control Systems"],
            "Business": ["Accounting", "Finance", "Marketing", "Management", "Entrepreneurship"],
            "Economics": ["Microeconomics", "Macroeconomics", "International Trade", "Monetary Policy", "Development Economics"]
        }
    
    def create_all_tables(self):
        """Create all database tables"""
        print("🏗️  Creating database tables...")
        
        # Students table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                gpa REAL,
                enrollment_date DATE,
                graduation_year INTEGER,
                department_id INTEGER,
                scholarship_amount REAL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Departments table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                code TEXT UNIQUE NOT NULL,
                head_name TEXT,
                building TEXT,
                budget REAL,
                established_year INTEGER,
                student_count INTEGER DEFAULT 0
            )
        """)
        
        # Courses table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                credits INTEGER,
                department_id INTEGER,
                semester TEXT,
                year INTEGER,
                max_students INTEGER,
                current_students INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        
        # Instructors table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS instructors (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                department_id INTEGER,
                hire_date DATE,
                rank TEXT,
                salary REAL,
                is_tenured BOOLEAN DEFAULT 0,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        
        # Enrollments table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY,
                student_id INTEGER,
                course_id INTEGER,
                instructor_id INTEGER,
                enrollment_date DATE,
                grade REAL,
                attendance_rate REAL,
                final_score REAL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (instructor_id) REFERENCES instructors(id)
            )
        """)
        
        # Assignments table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY,
                course_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                due_date DATE,
                max_score REAL,
                weight REAL,
                assignment_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)
        
        # Submissions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY,
                assignment_id INTEGER,
                student_id INTEGER,
                submission_date TIMESTAMP,
                score REAL,
                feedback TEXT,
                is_late BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)
        
        # Library table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS library_resources (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                isbn TEXT UNIQUE,
                category TEXT,
                publication_year INTEGER,
                available_copies INTEGER,
                total_copies INTEGER,
                location TEXT,
                added_date DATE
            )
        """)
        
        # Borrowing table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowing (
                id INTEGER PRIMARY KEY,
                resource_id INTEGER,
                student_id INTEGER,
                borrow_date DATE,
                due_date DATE,
                return_date DATE,
                fine_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (resource_id) REFERENCES library_resources(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)
        
        print("✅ Database tables created successfully")
    
    def populate_departments(self):
        """Populate departments table"""
        print("📚 Populating departments...")
        
        for i, dept_name in enumerate(self.departments, 1):
            code = dept_name[:3].upper()
            head_name = f"Dr. {random.choice(self.first_names)} {random.choice(self.last_names)}"
            building = f"Building {chr(65 + i % 8)}{i // 8 + 100}"
            budget = random.uniform(500000, 2000000)
            established_year = random.randint(1950, 2000)
            
            self.cursor.execute("""
                INSERT INTO departments (id, name, code, head_name, building, budget, established_year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (i, dept_name, code, head_name, building, budget, established_year))
        
        print(f"✅ {len(self.departments)} departments added")
    
    def populate_students(self, num_students=500):
        """Populate students table"""
        print(f"👨‍🎓 Populating {num_students} students...")
        
        for i in range(1, num_students + 1):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@university.edu"
            age = random.randint(18, 35)
            gpa = round(random.uniform(2.0, 4.0), 2)
            
            # Random enrollment date within last 4 years
            days_ago = random.randint(0, 1460)  # 4 years in days
            enrollment_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            graduation_year = enrollment_date.year + random.randint(3, 6)
            department_id = random.randint(1, len(self.departments))
            scholarship_amount = random.choice([0, 0, 0, 1000, 2500, 5000, 10000])
            
            self.cursor.execute("""
                INSERT INTO students (id, first_name, last_name, email, age, gpa, 
                                 enrollment_date, graduation_year, department_id, scholarship_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, first_name, last_name, email, age, gpa,
                   enrollment_date, graduation_year, department_id, scholarship_amount))
        
        print(f"✅ {num_students} students added")
    
    def populate_instructors(self, num_instructors=100):
        """Populate instructors table"""
        print(f"👨‍🏫 Populating {num_instructors} instructors...")
        
        ranks = ["Assistant Professor", "Associate Professor", "Professor", "Lecturer", "Adjunct Professor"]
        
        for i in range(1, num_instructors + 1):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@university.edu"
            phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            department_id = random.randint(1, len(self.departments))
            
            # Random hire date within last 20 years
            days_ago = random.randint(0, 7300)  # 20 years in days
            hire_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            rank = random.choice(ranks)
            salary = random.uniform(60000, 150000)
            is_tenured = rank in ["Associate Professor", "Professor"] and random.random() > 0.3
            
            self.cursor.execute("""
                INSERT INTO instructors (id, first_name, last_name, email, phone, 
                                    department_id, hire_date, rank, salary, is_tenured)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, first_name, last_name, email, phone, department_id,
                   hire_date, rank, salary, is_tenured))
        
        print(f"✅ {num_instructors} instructors added")
    
    def populate_courses(self, num_courses=200):
        """Populate courses table"""
        print(f"📖 Populating {num_courses} courses...")
        
        semesters = ["Fall", "Spring", "Summer"]
        
        for i in range(1, num_courses + 1):
            department_id = random.randint(1, len(self.departments))
            department_name = self.departments[department_id - 1]
            
            course_list = self.course_names.get(department_name, ["General Course"])
            title = random.choice(course_list)
            code = f"{department_name[:3].upper()}{random.randint(100, 599)}"
            
            description = f"Advanced study of {title.lower()} for undergraduate and graduate students."
            credits = random.choice(1, 2, 3, 4)
            semester = random.choice(semesters)
            year = random.randint(2020, 2024)
            max_students = random.randint(20, 200)
            
            self.cursor.execute("""
                INSERT INTO courses (id, code, title, description, credits, department_id,
                                 semester, year, max_students)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, code, title, description, credits, department_id,
                   semester, year, max_students))
        
        print(f"✅ {num_courses} courses added")
    
    def populate_enrollments(self, num_enrollments=2000):
        """Populate enrollments table"""
        print(f"📝 Populating {num_enrollments} enrollments...")
        
        # Get actual counts from database
        self.cursor.execute("SELECT MAX(id) FROM students")
        max_students = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT MAX(id) FROM courses")
        max_courses = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT MAX(id) FROM instructors")
        max_instructors = self.cursor.fetchone()[0] or 0
        
        for i in range(1, num_enrollments + 1):
            student_id = random.randint(1, max_students)
            course_id = random.randint(1, max_courses)
            instructor_id = random.randint(1, max_instructors)
            
            # Random enrollment date within current semester
            days_ago = random.randint(0, 120)
            enrollment_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            # Random grade (some may be null if course is ongoing)
            if random.random() > 0.3:  # 70% have grades
                grade = round(random.uniform(2.0, 4.0), 2)
                final_score = round(random.uniform(60, 100), 1)
                attendance_rate = round(random.uniform(0.6, 1.0), 2)
            else:
                grade = None
                final_score = None
                attendance_rate = round(random.uniform(0.6, 1.0), 2)
            
            status = "completed" if grade else "active"
            
            self.cursor.execute("""
                INSERT INTO enrollments (id, student_id, course_id, instructor_id,
                                      enrollment_date, grade, attendance_rate, final_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, student_id, course_id, instructor_id, enrollment_date,
                   grade, attendance_rate, final_score, status))
        
        print(f"✅ {num_enrollments} enrollments added")
    
    def populate_library_resources(self, num_resources=1000):
        """Populate library resources table"""
        print(f"📚 Populating {num_resources} library resources...")
        
        categories = ["Textbook", "Reference", "Fiction", "Non-Fiction", "Journal", "Thesis", "Research Paper"]
        
        for i in range(1, num_resources + 1):
            title = f"{' '.join(random.choices(['Advanced', 'Introduction', 'Modern', 'Classic'], k=1))} {' '.join(random.choices(['Science', 'Mathematics', 'Literature', 'History', 'Engineering'], k=1))} Volume {random.randint(1, 10)}"
            author = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
            isbn = f"978-{random.randint(0, 9)}{random.randint(100000000, 999999999)}"
            category = random.choice(categories)
            publication_year = random.randint(1990, 2024)
            total_copies = random.randint(1, 10)
            available_copies = random.randint(0, total_copies)
            location = f"Floor {random.randint(1, 5)}, Section {chr(65 + random.randint(0, 25))}{random.randint(1, 20)}"
            added_date = (datetime.now() - timedelta(days=random.randint(0, 3650))).date()
            
            self.cursor.execute("""
                INSERT INTO library_resources (id, title, author, isbn, category, publication_year,
                                          total_copies, available_copies, location, added_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, title, author, isbn, category, publication_year,
                   total_copies, available_copies, location, added_date))
        
        print(f"✅ {num_resources} library resources added")
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        print("🔧 Creating database indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_students_department ON students(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_email ON students(email)",
            "CREATE INDEX IF NOT EXISTS idx_courses_department ON courses(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_enrollments_instructor ON enrollments(instructor_id)",
            "CREATE INDEX IF NOT EXISTS idx_library_category ON library_resources(category)",
            "CREATE INDEX IF NOT EXISTS idx_borrowing_student ON borrowing(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_borrowing_resource ON borrowing(resource_id)"
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)
        
        print("✅ Database indexes created")
    
    def generate_sample_queries(self):
        """Generate sample queries for testing"""
        print("📝 Generating sample queries...")
        
        queries = {
            "basic_queries": [
                "Show me all students",
                "List all departments",
                "Display all courses",
                "Show all instructors"
            ],
            
            "filtering_queries": [
                "Find students older than 25",
                "Show courses with more than 3 credits",
                "Find instructors with salary greater than 100000",
                "Show students with GPA above 3.5",
                "Find courses offered in Fall semester",
                "Show tenured instructors only"
            ],
            
            "aggregation_queries": [
                "Count the number of students in each department",
                "What is the average GPA of all students?",
                "Find the maximum salary among instructors",
                "Count total courses offered by each department",
                "Calculate average scholarship amount",
                "Find the minimum age of students"
            ],
            
            "join_queries": [
                "Show students and their department names",
                "List courses with instructor names",
                "Show enrollments with student and course details",
                "Find students enrolled in Computer Science courses",
                "Show instructors and their department information"
            ],
            
            "temporal_queries": [
                "Show students enrolled last month",
                "Find courses offered this year",
                "Show instructors hired in the last 5 years",
                "Find library resources added this year",
                "Show enrollments from Fall 2023"
            ],
            
            "comparative_queries": [
                "Find students with GPA between 3.0 and 3.8",
                "Show courses with credits between 2 and 4",
                "Find instructors with salary between 80000 and 120000",
                "Show students with age between 20 and 25",
                "Find library resources published between 2020 and 2024"
            ],
            
            "complex_queries": [
                "Find the top 5 students by GPA in each department",
                "Show departments with more than 50 students",
                "Find instructors with above-average salary in their department",
                "Count students by department and graduation year",
                "Show courses with enrollment rate above 80%",
                "Find students with scholarships above average amount",
                "List departments with total budget over 1 million",
                "Show the most popular courses by enrollment count",
                "Find students with high GPA but no scholarship"
            ],
            
            "ai_enhanced_queries": [
                "What were the enrollment trends last semester?",
                "Compare performance across different departments",
                "Show students with improving academic performance",
                "Find the most productive instructors",
                "Analyze library resource usage patterns",
                "Predict course demand for next semester",
                "Show at-risk students based on performance",
                "Find research trends by publication year",
                "Analyze scholarship distribution effectiveness"
            ]
        }
        
        # Save queries to JSON file
        with open("sample_queries.json", "w") as f:
            json.dump(queries, f, indent=2)
        
        print("✅ Sample queries saved to sample_queries.json")
        
        return queries
    
    def generate_database_statistics(self):
        """Generate and display database statistics"""
        print("\n📊 Database Statistics:")
        
        stats = {}
        
        # Count records in each table
        tables = ["students", "departments", "courses", "instructors", "enrollments", "library_resources"]
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                stats[table] = count
                print(f"  {table.capitalize()}: {count:,} records")
            except:
                print(f"  {table.capitalize()}: Error counting records")
        
        # Department statistics
        self.cursor.execute("""
            SELECT d.name, COUNT(s.id) as student_count, AVG(s.gpa) as avg_gpa
            FROM departments d
            LEFT JOIN students s ON d.id = s.department_id
            GROUP BY d.id, d.name
            ORDER BY student_count DESC
        """)
        
        dept_stats = self.cursor.fetchall()
        print(f"\n  Top 5 departments by student count:")
        for i, (name, count, avg_gpa) in enumerate(dept_stats[:5], 1):
            print(f"    {i}. {name}: {count} students (avg GPA: {avg_gpa:.2f})")
        
        # Course statistics
        self.cursor.execute("""
            SELECT c.title, COUNT(e.id) as enrollment_count, AVG(e.final_score) as avg_score
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY c.id, c.title
            HAVING enrollment_count > 0
            ORDER BY enrollment_count DESC
        """)
        
        course_stats = self.cursor.fetchall()
        print(f"\n  Top 5 courses by enrollment:")
        for i, (title, count, avg_score) in enumerate(course_stats[:5], 1):
            print(f"    {i}. {title}: {count} enrollments (avg score: {avg_score:.1f})")
        
        return stats
    
    def create_comprehensive_database(self):
        """Create the complete enhanced database"""
        print("🚀 Creating Enhanced NeuroSQL Sample Database")
        print("=" * 60)
        
        # Create tables
        self.create_all_tables()
        
        # Populate data
        self.populate_departments()
        self.populate_students(500)
        self.populate_instructors(100)
        self.populate_courses(200)
        self.populate_enrollments(2000)
        self.populate_library_resources(1000)
        
        # Create indexes
        self.create_indexes()
        
        # Generate sample queries
        queries = self.generate_sample_queries()
        
        # Generate statistics
        stats = self.generate_database_statistics()
        
        # Commit changes
        self.conn.commit()
        
        print(f"\n✅ Enhanced database created successfully: {self.db_path}")
        print(f"📊 Total records: {sum(stats.values()):,}")
        print(f"📝 Sample queries: {sum(len(v) for v in queries.values())}")
        
        return stats, queries
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main function to create enhanced sample database"""
    generator = EnhancedSampleDataGenerator()
    
    try:
        stats, queries = generator.create_comprehensive_database()
        
        print(f"\n🎉 Database creation completed!")
        print(f"💾 Database file: {generator.db_path}")
        print(f"📄 Sample queries: sample_queries.json")
        
        print(f"\n📋 Quick Start:")
        print(f"  python enhanced_main.py --database {generator.db_path}")
        print(f"  python enhanced_main.py --web --database {generator.db_path}")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
    finally:
        generator.close()

if __name__ == "__main__":
    main()
