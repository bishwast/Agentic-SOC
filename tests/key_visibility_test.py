import os
from dotenv import load_dotenv
from tools.ip_intel import AbuseIPDBTool

load_dotenv() # Reads the .env file

def test_tool():
    # Calling the method directly on the class definition instead of on an instance. 
    # Object Instantiation
    tool = AbuseIPDBTool()
    # Testing with a known malicious IP or a common public IP
    result = tool._run(ip_address="8.8.8.8")
    print(f"Tool Result: {result}")

# key = os.getenv("ABUSEIPDB_API_KEY")

# if key:
#     print("Success: API Key loaded.")
# else:
#     print("Error: Could not find key in .env")

if __name__ == "__main__":
    test_tool()