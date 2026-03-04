## Top Bun

Top Bun is a Flask web application for tracking store performance through structured assessments (day, night, and online forms) and visualizing rankings on a dashboard.

### Features
- **Store management**: Create and manage store locations, with soft-delete support to preserve history.
- **Assessments and questions**: Configure assessments made up of questions with different scoring/aggregation types.
- **Responses and scoring**: Capture responses, automatically calculate percent scores, and rank stores.
- **Dashboard**: View monthly performance, rankings by form type, and aggregated scores per store.

![Top Bun dashboard](images/dashboard.png)

### Tech stack
- **Backend**: Python, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Forms**: Flask-WTF / WTForms

## Run locally (Working on getting fixed)
### 1. Clone repo
```bash
git clone https://github.com/your-username/Top_Bun.git
cd TopBun
```
### 2. Create and activate virtual environment
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
macOS / Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the database
Run the database migrations to create `app.db`:

```bash
flask db upgrade
```

### 5. Run the development server
```bash
flask run
```

Then open `http://127.0.0.1:5000/` in your browser.
