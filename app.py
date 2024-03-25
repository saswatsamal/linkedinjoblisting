from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# Define the function to extract job details
def get_job_details(response, limit=5):
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all job listings
    job_listings = soup.find_all("li")

    # Create an empty list to store job details
    job_details = []

    # Iterate over each job listing and extract relevant information
    for index, job in enumerate(job_listings):
        if index >= limit:  # Check if the number of listings processed exceeds the limit
            break

        job_title = job.find("h3", class_="base-search-card__title").text.strip()
        company_name = job.find("a", class_="hidden-nested-link").text.strip()
        location = job.find("span", class_="job-search-card__location").text.strip()
        job_url = job.find("a", class_="base-card__full-link")["href"]

        # Append the extracted information to the list
        job_details.append({
            "Job Title": job_title,
            "Company Name": company_name,
            "Location": location,
            "Job URL": job_url
        })

    return job_details

# Define the main route
@app.route("/", methods=["GET", "POST"])
def index():
    loading = False  # Initialize loading variable

    if request.method == "POST":
        keywords = request.form.get("keywords")
        location = request.form.get("location")

        # Define the API endpoint based on user input
        api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&f_TPR=r604800&f_SB2=4&f_E=2&f_WT=2"

        # Send a GET request to the API endpoint
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Call the function to extract job details
            job_details = get_job_details(response, limit=10)  # Limiting to 10 job listings
            if job_details:
                # Render the template with job details
                return render_template("results.html", job_details=job_details)
            else:
                return "No job listings found."
        elif response.status_code == 429:
            loading = True  # Set loading to True for retry
            time.sleep(10)  # Delay of 10 seconds
            # Retry the request
            response = requests.get(api_url)
            if response.status_code == 200:
                job_details = get_job_details(response, limit=10)  # Limiting to 10 job listings
                if job_details:
                    # Render the template with job details
                    return render_template("results.html", job_details=job_details)
                else:
                    return "No job listings found."
            else:
                return render_template("response.html", message="Request failed. Please try again later.")  # Render response.html on failure
        else:
            return render_template("response.html", message="Failed to fetch data from the API. Please try again later.")  # Render response.html for other errors

    return render_template("index.html", loading=loading)  # Pass loading variable to template

if __name__ == "__main__":
    app.run(debug=False)
