import pandas as pd
from sklearn.feature_extraction import FeatureHasher
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, roc_auc_score, log_loss
from sklearn.metrics import roc_curve, auc
from joblib import load
from sklearn.preprocessing import LabelEncoder
import warnings
import subprocess
warnings.filterwarnings("ignore")

def preprocess_data(data):
    data['TIMESTAMP'] = data['TIMESTAMP'].str.replace(r'(\d{2}):(\d{3})', r'\1.\2', regex=True)
    data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'], format='%Y-%m-%d %H:%M:%S.%f')

    ip_hasher = FeatureHasher(n_features=1000, input_type='string')
    url_hasher = FeatureHasher(n_features=1000, input_type='string')

    hashed_ip = ip_hasher.transform(data['IP'].astype(str).values.reshape(-1, 1)).toarray()
    hashed_url = url_hasher.transform(data['URL'].astype(str).values.reshape(-1, 1)).toarray()

    for i in range(hashed_ip.shape[1]):
        data[f'IP_hashed_{i}'] = hashed_ip[:, i]
    for i in range(hashed_url.shape[1]):
        data[f'URL_hashed_{i}'] = hashed_url[:, i]

    label_encoder_http_method = LabelEncoder()
    data['HTTP METHOD'] = label_encoder_http_method.fit_transform(data['HTTP METHOD'])
    label_encoder_username = LabelEncoder()
    data['USERNAME'] = label_encoder_username.fit_transform(data['USERNAME'])
    label_encoder_password = LabelEncoder()
    data['PASSWORD'] = label_encoder_password.fit_transform(data['PASSWORD'])
    label_encoder_attempt_status = LabelEncoder()
    data['ATTEMPT_STATUS'] = label_encoder_attempt_status.fit_transform(data['ATTEMPT_STATUS'])

    data = data.sort_values(by=['IP', 'TIMESTAMP'])

    for i in range(1, 6):
        data[f'ATTEMPT_STATUS_LAG{i}'] = data.groupby('IP')['ATTEMPT_STATUS'].shift(i)
        data[f'TIMESTAMP_DIFF_LAG{i}'] = data.groupby('IP')['TIMESTAMP'].shift(i)
        data[f'TIMESTAMP_DIFF_LAG{i}'] = (data['TIMESTAMP'] - data[f'TIMESTAMP_DIFF_LAG{i}']).dt.total_seconds()


    data.fillna(0, inplace=True)


    data['TIMESTAMP'] = (data['TIMESTAMP'] - data['TIMESTAMP'].min()).dt.total_seconds()

    return data



# Check if the CSV file is empty
csv_file = 'REALTIME.csv'
new_data = pd.read_csv(csv_file, quotechar='"', escapechar='\\')

detected_attacks=set()
if new_data.empty:
    print(f"{csv_file} is empty. Skipping execution.")
else:
    model = load('xgboost_model.joblib')

    new_data = pd.read_csv('REALTIME.csv', quotechar='"', escapechar='\\')

    # Store the original values before preprocessing
    original_timestamps = new_data['TIMESTAMP'].copy()
    original_referer = new_data['Referer'].copy()
    original_http_methods = new_data['HTTP METHOD'].copy()
    original_usernames = new_data['USERNAME'].copy()
    original_passwords = new_data['PASSWORD'].copy()

    new_data = preprocess_data(new_data)

    features = [f'IP_hashed_{i}' for i in range(1000)] + \
               [f'URL_hashed_{i}' for i in range(1000)] + \
               ['HTTP METHOD', 'USERNAME', 'PASSWORD', 'ATTEMPT_STATUS', 'TIMESTAMP'] + \
               [f'ATTEMPT_STATUS_LAG{i}' for i in range(1, 6)] + \
               [f'TIMESTAMP_DIFF_LAG{i}' for i in range(1, 6)]

    X_new = new_data[features]

    y_pred = model.predict(X_new)

    y_true = new_data['ATTACK']
    print("\n===== PREDICTED ATTACKS =====")
    for index, pred_label in enumerate(y_pred):
        if pred_label == 1:  # Predicted attack
            log_entry = new_data.iloc[index]
            display_index = index
            
            # If the current log is a GET request, use the previous log instead
            if original_http_methods.iloc[index] == 'GET' and index > 0:
                display_index = index - 1
                log_entry = new_data.iloc[display_index]
            
            print("\nWARNING: Potential attack detected!")
            print(f"Log details:")
            print(f"Timestamp: {original_timestamps.iloc[display_index]}")
            print(f"IP: {log_entry['IP']}")
            print(f"URL: {log_entry['URL']}")
            print(f"Referer: {original_referer.iloc[display_index]}")
            print(f"HTTP Method: {original_http_methods.iloc[display_index]}")
            print(f"Username: {original_usernames.iloc[display_index]}")
            print(f"Password: {original_passwords.iloc[display_index]}")
            if display_index != index:
                print("(Note: This is the log entry preceding a GET request flagged as an attack)")
            print("------------------------")
            if 'logout.php' != original_referer.iloc[display_index]:
                detected_attacks.add(original_referer.iloc[display_index])

# Write the detected URLs to a text file
with open('detected_urls.txt', 'w') as f:
    for url in detected_attacks:
        f.write(url + '\n')
print('Detected attack urls:',detected_attacks)

if len(detected_attacks)>0:
    # Run Crawler.py using subprocess
    process=subprocess.Popen(['python3', 'CrawlerV2.py'])
    return_code = process.wait()
    if return_code == 0:
        print(f"Crawler.py completed successfully.\n")
    else:
        print(f"Crawler.py failed with return code {return_code}\n")

'''
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)
conf_matrix = confusion_matrix(y_true, y_pred)
#roc_auc = roc_auc_score(y_true, y_pred)
logloss = log_loss(y_true, y_pred)

fpr, tpr, thresholds = roc_curve(y_true, y_pred)
#roc_auc_val = auc(fpr, tpr)

print("\n===== MODEL PERFORMANCE METRICS =====")
print(f"Model Accuracy on new data: {accuracy:.4f}")
print(f"Model Precision on new data: {precision:.4f}")
print(f"Model Recall on new data: {recall:.4f}")
print(f"Model F1 Score on new data: {f1:.4f}")
print(f"Confusion Matrix:\n{conf_matrix}")
#print(f"ROC AUC: {roc_auc:.4f}")
print(f"Log Loss: {logloss:.4f}")
#print(f"ROC Curve AUC: {roc_auc_val:.4f}")
'''

