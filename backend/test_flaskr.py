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
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'postgres',
                                                             'localhost:5432', self.database_name)
        setup_db(self.app)#, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {"question": "Who was Napoleon Bonapart?", 
                            "answer": "French Emperor and General", 
                            "difficulty": 2,
                            "category:": 4}
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertEqual(data["current_category"], "Science")

    def test_404_get_questions_beyond_valid(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_delete_question(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)

        question = Question.query.filter(Question.id == 5).one_or_none()
        self.assertEqual(question, None)

    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        pass

    def test_search_question(self):
        res = self.client().post("/questions", json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 1)
        self.assertTrue(data["questions"])

    def test_list_question_of_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 4)
        self.assertEqual(data['current_category'], 'Art')

    def test_category_not_present(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_quiz_question_left(self):
        res = self.client().post('/quizzes',json={"previous_questions":[16,17,18],"quiz_category":{"type":"Art", "id":2}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['question']['id'],19)
        self.assertEqual(data['question']["difficulty"],2)
        self.assertEqual(data["forceEnd"],False)

    def test_quiz_no_question_left(self):
        res = self.client().post('/quizzes',json={"previous_questions":[16,17,18,19],"quiz_category":{"type":"Art", "id":2}})
        data = json.loads(res.data)    

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['question'],None)
        self.assertEqual(data["forceEnd"],True)   

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()