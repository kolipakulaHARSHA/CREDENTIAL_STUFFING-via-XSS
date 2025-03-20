import csv

# Define the path to your input log file and the output CSV file
input_log_file = 'Access.log'
output_csv_file = 'REALTIME.csv'

# Define the headers for the output CSV file
headers = ["IP", "TIMESTAMP", "HTTP METHOD", "URL", "PROTOCOL", "STATUS", "LENGTH", "Referer", "USERNAME", "PASSWORD", "ATTEMPT_STATUS", "ATTACK"]

# Open the input log file and the output CSV file
with open(input_log_file, 'r') as infile, open(output_csv_file, 'w', newline='') as outfile:
    csv_writer = csv.writer(outfile)
    csv_writer.writerow(headers)  # Write the headers to the CSV file
    
    # Read each line from the log file
    for line in infile:
        line = line.strip()  # Remove leading/trailing whitespace
        
        if not line:  # Skip empty lines
            continue
        
        fields = line.split()  # Split the line into fields
        
        # Check if the line has the expected number of fields
        #if len(fields) < 12:
        #    print(f"Skipping malformed line: {line}")  # Print the entire line for debugging
        #    continue
        
        try:
            # Extract and transform fields according to the task requirements
            ip = fields[0]
            timestamp = fields[1].replace('t', ' ')  # Replace 't' in TIMESTAMP
            http_method = fields[2]
            url = fields[3]
            protocol = fields[4]
            status = fields[5]
            length = fields[6]
            referer = fields[7]
            username = fields[8]
            password = fields[9]
            attempt_status = fields[10]
            attack = fields[11].replace('-', '0')  # Replace '-' with '0' in ATTACK

            # Write the processed fields to the CSV file
            csv_writer.writerow([
                ip.replace('"', ''), 
                timestamp.replace('"', ''), 
                http_method.replace('"', ''), 
                url.replace('"', ''), 
                protocol.replace('"', ''), 
                status.replace('"', ''), 
                length.replace('"', ''), 
                referer.replace('"', ''), 
                username.replace('"', ''), 
                password.replace('"', ''), 
                attempt_status.replace('"', ''), 
                attack.replace('"', '')
            ])
        
        except Exception as e:
            print(f"Error processing line: {line}\nException: {e}")

print("Log processing completed.")


