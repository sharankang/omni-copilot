import sys
sys.path.insert(0, '/Users/archijain/Downloads/omni_copilot/backend/tools')
from all_tools import get_drive_service
service = get_drive_service()
results = service.files().list(q="name contains 'Archi'", pageSize=20, fields="files(name)").execute()
print("Archi files:", results)
results_all = service.files().list(pageSize=20, fields="files(name)").execute()
print("All files:", results_all)
