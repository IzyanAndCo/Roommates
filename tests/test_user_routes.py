import json
import os
import unittest
from random import randint

from app import create_app, db
from app.models import User


class TestUserBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user
        self.first_test_user = User(username='testUse2', email='testuser1@example.com', password="0000")
        db.session.add(self.first_test_user)
        db.session.commit()

        self.client = self.app.test_client()
        # Get the absolute path of the test data file
        test_data_path = os.path.join(os.path.dirname(__file__), 'data', 'test_users.json')

        # Load the test data from the JSON file
        with open(test_data_path) as f:
            self.test_users = json.load(f)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_user(self):
        # Test getting the test user by ID
        response = self.client.get('/api/users/{}'.format(self.first_test_user.id))
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['id'], self.first_test_user.id)
        self.assertEqual(data['username'], self.first_test_user.username)
        self.assertEqual(data['email'], self.first_test_user.email)

        # Test getting a non-existing user
        response = self.client.get('/api/users/{}'.format(randint(10, 1000)))
        self.assertEqual(response.status_code, 404)

    def test_create_user(self):
        # Test posting a new user with correct data
        test_valid_users = self.test_users.get("ValidUsers")
        for u in test_valid_users:
            response = self.client.post('/api/users', json=u)
            self.assertEqual(response.status_code, 201)
            response_data = response.json
            self.assertEqual(response_data["username"], u["username"])
            self.assertEqual(response_data["email"], u["email"])

        # Test posting a new use with existing email
        existing_email_user = test_valid_users[0]
        existing_email_user["username"] += "1"
        response = self.client.post('/api/users', json=existing_email_user)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Email", response.json.get("error"))

        # Test posting a new user with existing username
        existing_username_user = test_valid_users[1]
        existing_username_user["email"] += "a"
        response = self.client.post('/api/users', json=existing_username_user)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Username", response.json.get("error"))

    def test_create_user_invalid_username(self):
        # Test posting a user with invalid usernames
        test_users_invalid_username = self.test_users.get("InvalidUsernameUsers")
        for u in test_users_invalid_username:
            response = self.client.post('/api/users', json=u)
            self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_email(self):
        # Test posting a user with invalid emails
        test_users_invalid_username = self.test_users.get("InvalidUsernameUsers")
        for u in test_users_invalid_username:
            response = self.client.post('/api/users', json=u)
            self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_password(self):
        # Test posting a user with invalid passwords
        test_users_invalid_username = self.test_users.get("InvalidUsernameUsers")
        for u in test_users_invalid_username:
            response = self.client.post('/api/users', json=u)
            self.assertEqual(response.status_code, 400)