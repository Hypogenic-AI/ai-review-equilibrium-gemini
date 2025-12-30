import unittest
from unittest.mock import MagicMock, patch
from src.reviewer import ReviewerAgent

class TestReviewerAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ReviewerAgent("test-model", "TestAgent")

    @patch('src.reviewer.OpenAI')
    def test_review_parsing(self, mock_openai):
        # Mock the client response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Valid JSON response
        mock_message.content = '{"score": 7, "decision": "Accept", "summary": "Good", "strengths": [], "weaknesses": []}'
        
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Inject mock client into agent (since we can't easily patch the __init__ call's client creation without more work, 
        # we'll just overwrite it after init, assuming the real init doesn't fail without a key if we don't call it.
        # Actually src.reviewer creates client in __init__. We might need to mock env var or patch the class before init.
        # Simpler: just overwrite self.agent.client
        self.agent.client = mock_client
        
        result = self.agent.review("dummy text")
        
        self.assertEqual(result['score'], 7)
        self.assertEqual(result['decision'], "Accept")

    def test_update_review_parsing(self):
        # Mocking the _call_api method directly to avoid complex client mocking
        with patch.object(self.agent, '_call_api', return_value='{"score": 8, "reasoning": "Better"}') as mock_call:
            result = self.agent.update_review("text", {"score": 7}, [{"score": 9}])
            self.assertEqual(result['score'], 8)
            self.assertEqual(result['reasoning'], "Better")

if __name__ == '__main__':
    unittest.main()
