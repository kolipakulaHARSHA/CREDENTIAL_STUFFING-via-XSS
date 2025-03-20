import schedule
import time
import subprocess
import os
import csv

def job():
    print("Starting job function:\n")
    print("Running CSV.py\n")
    process = subprocess.Popen(["python3", "CSVV2.py"])
    return_code = process.wait()
    if return_code == 0:
        print(f"Script CSV.py completed successfully.\n")
    else:
        print(f"Script CSV.py failed with return code {return_code}\n")
    
    print("Printing CSV file contents:\n")
    with open("REALTIME.csv",'r',newline='') as csvfile:
        csv_reader=csv.reader(csvfile)
        for row in csv_reader:
            print(', '.join(row))
    print("\n")


    log_file = "/home/kali/Documents/ISFCR/FINAL_XG/DemoDay/Access.log"
    print("Checking Access.log before clearing:\n")
    try:
        with open(log_file, 'r') as logfile:
            print(logfile.read())
    except FileNotFoundError:
        print(f"{log_file} does not exist\n")

    print("Clearing Access.log")
    
    subprocess.run(['sh', '-c', f'echo "" > {log_file}'], check=True)
        #process = subprocess.Popen(["python3", "CSV.py"])
    #return_code = process.wait()
    #if return_code == 0:
    #    print(f"Clearing Log completed successfully.\n")
    #else:
    #    print(f"Clearing Log failed with return code {return_code}\n")
        #with open(log_file,'w'):
        #    pass
    print(f"Cleared {log_file}\n")
    #except:
        #print(f"{log_file} does not exist\n")
   
    print("Checking Access.log after clearing:\n")
    try:
        with open(log_file, 'r') as logfile:
            print(logfile.read())
    except FileNotFoundError:
        print(f"{log_file} does not exist\n")


    print("Checking CSV file before running Test.py:\n")
    csv_file="REALTIME.csv"
    with open("REALTIME.csv",'r',newline='') as csvfile:
        csv_reader=csv.reader(csvfile)
        for row in csv_reader:
            print(', '.join(row))

    print("Running Test.py:\n")
    process = subprocess.Popen(["python3", "TestV3.py"])
    return_code = process.wait()
    if return_code == 0:
        print(f"Script Test.py completed successfully.")
    else:
        print(f"Script Test.py failed with return code {return_code}")
    
    print("Clearing REALTIME.csv\n")

    print("Checking if CSV file is empty after clearing\n")
    csv_file="REALTIME.csv"
    try:
        with open(csv_file,'w'):
            pass
        with open("REALTIME.csv",'r',newline='') as csvfile:
            csv_reader=csv.reader(csvfile)
            for row in csv_reader:
                print(', '.join(row))
        print(f"Cleared {csv_file}\n")
    except:
        print(f"{csv_file} does not exist\n")


job()

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

