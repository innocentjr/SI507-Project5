import unittest
from SI507project5_code import *

###########

# REMEMBER, these tests DO NOT test everything in the project.
class RunningSimpleTests(unittest.TestCase):

	def setUp(self):
		self.subcategories = open("eventbrite.json")
		self.events = open("events.json")
		self.super_token = open("super_token.json")
		self.chicago_events = open("SomeEventsinChicago.csv")
		self.subcategories_csv =open("EventbriteSubcategories.csv")

	def test_files_exist(self):
		self.assertTrue(json.loads(self.subcategories.read()))
		self.assertTrue(json.loads(self.events.read()))
		self.assertTrue(json.loads(self.super_token.read()))
		self.assertTrue(csv.reader(self.chicago_events))
		self.assertTrue(csv.reader(self.subcategories_csv))

	def tearDown(self):
		self.subcategories.close()
		self.events.close()
		self.super_token.close()
		self.chicago_events.close()
		self.subcategories_csv.close()

	def test_AUTH_url(self):
		self.assertTrue(AUTHORIZATION_BASE_URL, 'https://www.eventbrite.com/oauth/authorize')

	def test_TOKEN_url(self):
		self.assertTrue(TOKEN_URL, 'https://www.eventbrite.com/oauth/token')

	def test_REDIRECT_uri(self):
		self.assertTrue(REDIRECT_URI, 'http://localhost:8000')

	def test_PORT(self):
		self.assertTrue(port, 8000)

	def test_clientID(self):
		self.assertEqual(APP_ID, None)

	def test_clientSecret(self):
		self.assertEqual(APP_SECRET, None)

	def test_ExpireCondition(self):
		self.assertEqual(has_cache_expired("2017-11-10 11:57:37.541703", 1), True)

if __name__ == "__main__":
    unittest.main(verbosity=2)
