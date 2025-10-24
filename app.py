from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import job_search_module
import io
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return jsonify({
        'message': 'ToolHouzz Job Search API',
        'status': 'running',
        'version': '1.0',
        'endpoints': {
            '/search': 'POST - Search for jobs across 23+ portals'
        }
    })

@app.route('/search', methods=['POST', 'OPTIONS'])
def search_jobs():
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # FIXED: Handle None values properly
        job_title = (data.get('job_title') or '').strip()
        job_age = data.get('job_age', 15)
        city = (data.get('city') or '').strip()
        country = (data.get('country') or '').strip()
        
        # Validate required fields
        if not job_title:
            return jsonify({'error': 'Job title is required'}), 400
        
        if not country:
            return jsonify({'error': 'Country is required'}), 400
        
        # Convert job_age to integer
        try:
            job_age = int(job_age)
        except (ValueError, TypeError):
            job_age = 15
        
        # Build location string
        location = f"{city}, {country}" if city else country
        
        print(f"[INFO] Searching for: {job_title} in {location} (last {job_age} days)")
        
        # Perform the job search
        results = job_search_module.search_all_portals(
            job_title=job_title,
            location=location,
            job_age=job_age
        )
        
        if not results or len(results) == 0:
            return jsonify({'error': 'No jobs found. Try different search terms.'}), 404
        
        print(f"[SUCCESS] Found {len(results)} jobs")
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Source', 'Company', 'Job Title', 'Location', 'URL', 'Detected Term', 'Posted (UTC)'])
        
        # Write data
        for job in results:
            writer.writerow([
                job.get('date', ''),
                job.get('source', ''),
                job.get('company', 'N/A'),
                job.get('title', ''),
                job.get('location', ''),
                job.get('url', ''),
                job.get('detected_term', job_title),
                job.get('posted_utc', '')
            ])
        
        # Convert to bytes
        output.seek(0)
        csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"jobs_{job_title.replace(' ', '_')}_{timestamp}.csv"
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Render will use the PORT environment variable
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
