import unittest
from chatbot_with_weather import chat_with_weather_bot

class TestChatbotWithWeather(unittest.TestCase):
    def test_weather_query(self):
        response = chat_with_weather_bot("weather in London")
        # Expect response to be a string with 'Weather' keyword or 'Failed' for API failure
        self.assertTrue(isinstance(response, str))
        self.assertTrue("Weather" in response or "Failed" in response)

    def test_normal_chat(self):
        response = chat_with_weather_bot("Hello")
        self.assertTrue(isinstance(response, str))
        self.assertNotEqual(response.strip(), "")

if __name__ == '__main__':
    unittest.main()
