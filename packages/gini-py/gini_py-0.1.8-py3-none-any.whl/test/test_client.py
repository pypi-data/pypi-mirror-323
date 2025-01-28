import unittest
from gini_py import GiniClient, Attachment
from pathlib import Path

class TestGiniClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "g1SnTWfmJzY800ydIjtkD5ZzKqeFq8q9inQ2wcKWVaU="
        self.client = GiniClient(
            api_key=self.api_key,
            port=8001,
            host="localhost"
        )
        
        # Create a test file for attachment testing
        self.test_file_path = Path("test/test_file.txt")
        with open(self.test_file_path, "w") as f:
            f.write("This is a test file content")

    def tearDown(self):
        if self.test_file_path.exists():
            self.test_file_path.unlink()

    def test_basic_execution(self):
        """Test basic Gini execution without attachments"""
        response = self.client.execute_gini(
            input="What is the weather like today?",
            attachments=[]
        )

        print("\nBasic execution response:")
        print(f"Response: {response.response}")
        print (f"Type of response: {type(response.response)}")
        # Simply verify we get a GiniResponse object
        self.assertIsNotNone(response)

    def test_execution_with_attachment(self):
        """Test Gini execution with file attachment"""
        attachment = Attachment.from_path(str(self.test_file_path))
        response = self.client.execute_gini(
            input="Can you read the contents of this file using the read tool?",
            attachments=[attachment]
        )

        print("\nExecution with attachment response:")
        print(f"Response: {response.response}")
        print (f"Type of response: {type(response.response)}")
        

        # Simply verify we get a GiniResponse object
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main() 