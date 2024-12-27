import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request,selection):
    page = request.args.get("page",1,type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_array = [category.format()["type"] for category in categories]

        return jsonify(
            {
                "success": True,
                "categories": categories_array,
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request,selection)
        
        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.all()
        categories_array = [category.format()['type']  for category in categories]
        
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "categories": categories_array,
                "current_category": categories_array[0],
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id
                }
            )
        
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    # @app.route("/questions", methods=["POST"])
    @app.route("/questions", methods=["POST"])
    def post_question():
        
        body = request.get_json()

        searchTerm = body.get("searchTerm", None)

        if searchTerm:

            try:

                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                )
                current_questions = paginate_questions(request,selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(current_questions),
                        "current_category": None,
                    }
                )
            except:
                abort(422)
        
        else:
        
            try:

                new_question = body.get("question", None)
                new_answer = body.get("answer", None)
                new_difficulty = body.get("difficulty", None)
                new_category = body.get("category", None)

                if new_question is None:
                    raise Exception("No valid input")
                if new_answer is None:
                    raise Exception("No valid input")
                if new_difficulty is None:
                    raise Exception("No valid input")
                if new_category is None:
                    raise Exception("No valid input")
                
                question = Question(question=new_question, 
                                    answer=new_answer, 
                                    category=new_category,
                                    difficulty=new_difficulty)
                
                question.insert()

                return jsonify(
                    {
                        "success": True
                    }
                )

            except:
                abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def list_questions_of_category(category_id):
        
        try:
            current_category = Category.query.filter(
                Category.id == (category_id+1)).one_or_none()
            
            if current_category is None:
                abort(404)

            questions = Question.query.filter(
                Question.category==current_category.id).all()
            
            question_formatted = [question.format() for question in questions]

            category_formatted = current_category.format()["type"]

            return jsonify(
                    {
                    "success": True,
                    "questions": question_formatted,
                    "total_questions": len(question_formatted),
                    "current_category": category_formatted,
                    }
                )

        except:
            abort(422)



    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes",methods=["POST"])
    def get_next_question():

        body = request.get_json()

        previous_questions=body.get("previous_questions")
        quiz_category=body.get("quiz_category")

        try:
            if quiz_category['type'] != 'All':
                # determine id of current category
                current_category = Category.query.filter(
                    Category.type == (quiz_category['type'])).one_or_none()
                
                # Checking, if category exists
                if current_category is None:
                    abort(404)

                # filter a selection of questions for category
                selection = Question.query.filter(
                    Question.category==current_category.id).all()
            else:
                selection = Question.query.all()
            
            sub_selection = \
                [question for question in selection 
                 if question.id not in previous_questions]
            
            # Checking, if questions are left
            # if questions still exist ..
            if len(sub_selection)>0:
                # select a question randomly
                random_question = random.choice(sub_selection)
                return jsonify({
                    "success": True,
                    "previousQuestions": previous_questions,
                    "question": random_question.format(),
                    "guess": "",
                    "forceEnd": False
                })
            else:
                # else end game and return question as None
                random_question = None
                return jsonify({
                    "success": True,
                    "previousQuestions": previous_questions,
                    "question": None,
                    "guess": "",
                    "forceEnd": True
                })

        except:
            abort(422)



    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return(
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404
        )
    
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success":False, "error": 422, "message":"unprocessable"}),
            422,
        )

    return app

