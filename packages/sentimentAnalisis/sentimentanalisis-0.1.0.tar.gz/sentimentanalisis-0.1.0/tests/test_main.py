import unittest  
from sentimenAnalisis.main import main  
  
class TestSentimentAnalysis(unittest.TestCase):  
      
    def test_main_function(self):  
        # Uji apakah fungsi main tidak menghasilkan error  
        try:  
            main()  
            result = True  
        except Exception as e:  
            result = False  
        self.assertTrue(result)  
  
if __name__ == '__main__':  
    unittest.main()  
