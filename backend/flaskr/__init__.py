import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def random_question(questions):
    # Function to get random question
    index = random.randint(0, len(questions) - 1)
    question = questions[index]

    return question


def paginate_questions(request, selection):
    # Function to paginate questions
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS'
        )
        return response

    # GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def retrieve_categories():
        try:
            categories = Category.query.order_by(Category.type).all()

            if len(categories) == 0:
                abort(404)
            else:
                return jsonify({
                    'success': True,
                    'categories': [cat.format() for cat in categories],
                    'total_categories': len(categories)
                }), 200
        except BaseException:
            abort(500)

    # GET requests for questions, including pagination (every 10 questions).
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.type).all()

        if len(current_questions) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'categories': [category.format() for category in categories]
            }), 200

    # DELETE question using a question ID
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': [question.format() for question in selection],
                'total_questions': len(selection)
            }), 200
        except BaseException:
            abort(422)

    # POST a new question
    @app.route('/questions', methods=['POST'])
    def create_questions():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if new_question == "" or new_answer == "no answer":
            abort(400)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )

            question.insert()

            selection = Question.query.order_by(Question.id).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in selection]
            })
        except BaseException:
            abort(422)

    # POST endpoint to get questions based on a search term.
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()

        search = body.get('searchTerm', None)

        try:
            selection = Question.query.order_by(
                Question.id).filter(
                Question.question.ilike(
                    '%{}%'.format(search)))

            return jsonify({
                'success': True,
                'questions': [question.format() for question in selection]
            }), 200
        except BaseException:
            abort(422)

    # GET endpoint to get questions based on category.
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_categories_questions(category_id):
        selection = Question.query.filter_by(category=category_id).all()
        questions = [question.format() for question in selection]

        if len(questions) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(selection),
                'current_category': category_id
            }), 200

    # POST endpoint to get questions to play the quiz.
    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():
        body = request.get_json()

        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)

        try:

            questions = Question.query.all()

            if quiz_category['id'] != 0:
                questions = Question.query.filter_by(
                    category=quiz_category['id']).all()

            next_question = random_question(questions)

            selected = False
            question_count = 0

            while selected is False:
                if next_question.id in previous_questions:
                    next_question = random_question(questions)
                else:
                    selected = True
                if question_count == len(questions):
                    break
                question_count += 1

            next_question = next_question.format()
            return jsonify({
                'success': True,
                'question': next_question
            }), 200
        except BaseException:
            abort(422)

    # Error handlers for all expected errors
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
