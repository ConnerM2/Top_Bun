## Top Bun

Top Bun is a Flask web application for tracking store performance through structured assessments (day, night, and online forms) and visualizing rankings on a dashboard.

### Features
- **Store management**: Create and manage store locations, with soft-delete support to preserve history.
- **Assessments and questions**: Configure assessments made up of questions with different scoring/aggregation types.
- **Responses and scoring**: Capture responses, automatically calculate percent scores, and rank stores.
- **Dashboard**: View monthly performance, rankings by form type, and aggregated scores per store.

![Planck vs Rayleigh–Jeans](images/dashboard.png)

### Tech stack
- **Backend**: Python, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Forms**: Flask-WTF / WTForms

## Run locally
### 1. Clone repo
```bash
git clone https://github.com/your-username/Top_Bun.git
cd TopBun
```
### 2. Create and activate virtual environment
(powershell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
(macOS/Linux)
```
python -m venv .venv
source .venv/bin/activate
```
### 3. Install dependencies
```bask
pip install -r requirments.txt
```
### 4. Configuration
Override SECRET_KEY
```bash
set SECRET_KEY=some-dev-secret           # Windows
export SECRET_KEY=some-dev-secret        # macOS/Linux
```
Override db URL
```bash
set DATABASE_URL=postgresql://user:pass@localhost/dbname     # Windows
export DATABASE_URL=postgresql://user:pass@localhost/dbname  # macOS/Linux
```
### 5. initialize the database
`flask --app top_bun.py db upgrade`
### 6. Run
`flask --app top_bun.py run`




