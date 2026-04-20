import sys
sys.path.insert(0, '/Users/archijain/Downloads/omni_copilot/backend/tools')
from all_tools import send_email_tool

result = send_email_tool.invoke({"to_email": "jainarchi59@gmail.com", "subject": "Test", "body": "This is a test email triggered by Omni Copilot backend."})
print("Result:", result)
