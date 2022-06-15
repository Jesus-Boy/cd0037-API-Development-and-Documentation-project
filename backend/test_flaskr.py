import os
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:1234@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.test_question = {
          'question': 'What is the capital of France?',
          'answer': 'Paris',
          'category': 2,
          'difficulty': 2 
        }

        self.test_quiz = {
          'previous_questions': [2, 5],
          'quiz_category': 3
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Expected behaviour
    def test_get_categories(self):
      response = self.client().get('/categories')
      self.assertEqual(response.status_code, 200)

    def test_get_questions(self):
      response = self.client().get('/questions')
      body = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertTrue(body['total_questions'])
      self.assertTrue(len(body['questions']))
      self.assertTrue(len(body['categories']))

    def test_add_question(self):
      response = self.client().post('/questions', json = self.test_question)
      body = json.loads(response.data)
      added_question = Question.query.get(body['added'])
      self.assertEqual(response.status_code, 200)
      self.assertTrue(body['success'])

    def test_delete_question(self):
      response = self.client().delete('/questions/3')
      body = json.loads(response.data)
      self.assertEqual(response.status_code, 200)
      self.assertTrue(body['success'])
      self.assertTrue(body['deleted'])

    
    def test_search_question(self):
      response = self.client().post('/questions', json= {'searchTerm':'what'})

      body = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertTrue(body['questions'])
      self.assertTrue(body['total_questions'])

    def test_get_questions_by_categories(self):
      response = self.client().get('/categories/5/questions')

      body = json.loads(response.data)
      self.assertEqual(response.status_code, 200)
      self.assertTrue(body['total_questions'])
      self.assertTrue(body['questions'])

    def test_get_quiz(self):
      response = self.client().post('/quizzes', json= self.test_quiz)

      body = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertTrue(body['success'])
      self.assertTrue(body['next_question'])

    # Expected errors
    def test_page_not_found(self):
      response = self.client().get('/questions?page=35')

      data = json.loads(response.data)
      self.assertEqual(response.status_code, 404)
      self.assertEqual(data['error'], 404)
      self.assertEqual(data['message'], 'Not found')

    def test_bad_request(self):
      response = self.client().post('/quizzes', json= {
        'previous_questions': [200],
        'quiz-category': 50
      })

      data = json.loads(response.data)
      self.assertEqual(response.status_code, 400)
      self.assertEqual(data['error'], 400)
      self.assertEqual(data['mesaage'], 'Bad request')

    def test_unprocesable(self):
      response = self.client().post('/questions', json= {})

      data = json.loads(response.data)
      self.assertEqual(response.status_code, 422)
      self.assertEqual(data['error'], 422)  
      self.assertEqual(data['mesaage'], 'Request could not be processed')

    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()