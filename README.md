# ToolHouzz Backend - Job Search API

Backend server for the ToolHouzz Job Search feature. Searches 23+ job portals and returns results as CSV.

## 🌐 Job Portals Searched

- LinkedIn
- Indeed
- Glassdoor
- Monster
- Eluta
- JobBank (Canada)
- ZipRecruiter
- SimplyHired
- Jobboom
- Workopolis
- Talent.com
- CareerBuilder
- Robert Half
- TalentEgg
- Snagajob
- Careerjet
- Dice
- Upwork
- FlexJobs
- Kijiji
- Workable
- RBC Careers
- TD Bank Careers
- BMO Careers

## 📁 Files

- **app.py** - Flask web server with API endpoints
- **job_search_module.py** - Job search logic for all portals
- **requirements.txt** - Python dependencies

## 🚀 Deployment

This backend is deployed on Render.com (free tier).

### Deploy on Render:

1. Push these files to a GitHub repository
2. Connect the repository to Render
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
   - **Port:** 10000

## 📡 API Endpoints

### POST /search

Search for jobs across all portals.

**Request Body:**
```json
{
  "job_title": "Business Analyst",
  "job_age": 15,
  "city": "Toronto",
  "country": "Canada"
}
```

**Response:**
Returns a CSV file with columns:
- Date
- Source
- Company
- Job Title
- Location
- URL
- Detected Term
- Posted (UTC)

### GET /

Health check endpoint.

**Response:**
```json
{
  "message": "ToolHouzz Job Search API",
  "status": "running",
  "version": "1.0"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py

# Server runs on http://localhost:5000
```

## 📝 Notes

- CORS is enabled for all origins
- Rate limiting: Small delay between portal requests
- Timeout: 15 seconds per portal
- Results are limited to 20 jobs per portal
- If scraping fails, returns direct search URLs for each portal

## 🛠️ Technologies

- Flask - Web framework
- BeautifulSoup4 - HTML parsing
- Requests - HTTP client
- Gunicorn - Production WSGI server

## 📄 License

Part of ToolHouzz project - Free web tools for everyone.

---

**Frontend:** https://github.com/Tegbircoder/toolhouzz
**Website:** https://toolhouzz.com
