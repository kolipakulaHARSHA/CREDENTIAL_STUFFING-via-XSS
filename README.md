Credential Stuffing  via Stored XSS Detection

Overview
--------
This project implements a novel security solution to detect credential stuffing attacks initiated through stored Cross-Site Scripting (XSS) vulnerabilities in web applications.
It combines a machine learning (ML) model for analyzing web logs and a web crawler to identify XSS vulnerabilities. The system monitors logs for anomalous login patterns, flags potential credential stuffing attempts,
and scans associated web pages for stored XSS vulnerabilities to facilitate mitigation.

Key Features
- Machine Learning Detection: Utilizes an XGBoost classifier trained on web application logs to detect credential stuffing attempts with high accuracy.
- Web Crawler: Systematically explores web pages to identify stored XSS vulnerabilities using a predefined payload dataset.
- Integrated Approach: Combines log analysis and vulnerability scanning for a comprehensive defense against this sophisticated attack vector.
- Simulation Environment: Tested on the Damn Vulnerable Web Application (DVWA) to validate effectiveness.

This project was developed as part of a research effort at PES University, documented in the paper "Detection of Credential Stuffing Via Stored Cross-site Scripting Attack Using ML-based Log Analysis and a Web Crawler," 
co-authored by Kolipakula Harsha, Jake J Mathew, and Nagasundari S, currently under review for publication.

Prerequisites
-------------
To run this project, ensure you have the following installed:
- Python 3.8+
- Virtual Machines: For simulating DVWA and generating logs (e.g., using VirtualBox or VMware).
- Damn Vulnerable Web Application (DVWA): For testing the system in a controlled environment.
- Dependencies: Listed in requirements.txt.


Project Structure
-----------------
credential-stuffing-detection/
│
├── data/
│   ├── logs/              # Directory for raw and processed logs
│   └── payloads/          # XSS payload dataset
├── scripts/
│   ├── Connection.py          # Orchestrates periodic execution
│   ├── CSVV2.py      # Converts logs to CSV
│   ├── TestV3.py # ML-based attack detection
│   └── CrawlerV2.py     # Web crawler for XSS detection
├── models/
│   └── xgboost_model.joblib  # Pre-trained XGBoost model
├── README.txt             # Project documentation
└── requirements.txt       # Python dependencies

Usage
-----
1. Generate Logs
   - Deploy DVWA on a VM and simulate user activity and attacks using multiple VMs.
   - Use a script (e.g., a modified version of scripts/log_generator.py) to create logs mimicking credential stuffing via XSS.

2. Train the ML Model
   - Preprocess logs and train the XGBoost model:
     python scripts/XGBOOST.py --input data/logs/access.log --output models/xgboost_model.pkl
   - This generates visualizations (e.g., confusion matrix, ROC curve) in the plots/ directory.

3. Run the Detection System
   - Start the main scheduler to monitor logs and detect attacks:
     python scripts/driver.py
   - The system:
     - Converts logs to CSV (log_to_csv.py).
     - Analyzes logs for credential stuffing (attack_detection.py).
     - Triggers the crawler if an attack is detected (xss_crawler.py).

4. Crawl for XSS Vulnerabilities
   - Manually run the crawler for testing:
     python scripts/xss_crawler.py --url http://192.168.1.x/dvwa --payloads data/payloads/xss_payloads.txt
   - Results are logged to data/logs/vulnerability_report.txt.

Methodology
-----------
The system operates in two main phases:

1. Log Analysis with ML
   - Preprocessing: Converts logs to CSV, handles timestamps, and hashes high-cardinality features (e.g., IPs, URLs).
   - Feature Engineering: Includes lag features (e.g., timestamp differences) to capture temporal patterns.
   - Model: XGBoost classifier tuned with GridSearchCV (max-depth: 7-11, n-estimators: 200-400, learning-rate: 0.1-0.3).
   - Metrics: Achieved 97.91% accuracy, 98.07% precision, and 80.14% recall.

2. Web Crawler
   - Discovery: Recursively follows links from a base URL.
   - Testing: Submits XSS payloads to input fields and checks for persistence in responses.
   - Output: Logs vulnerable URLs and payload success counts.

See the paper for detailed pseudocode and system design diagrams.

Results
-------
- Detection Performance: The ML model effectively flags credential stuffing attempts with an AUC of 0.90 on the ROC curve.
- Crawler Efficiency: Successfully identifies stored XSS vulnerabilities in DVWA, with processing times varying by page complexity (see histogram in paper).
- Key Features: URL hashes (44%) and timestamp differences (34%) are the most significant predictors of malicious activity.

Limitations
-----------
- Recall: 19.86% of attacks may go undetected due to the recall rate of 80.14%.
- Scalability: The crawler’s efficiency decreases with large web applications.
- Adaptability: The model may require retraining as attack patterns evolve.

Future Work
-----------
- Enhance recall by incorporating additional features or ensemble methods.
- Optimize the crawler for larger sites using parallel processing or heuristic filtering.
- Extend detection to other XSS types (e.g., reflected, DOM-based).

Acknowledgments
---------------
- Authors: Kolipakula Harsha, Jake J Mathew, Nagasundari S
- Institution: PES University, ISFCR, Bengaluru, India
- Support: Thanks to PES University for providing resources and guidance.

Contact
-------
For questions or collaboration, reach out to:
- Kolipakula Harsha: harshak1874@gmail.com
- Jake J Mathew: jakejmathew@gmail.com
