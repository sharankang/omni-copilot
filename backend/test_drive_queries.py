import sys
sys.path.insert(0, '/Users/archijain/Downloads/omni_copilot/backend/tools')
from all_tools import get_drive_service
service = get_drive_service()

queries_to_test = [
    "Archi_resume_scaler.pdf",
    "archi_resume_scaler.pdf",
    "Archi",
    "resume",
    "scaler"
]

for q_val in queries_to_test:
    q = f"name contains '{q_val}'"
    results = service.files().list(q=q, pageSize=10, fields="files(name)").execute()
    print(f"Query: {q:35} -> Results: {[f['name'] for f in results.get('files', [])]}")
