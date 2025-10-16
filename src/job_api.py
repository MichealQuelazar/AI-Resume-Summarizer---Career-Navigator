import http.client
import json
import urllib.parse

# Fetch LinkedIn jobs based on search query and location
def fetch_linkedin_jobs(search_query, location="Worldwide", rows=60):
    conn = http.client.HTTPSConnection("jobs-api14.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "185a6a42b0msh9b8daefadaad35cp16ce2ejsn06ffb2c3f330",
        'x-rapidapi-host': "jobs-api14.p.rapidapi.com"
    }
    
    # URL encode the search query
    encoded_query = urllib.parse.quote(search_query)
    
    # Build the request URL with parameters
    url = f"/v2/linkedin/search?query={encoded_query}&experienceLevels=intern%3Bentry%3Bassociate%3BmidSenior%3Bdirector&workplaceTypes=remote%3Bhybrid%3BonSite&location={location}&datePosted=month&employmentTypes=contractor%3Bfulltime%3Bparttime%3Bintern%3Btemporary"
    
    try:
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        # Parse JSON response
        jobs_data = json.loads(data.decode("utf-8"))
        
        # Extract jobs from the response - API returns jobs in 'data' key
        if isinstance(jobs_data, dict) and 'data' in jobs_data:
            jobs = jobs_data['data'][:rows]
        elif isinstance(jobs_data, dict) and 'jobs' in jobs_data:
            jobs = jobs_data['jobs'][:rows]
        elif isinstance(jobs_data, list):
            jobs = jobs_data[:rows]
        else:
            jobs = []
            
        return jobs
        
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []
    finally:
        conn.close()

