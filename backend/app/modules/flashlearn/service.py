from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Flashcard
from typing import Optional
import random


class FlashLearnService:
    """Service for managing flashcards and study sessions"""

    @staticmethod
    def get_flashcards(db: Session, topic: Optional[str] = None, company: Optional[str] = None, limit: int = 10):
        """Get flashcards with optional filters"""
        query = db.query(Flashcard)
        if topic:
            query = query.filter(Flashcard.topic == topic)
        if company:
            query = query.filter(Flashcard.company == company)
        return query.limit(limit).all()

    @staticmethod
    def get_random_flashcards(db: Session, count: int = 10, difficulty: Optional[str] = None, topic: Optional[str] = None, company: Optional[str] = None):
        """Get random flashcards for study, optionally filtered by topic and company"""
        query = db.query(Flashcard.id)
        if difficulty:
            query = query.filter(Flashcard.difficulty == difficulty)
        if topic:
            query = query.filter(Flashcard.topic == topic)
        if company:
            query = query.filter(Flashcard.company == company)

        all_ids = [row[0] for row in query.all()]
        if not all_ids:
            return []
        selected_ids = random.sample(all_ids, min(count, len(all_ids)))
        return db.query(Flashcard).filter(Flashcard.id.in_(selected_ids)).all()

    @staticmethod
    def get_flashcard_by_id(db: Session, flashcard_id: int):
        return db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()

    @staticmethod
    def create_flashcard(db: Session, question: str, answer: str, topic: str,
                         company: Optional[str] = None, difficulty: str = "medium"):
        flashcard = Flashcard(question=question, answer=answer, topic=topic,
                              company=company, difficulty=difficulty)
        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)
        return flashcard

    @staticmethod
    def get_topics(db: Session):
        return [r[0] for r in db.query(Flashcard.topic).distinct().all() if r[0]]

    @staticmethod
    def get_companies(db: Session):
        return [r[0] for r in db.query(Flashcard.company).filter(Flashcard.company != None).distinct().all()]

    @staticmethod
    def seed_flashcards(db: Session):
        """Seed database with 120+ categorized flashcards across companies & topics"""
        sample_cards = [

            # ══════════════════════════════════════
            # TCS — APTITUDE (20 cards)
            # ══════════════════════════════════════
            {"question": "What is the square root of 256?", "answer": "16 (16×16 = 256)", "topic": "Aptitude", "company": "TCS", "difficulty": "easy"},
            {"question": "If a person can complete a task in 10 days and another in 15 days, how long will they take working together?", "answer": "6 days. LCM approach: 1/10 + 1/15 = 5/30, so 30/5 = 6 days.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "A train 200m long is running at 72 km/h. How long will it take to pass a platform 300m long?", "answer": "25 seconds. Total distance = 500m, Speed = 72 km/h = 20 m/s. Time = 500/20 = 25s.", "topic": "Aptitude", "company": "TCS", "difficulty": "hard"},
            {"question": "A can do work in 12 days, B in 18 days. They work together for 6 days, then A leaves. How many more days does B need?", "answer": "6 days. Together in 6 days: 6(1/12+1/18) = 6×5/36 = 5/6. Remaining = 1/6. B alone: (1/6)/(1/18) = 3 days.", "topic": "Aptitude", "company": "TCS", "difficulty": "hard"},
            {"question": "If 20% of a number is 80, what is 30% of that number?", "answer": "120. Number = 80/0.20 = 400. 30% of 400 = 120.", "topic": "Aptitude", "company": "TCS", "difficulty": "easy"},
            {"question": "A shopkeeper sells an item at Rs. 520 with a 30% profit. What is the cost price?", "answer": "Rs. 400. CP = 520/1.30 = 400.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "Find the next in series: 2, 6, 12, 20, 30, ?", "answer": "42. Pattern: differences are 4,6,8,10,12. So 30+12=42.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "Three numbers are in ratio 1:2:3. Their HCF is 12. What is their LCM?", "answer": "72. Numbers: 12, 24, 36. LCM(12,24,36)=72.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "A boat travels 30km upstream in 3 hrs, 30km downstream in 2 hrs. Find speed of boat in still water.", "answer": "12.5 km/h. Upstream=10, Downstream=15. Boat speed=(10+15)/2=12.5.", "topic": "Aptitude", "company": "TCS", "difficulty": "hard"},
            {"question": "Two dice are rolled. What is the probability of getting a sum of 7?", "answer": "1/6. Favorable outcomes:(1,6)(2,5)(3,4)(4,3)(5,2)(6,1) = 6 out of 36.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "Simple interest for Rs. 5000 at 8% per annum for 3 years?", "answer": "Rs. 1200. SI = (5000×8×3)/100 = 1200.", "topic": "Aptitude", "company": "TCS", "difficulty": "easy"},
            {"question": "The ratio of boys to girls in a class is 5:3. If there are 40 students, how many girls are there?", "answer": "15 girls. Girls = 40×(3/8) = 15.", "topic": "Aptitude", "company": "TCS", "difficulty": "easy"},
            {"question": "If APPLE = 50 in some code, what does MANGO = ?", "answer": "Depends on encoding. In A=1 to Z=26: MANGO=13+1+14+7+15=50. So MANGO=50 as well.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "Divide Rs. 1500 among A, B, C in ratio 3:4:8. How much does C get?", "answer": "Rs. 800. C gets 8/15 × 1500 = 800.", "topic": "Aptitude", "company": "TCS", "difficulty": "easy"},
            {"question": "Find the greatest 4-digit number divisible by 24, 36, and 48.", "answer": "9936. LCM(24,36,48)=144. 9999÷144=69.4, so 69×144=9936.", "topic": "Aptitude", "company": "TCS", "difficulty": "hard"},
            {"question": "What is 15% of 15% of 600?", "answer": "13.5. 15% of 600=90. 15% of 90=13.5.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "Clock Problem: What is the angle between the hour and minute hands at 3:40?", "answer": "130°. Minute hand at 40×6=240°. Hour hand at 3×30+40×0.5=110°. Difference=130°.", "topic": "Aptitude", "company": "TCS", "difficulty": "hard"},
            {"question": "Pipe A fills a tank in 6 hours, Pipe B drains in 12 hours. How long to fill if both open?", "answer": "12 hours. Net rate = 1/6 - 1/12 = 1/12. Time = 12 hours.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "Find the compound interest on Rs. 10,000 at 10% per annum for 2 years.", "answer": "Rs. 2100. A=10000×(1.1)²=12100. CI=12100-10000=2100.", "topic": "Aptitude", "company": "TCS", "difficulty": "medium"},
            {"question": "In 1 km race, A beats B by 40m. In 1 km race, B beats C by 50m. By how much does A beat C in 1 km?", "answer": "Approx 88m. When A runs 1000m, B runs 960m. When B runs 1000m, C runs 950m. C runs 960×950/1000=912m. A beats C by 88m.", "topic": "Aptitude", "company": "TCS", "difficulty": "hard"},

            # ══════════════════════════════════════
            # TCS — CODING (10 cards)
            # ══════════════════════════════════════
            {"question": "What is the output of: x = [1,2,3]; print(x*2)?", "answer": "[1,2,3,1,2,3] — The * operator on a list repeats it, it does NOT multiply elements.", "topic": "Coding", "company": "TCS", "difficulty": "easy"},
            {"question": "Write a program to check if a number is palindrome.", "answer": "n=int(input()); print(str(n)==str(n)[::-1]). Reverses the string and compares.", "topic": "Coding", "company": "TCS", "difficulty": "easy"},
            {"question": "What is the time complexity of Binary Search?", "answer": "O(log n) — Each step halves the search space.", "topic": "Coding", "company": "TCS", "difficulty": "easy"},
            {"question": "What is the difference between a stack and a queue?", "answer": "Stack is LIFO (Last In First Out). Queue is FIFO (First In First Out). Stack uses push/pop, Queue uses enqueue/dequeue.", "topic": "Coding", "company": "TCS", "difficulty": "easy"},
            {"question": "What does SQL SELECT DISTINCT do?", "answer": "Returns only unique/distinct rows, eliminating duplicates from results.", "topic": "Coding", "company": "TCS", "difficulty": "easy"},
            {"question": "Write a function to find the factorial of a number recursively.", "answer": "def fact(n): return 1 if n<=1 else n*fact(n-1). Base case: fact(0)=fact(1)=1.", "topic": "Coding", "company": "TCS", "difficulty": "medium"},
            {"question": "What is the difference between '==' and 'is' in Python?", "answer": "'==' checks value equality. 'is' checks object identity (same memory address). E.g., [1,2]==[1,2] is True but [1,2] is [1,2] is False.", "topic": "Coding", "company": "TCS", "difficulty": "medium"},
            {"question": "Find the missing number in an array from 1 to N.", "answer": "Sum formula: Expected sum = N(N+1)/2. Missing = Expected sum - Actual sum. O(n) time, O(1) space.", "topic": "Coding", "company": "TCS", "difficulty": "medium"},
            {"question": "What is the use of 'try-except-finally' in Python?", "answer": "try: code that may fail. except: handles the exception. finally: always executes regardless of exception — used for cleanup like closing files.", "topic": "Coding", "company": "TCS", "difficulty": "medium"},
            {"question": "Reverse a singly linked list.", "answer": "Use 3 pointers: prev=None, curr=head, next=None. While curr: next=curr.next, curr.next=prev, prev=curr, curr=next. Return prev.", "topic": "Coding", "company": "TCS", "difficulty": "hard"},

            # ══════════════════════════════════════
            # TCS — HR INTERVIEW (5 cards)
            # ══════════════════════════════════════
            {"question": "Tell me about yourself.", "answer": "Structure: 1. Brief personal intro (10s). 2. Education background (20s). 3. Technical skills and projects (30s). 4. Why TCS (20s). Keep it under 2 minutes and end with enthusiasm.", "topic": "HR Interview", "company": "TCS", "difficulty": "easy"},
            {"question": "Why do you want to join TCS?", "answer": "Mention: TCS is India's #1 IT company with 600k+ employees. Strong training programs like TCS iON. Global exposure. Stable growth path. Align your career goals with TCS's digital transformation vision.", "topic": "HR Interview", "company": "TCS", "difficulty": "easy"},
            {"question": "What is TCS NQT? What are its sections?", "answer": "TCS National Qualifier Test. Sections: 1. Numerical Ability 2. Verbal Ability 3. Reasoning Ability 4. Coding (for Digital/Prime tiers). Scores determine TCS Ninja vs Digital vs Prime placement.", "topic": "HR Interview", "company": "TCS", "difficulty": "medium"},
            {"question": "Where do you see yourself in 5 years?", "answer": "Answer formula: Short-term (1-2 yrs): Master your tech stack at TCS. Mid-term (3-4 yrs): Lead a team or module. Long-term (5 yrs): Become a solution architect or senior engineer contributing to client delivery.", "topic": "HR Interview", "company": "TCS", "difficulty": "easy"},
            {"question": "What are your strengths and weaknesses?", "answer": "Strength (choose 1 relevant): 'I am quick to learn new technologies and adapt.' Weakness (show growth): 'I used to struggle with public speaking, but I joined a debate club and improved significantly.'", "topic": "HR Interview", "company": "TCS", "difficulty": "easy"},

            # ══════════════════════════════════════
            # INFOSYS — CODING (20 cards)
            # ══════════════════════════════════════
            {"question": "Explain Polymorphism in OOP with a real-world example.", "answer": "Polymorphism = same method name, different behaviors. Real world: 'speak()' method — Dog says 'Woof', Cat says 'Meow'. In Java: method overriding (runtime) and method overloading (compile-time).", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is the difference between ArrayList and LinkedList in Java?", "answer": "ArrayList: uses dynamic array, O(1) access, O(n) insert. LinkedList: doubly linked list, O(n) access, O(1) insert/delete at head. Use ArrayList for frequent access, LinkedList for frequent insertions.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is a deadlock in OS? How to prevent it?", "answer": "Deadlock: Two or more processes wait for each other's resources indefinitely. Prevention: 1. Mutual Exclusion 2. Hold and Wait 3. No Preemption 4. Circular Wait — Break any one of these Coffman conditions.", "topic": "Coding", "company": "Infosys", "difficulty": "hard"},
            {"question": "Explain normalization. What is 3NF?", "answer": "Normalization reduces data redundancy. 3NF: 1. In 2NF. 2. No transitive dependency (non-key column depending on another non-key column). Every non-prime attribute must depend on the primary key only.", "topic": "Coding", "company": "Infosys", "difficulty": "hard"},
            {"question": "What is the output of: for i in range(3): print(i) after a continue when i==1?", "answer": "0 and 2 are printed. 'continue' skips the rest of the loop body for i=1, so 1 is not printed.", "topic": "Coding", "company": "Infosys", "difficulty": "easy"},
            {"question": "Write code to check if a string is an anagram of another.", "answer": "sorted(s1)==sorted(s2) OR use Counter: Counter(s1)==Counter(s2). Both O(n log n) and O(n) approaches.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is the difference between TCP and UDP?", "answer": "TCP: Connection-oriented, reliable, ordered (handshake needed). Used for HTTP, FTP. UDP: Connectionless, fast, no guarantee of delivery. Used for video streaming, DNS, gaming.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is a virtual function in C++?", "answer": "A virtual function enables runtime polymorphism. Declared with 'virtual' keyword in base class. Derived class overrides it. Called via base class pointer — correct derived version executes. Pure virtual: =0.", "topic": "Coding", "company": "Infosys", "difficulty": "hard"},
            {"question": "Explain the concept of garbage collection in Java.", "answer": "JVM automatically frees heap memory for objects no longer referenced. Uses algorithms like Mark-and-Sweep, G1GC. Programmers can suggest GC via System.gc() but cannot force it.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is the difference between == and equals() in Java?", "answer": "'==' compares references (memory addresses). '.equals()' compares content. Always use .equals() to compare String values. 'abc' == 'abc' may be false for different objects.", "topic": "Coding", "company": "Infosys", "difficulty": "easy"},
            {"question": "What is Big O notation? Give examples.", "answer": "O(1): constant — Array access. O(log n): Binary Search. O(n): Linear scan. O(n log n): Merge Sort. O(n²): Bubble Sort. O(2ⁿ): Fibonacci recursive.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "Write SQL to find the 2nd highest salary.", "answer": "SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees); OR use DENSE_RANK().", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is the difference between process and thread?", "answer": "Process: independent program with its own memory. Thread: lightweight unit within a process that shares memory. Threads communicate faster but risk race conditions.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "Explain inheritance types in OOP.", "answer": "Single (A→B), Multiple (A+B→C, not in Java), Multilevel (A→B→C), Hierarchical (A→B, A→C), Hybrid. Java uses interfaces to achieve multiple inheritance safely.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is a hash table? What is collision?", "answer": "Hash table stores key-value pairs using a hash function to map keys to indices. Collision: Two keys hash to same index. Resolved by Chaining (linked list) or Open Addressing (linear probing).", "topic": "Coding", "company": "Infosys", "difficulty": "hard"},
            {"question": "What does 'static' mean in Java?", "answer": "Static members belong to the class, not instances. Static variables are shared across all objects. Static methods can be called without creating an object. Used for utility functions like Math.sqrt().", "topic": "Coding", "company": "Infosys", "difficulty": "easy"},
            {"question": "Write a Python function to flatten a nested list.", "answer": "def flatten(lst): result=[]; [result.extend(flatten(i)) if isinstance(i,list) else result.append(i) for i in lst]; return result. Uses recursion.", "topic": "Coding", "company": "Infosys", "difficulty": "hard"},
            {"question": "What is the difference between DFS and BFS?", "answer": "DFS: Depth-First Search — goes as deep as possible using Stack (recursive/iterative). BFS: Breadth-First Search — explores level by level using Queue. BFS finds the shortest path in unweighted graphs.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is a REST API? What are its principles?", "answer": "REST (Representational State Transfer) uses HTTP methods: GET (read), POST (create), PUT (update), DELETE (remove). Stateless, cacheable, uniform interface. Returns JSON/XML.", "topic": "Coding", "company": "Infosys", "difficulty": "medium"},
            {"question": "What is the difference between primary key and foreign key?", "answer": "Primary Key: uniquely identifies each row in a table, cannot be NULL. Foreign Key: references the primary key of another table, maintains referential integrity between tables.", "topic": "Coding", "company": "Infosys", "difficulty": "easy"},

            # ══════════════════════════════════════
            # INFOSYS — HR INTERVIEW (5 cards)
            # ══════════════════════════════════════
            {"question": "Why Infosys?", "answer": "Mention: Infosys is a global leader with 300k+ employees. Strong on digital transformation, cloud, AI. InfyTQ learning platform and global training programs. Align with their 'Navigate your next' vision.", "topic": "HR Interview", "company": "Infosys", "difficulty": "easy"},
            {"question": "Describe a time you worked in a team and faced a conflict. How did you resolve it?", "answer": "Use STAR method: Situation — project deadline clashing. Task — resolve team disagreement. Action — facilitated discussion, found compromise, redistributed tasks. Result — delivered on time. Emphasize empathy and communication.", "topic": "HR Interview", "company": "Infosys", "difficulty": "medium"},
            {"question": "Are you comfortable relocating?", "answer": "Best answer: 'Yes, I am open to relocation. I understand Infosys has offices across India and globally, and I am excited for the opportunity to work in different environments.'", "topic": "HR Interview", "company": "Infosys", "difficulty": "easy"},
            {"question": "What do you know about InfyTQ?", "answer": "InfyTQ is Infosys's Learning Platform for campus students. Offers courses in Java, Python, Data Structures. Clearing InfyTQ can directly qualify you for Infosys recruitment, bypassing the aptitude test.", "topic": "HR Interview", "company": "Infosys", "difficulty": "medium"},
            {"question": "How do you handle pressure and tight deadlines?", "answer": "Formula: 'I prioritize tasks by impact, break large work into smaller chunks, communicate blockers early, and stay focused. During college projects, I managed last-minute requirement changes by...' Give a specific example.", "topic": "HR Interview", "company": "Infosys", "difficulty": "medium"},

            # ══════════════════════════════════════
            # WIPRO — APTITUDE (10 cards)
            # ══════════════════════════════════════
            {"question": "If the selling price is Rs. 440 and is 10% more than cost price, find profit.", "answer": "Cost Price = 440/1.10 = Rs. 400. Profit = Rs. 40.", "topic": "Aptitude", "company": "Wipro", "difficulty": "easy"},
            {"question": "A man walks 4 km east, then 3 km north. What is his distance from start?", "answer": "5 km. Using Pythagorean theorem: √(4²+3²) = √25 = 5.", "topic": "Aptitude", "company": "Wipro", "difficulty": "easy"},
            {"question": "In how many ways can the letters of 'LEADER' be arranged?", "answer": "360. Total = 6!/2! = 720/2 = 360 (E repeats twice).", "topic": "Aptitude", "company": "Wipro", "difficulty": "hard"},
            {"question": "What comes next: 1, 4, 9, 16, 25, ?", "answer": "36. These are perfect squares: 1²,2²,3²,4²,5²,6²=36.", "topic": "Aptitude", "company": "Wipro", "difficulty": "easy"},
            {"question": "A sum triples in 6 years at simple interest. What is the rate?", "answer": "33.33% per annum. If principal = P, amount = 3P, SI = 2P. Rate = 2P×100/(P×6) = 33.33%.", "topic": "Aptitude", "company": "Wipro", "difficulty": "hard"},
            {"question": "Two trains start at the same time from A and B, 120km apart, travelling towards each other at 60 and 40 km/h. When do they meet?", "answer": "After 1.2 hours. Relative speed = 100 km/h. Time = 120/100 = 1.2 hours.", "topic": "Aptitude", "company": "Wipro", "difficulty": "medium"},
            {"question": "Find the median of: 7, 2, 5, 1, 8, 9, 3", "answer": "5. Sort: 1,2,3,5,7,8,9. Middle element (4th) = 5.", "topic": "Aptitude", "company": "Wipro", "difficulty": "easy"},
            {"question": "In a group of 60, 30 play cricket, 25 play football, 10 play both. How many play neither?", "answer": "15. Using set formula: |C∪F| = 30+25-10 = 45. Neither = 60-45 = 15.", "topic": "Aptitude", "company": "Wipro", "difficulty": "medium"},
            {"question": "The average of 5 numbers is 40. Four of them are 30, 35, 42, 51. Find the fifth number.", "answer": "42. Total = 5×40=200. Fifth = 200-(30+35+42+51) = 200-158 = 42.", "topic": "Aptitude", "company": "Wipro", "difficulty": "easy"},
            {"question": "A sum of Rs. 2519 is to be divided among A,B,C in ratio 2:3:5. Find A's share.", "answer": "Rs. 503.8 ≈ Rs. 504. A's share = (2/10)×2519 = 503.8.", "topic": "Aptitude", "company": "Wipro", "difficulty": "easy"},

            # ══════════════════════════════════════
            # WIPRO — HR INTERVIEW (10 cards)
            # ══════════════════════════════════════
            {"question": "Why do you want to join Wipro?", "answer": "Wipro is a global leader in IT services. Strong focus on cloud, AI, and sustainability. Good work-life balance. Wipro's WILP (Work Integrated Learning Program) for upskilling is a huge benefit. Align with Digital Transformation vision.", "topic": "HR Interview", "company": "Wipro", "difficulty": "easy"},
            {"question": "What is your greatest achievement so far?", "answer": "Structure: Pick a technical or academic achievement. Explain the Context, Challenge, Your Action, and Result. Example: 'Built an ML model that reduced prediction error by 15% in my final year project. It was selected for college symposium.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "medium"},
            {"question": "Are you ready to work in shifts (Wipro has 24/7 operations)?", "answer": "'Yes, I understand the nature of IT service delivery requires flexibility. I am comfortable working in shifts and adapting to client time zones. I see it as an opportunity to work with global teams.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "easy"},
            {"question": "How quickly can you learn new technologies?", "answer": "Give a real example: 'In my college project, I learned React in 2 weeks. I approach new tech by: reading official docs, building a mini project, and using resources like YouTube and official certifications.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "medium"},
            {"question": "What do you know about Wipro's Elite NTH test?", "answer": "Wipro NTH (National Talent Hunt): Aptitude, Written English, Essay. For Elite track: Advanced Aptitude and Online Programming Test in Python/Java. Elite candidates get better packages and roles.", "topic": "HR Interview", "company": "Wipro", "difficulty": "medium"},
            {"question": "Do you prefer working alone or in a team?", "answer": "'I enjoy both. For deep focus tasks like coding and debugging, I prefer working individually with clear requirements. For system design and planning, team collaboration is more effective. I'm flexible based on the project need.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "easy"},
            {"question": "What motivates you to work every day?", "answer": "'Learning something new every day. I am driven by problem-solving and seeing tangible impact from my work — whether it's fixing a complex bug or delivering a feature a user loves. Growth and contribution are my core motivators.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "easy"},
            {"question": "Describe a failed project or mistake. What did you learn?", "answer": "Be honest but constructive. Example: 'In my 3rd year project, the database design was poor, causing performance issues. I learned the importance of normalization early in development. Now I always review the schema before coding.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "medium"},
            {"question": "What are your long-term career goals?", "answer": "'Short term: become proficient in cloud technologies at Wipro. Mid term: earn AWS/Azure certification and lead a module. Long term: transition into solution architecture, helping clients design scalable IT systems.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "easy"},
            {"question": "What is your expected salary at Wipro?", "answer": "'I am aware Wipro offers competitive packages for freshers around 3.5-6.5 LPA depending on the role. I trust Wipro's standard compensation and would be open to discussing based on the role requirement.'", "topic": "HR Interview", "company": "Wipro", "difficulty": "easy"},

            # ══════════════════════════════════════
            # ACCENTURE — HR + Cognitive (10 cards)
            # ══════════════════════════════════════
            {"question": "What is Accenture's vision and core values?", "answer": "Vision: 'To be a leading company trusted to deliver innovation.' Core values: Stewardship, Best People, Client Value Creation, One Global Network, Respect for Individual, Integrity. Know these for Accenture interviews.", "topic": "HR Interview", "company": "Accenture", "difficulty": "medium"},
            {"question": "Explain a time you showed leadership.", "answer": "Use STAR: Situation, Task, Action, Result. Example: 'As project lead in college, I noticed team morale was low. I organized daily standups, identified blockers, and redistributed tasks. Result: Delivered 2 days early with positive feedback.'", "topic": "HR Interview", "company": "Accenture", "difficulty": "medium"},
            {"question": "What do you know about Accenture's business areas?", "answer": "Accenture operates in: Strategy & Consulting, Interactive, Technology, Operations, Song. Major clients in banking, healthcare, retail, and manufacturing. Strong in cloud migration, AI, and sustainability services.", "topic": "HR Interview", "company": "Accenture", "difficulty": "medium"},
            {"question": "How do you handle feedback from a manager or client?", "answer": "'I actively seek feedback and see criticism as a growth tool. When a client suggests changes, I listen without defensiveness, clarify requirements, implement the change, and follow up to confirm satisfaction.'", "topic": "HR Interview", "company": "Accenture", "difficulty": "easy"},
            {"question": "If A does a job in 6 days and B in 9 days, how many days together?", "answer": "3.6 days. 1/6+1/9 = 5/18. Days = 18/5 = 3.6 days.", "topic": "Aptitude", "company": "Accenture", "difficulty": "medium"},
            {"question": "What is cloud computing? Name 3 types of cloud services.", "answer": "Cloud computing delivers IT resources over the internet on-demand. Types: IaaS (Infrastructure — AWS EC2), PaaS (Platform — Google App Engine), SaaS (Software — Gmail, Salesforce).", "topic": "Coding", "company": "Accenture", "difficulty": "easy"},
            {"question": "Cognitive: A is to B as 21 is to?", "answer": "Depends on pattern. A=1, B=2 alphabetically. 21 corresponds to position 21 = 'U'. So A:B :: 21:22 or U:V depending on the question format.", "topic": "Aptitude", "company": "Accenture", "difficulty": "medium"},
            {"question": "What is digital transformation and why does Accenture care?", "answer": "Digital transformation = using tech (cloud, AI, data) to fundamentally change business processes and customer experience. Accenture earns most revenues from digital projects — hence understanding this is crucial for interviews.", "topic": "HR Interview", "company": "Accenture", "difficulty": "medium"},
            {"question": "Situational: Your client is angry about a delayed delivery. What do you do?", "answer": "1. Listen and empathize without excuses. 2. Apologize for the inconvenience. 3. Explain current status. 4. Commit to a revised deadline. 5. Follow through. 6. After resolution, share a plan to prevent recurrence.", "topic": "HR Interview", "company": "Accenture", "difficulty": "hard"},
            {"question": "What Microsoft tools are commonly used at Accenture?", "answer": "Teams (communication), SharePoint (document management), Power BI (reporting), Azure (cloud), Excel (data analysis), Outlook (email). Accenture is a major Microsoft partner.", "topic": "Coding", "company": "Accenture", "difficulty": "easy"},

            # ══════════════════════════════════════
            # COGNIZANT — CODING + DSA (10 cards)
            # ══════════════════════════════════════
            {"question": "Explain the concept of dynamic programming.", "answer": "DP breaks complex problems into overlapping subproblems and stores results (memoization/tabulation) to avoid recomputation. Classic problems: Fibonacci, Knapsack, Longest Common Subsequence.", "topic": "Coding", "company": "Cognizant", "difficulty": "hard"},
            {"question": "What is the difference between a heap and a stack in memory?", "answer": "Stack: stores function calls, local variables. LIFO, managed automatically. Heap: dynamic memory allocation (malloc/new). Larger, managed by programmer. Memory leaks occur when heap is not freed.", "topic": "Coding", "company": "Cognizant", "difficulty": "medium"},
            {"question": "What is a binary tree? What is BST?", "answer": "Binary Tree: each node has at most 2 children. BST (Binary Search Tree): left subtree < root < right subtree. Enables O(log n) search, insert, delete in balanced trees.", "topic": "Coding", "company": "Cognizant", "difficulty": "medium"},
            {"question": "Cognizant Aptitude: If 5 machines make 5 parts in 5 minutes, how long do 100 machines take to make 100 parts?", "answer": "5 minutes. Each machine makes 1 part in 5 mins. 100 machines make 100 parts simultaneously in 5 mins.", "topic": "Aptitude", "company": "Cognizant", "difficulty": "hard"},
            {"question": "What is SOLID principle in software design?", "answer": "S-Single Responsibility. O-Open/Closed. L-Liskov Substitution. I-Interface Segregation. D-Dependency Inversion. These 5 principles ensure maintainable, scalable OOP code.", "topic": "Coding", "company": "Cognizant", "difficulty": "hard"},
            {"question": "What is the difference between Agile and Waterfall?", "answer": "Waterfall: sequential phases (Requirements→Design→Code→Test→Deploy). Rigid. Agile: iterative sprints, continuous feedback. Flexible. Cognizant uses Agile/SAFe for most projects.", "topic": "Coding", "company": "Cognizant", "difficulty": "medium"},
            {"question": "Write a function to detect if a linked list has a cycle.", "answer": "Use Floyd's Slow-Fast algorithm. slow=fast=head. While fast and fast.next: slow=slow.next, fast=fast.next.next. If slow==fast, cycle exists. O(n) time, O(1) space.", "topic": "Coding", "company": "Cognizant", "difficulty": "hard"},
            {"question": "What is an index in SQL? When should you use it?", "answer": "Index is a data structure (B-Tree) that speeds up SELECT queries. Use on frequently queried columns (WHERE, JOIN). Downside: slows INSERT/UPDATE. Don't over-index.", "topic": "Coding", "company": "Cognizant", "difficulty": "medium"},
            {"question": "Cognizant HR: Describe yourself in 3 words.", "answer": "Pick words that reflect work traits: Adaptable, Analytical, Collaborative. Then briefly justify each: 'Adaptable — I learned 3 frameworks in my final year. Analytical — I approach problems systematically...'", "topic": "HR Interview", "company": "Cognizant", "difficulty": "easy"},
            {"question": "What is a microservice architecture?", "answer": "Breaks monolithic app into small, independent services. Each service has its own database, codebase, and deployment. Services communicate via REST/gRPC. Benefits: scalability, independent deployment, fault isolation.", "topic": "Coding", "company": "Cognizant", "difficulty": "hard"},
        ]

        added = 0
        for card_data in sample_cards:
            existing = db.query(Flashcard).filter(Flashcard.question == card_data["question"]).first()
            if not existing:
                db.add(Flashcard(**card_data))
                added += 1
        db.commit()
        return {"seeded": added, "total_attempted": len(sample_cards)}
