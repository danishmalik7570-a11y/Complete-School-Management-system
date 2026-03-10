# DNL Institute Management System 🎓

A modern, professional school management system designed for **DNL Institute of Information Technology**. This application provides a comprehensive solution for managing students, instructors, courses, and financial records with a focus on ease of use and visual excellence.

---

## 👋 Developed By
**Muhammad Danish**  
*Full Stack Developer*

---

## ✨ Key Features

### 👨‍🎓 Student Management
- Complete student registration and profile management.
- Dynamic fee structures with support for advance payments and monthly installments.
- Automatic generation of admission slips.

### 👨‍🏫 Instructor Management
- Instructor profiles with qualifications and experience tracking.
- Salary management and category assignments.

### 💰 Financial Ecosystem
- **Revenue Tracking**: Monitor all income sources (admission fees, monthly dues).
- **Expense Management**: Track institute costs by category (rent, salaries, utilities).
- **Net Profit Analysis**: Real-time financial health dashboard.
- **Fee Reports**: Insightful reporting on collected vs. overdue fees.

### 🏢 Course & Category Management
- Organize courses into logical categories.
- Dashboard-level statistics for quick overview of institute activity.

### 🔒 Security & Administration
- Multi-role authentication (Admin and Employee).
- Secure password hashing and session management.

---

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **ORM**: SQLAlchemy
- **Database**: SQLite (Configurable)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap 5 + TailwindCSS (Glassmorphic & Premium UI)
- **Forms**: Flask-WTF with secure validation

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd schoolmanagementtsystem-main
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Or use `uv sync` if using uv)*

3. **Set environment variables**:
   ```bash
   # Windows
   set SESSION_SECRET=your-secret-key
   # Linux/Mac
   export SESSION_SECRET=your-secret-key
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Access the system**:
   Open your browser and navigate to `http://127.0.0.1:5000`

---

## 🔐 Default Admin Access
For initial setup, use the following credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

## 📸 Design Philosophy
The system features a **Premium UI** with:
- **Glassmorphism**: Subtle blur effects and soft shadows.
- **Responsive Layout**: Works seamlessly on Mobile, Tablet, and Desktop.
- **Dynamic Icons**: Powered by Font Awesome for a modern look.
- **Vibrant Palettes**: Professional blue and white theme with high readability.

---

© 2026 **Muhammad Danish** | DNL Institute Management System
