import unittest
from unittest.mock import patch
from deepseek_reason_extractor import DeepseekReasonExtractor

class TestDeepseekReasonExtractor(unittest.TestCase):
    @patch('deepseek_reason_extractor.core.vaklm')
    def test_extract_reasoning(self, mock_vaklm):
        # Setup mock
        mock_vaklm.return_value = "Test reasoning output"
        
        # Initialize extractor
        extractor = DeepseekReasonExtractor()
        
        # Test extraction
        result = extractor.extract_reasoning("Test prompt")
        
        # Assertions
        self.assertEqual(result, "Test reasoning output")
        mock_vaklm.assert_called_once()

    @patch('deepseek_reason_extractor.core.vaklm')
    def test_error_handling(self, mock_vaklm):
        # Setup mock to raise exception
        mock_vaklm.side_effect = Exception("Test error")
        
        extractor = DeepseekReasonExtractor()
        
        with self.assertRaises(RuntimeError):
            extractor.extract_reasoning("Test prompt")

if __name__ == '__main__':
    unittest.main()
