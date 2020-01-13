import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_user = "postgres"
        self.database_pass = ""
        self.database_host = "localhost:5432"
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            self.database_user,
            self.database_pass,
            self.database_host,
            self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who is the best artiste in Nigeria',
            'answer': 'Burna Boy',
            'category': 5,
            'difficulty': 5
        }

        self.empty_question = {
            'question': '',
            'answer': '',
            'category': 5,
            'difficulty': 5
        }

        self.new_play_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Entertainment',
                'id': 1
            }
        }

        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # Create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

    def test_404_invalid_page_get_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_delete_book(self):
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 6).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 6)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_400_if_question_field_empty(self):
        res = self.client().post('/questions', json=self.empty_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    def test_get_question_search_with_results(self):
        res = self.client().post(
            '/questions/search',
            json={
                'searchTerm': 'hank'
            }
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_get_question_search_without_results(self):
        res = self.client().post(
            '/questions/search',
            json={
                'search': 'applejacks'
            }
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)

    def test_get_categories_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 1)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_play_quizzes(self):
        res = self.client().post('/quizzes', json=self.new_play_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

# dropdb trivia_test && createdb trivia_test
# psql trivia_test < trivia.psql && python test_flaskr.py


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
