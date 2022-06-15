import os
from unicodedata import category
from flask import Flask, request, abort, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

# from jmespath import search

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r'*/api/*': {'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
      return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
      try:
        all_categories = Category.query.order_by(Category.id).all()
        
        formatted_categories =  { entry.id: entry.type for entry in all_categories}
        
        return jsonify({
          'success': True,
          'categories': formatted_categories
        })
      except:
        abort(404)
         
         

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
    @app.route('/questions')
    def get_questions():
        try:
          all_questions = Question.query.order_by(Question.id).all()
          all_categories = Category.query.all()

          categories =  { entry.id: entry.type for entry in all_categories}

          page = request.args.get('page', 1, type= int)
          start = (page - 1) * QUESTIONS_PER_PAGE
          end = QUESTIONS_PER_PAGE + start
          
          formatted_questions = [entry.format() for entry in all_questions]

          return jsonify({
            'success': True,
            'questions': formatted_questions[start: end],
            'total_questions': len(formatted_questions),
            'categories': categories
          })
        except:
          abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods= ['DELETE'])
    def delete_question(question_id):
        try:
          question = Question.query.get(question_id)
          if question is None:
            abort(404)
          else:
            question.delete()
            return jsonify({
              'success': True,
              'deleted': True
            })
        except:
          abort(417)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
      body = request.json
      question = body['question']
      answer = body['answer']
      difficulty = body['difficulty']
      category = body['category']
      try:
        new_question = Question(question=question, answer= answer, difficulty= int(difficulty), category= int(category))
        new_question.insert()  
        
        return jsonify({
            'success': True,
            'added': new_question.id
        })
      except:
        abort(422) 

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def search_question():
      try:
        body = request.json
        search_term = body.get('searchTerm').lower()
        if search_term is None:
          abort(422)
        else:
          questions = Question.query.filter(Question.question.like('%{}%'.format(search_term))).all()
          formatted_questions = [entry.format() for entry in questions]

          return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions)
          })
      except:
        abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category>/questions')
    def get_questions_by_category(category):
      try:
        questions = Question.query.filter_by(category= category).all()
        formatted_questions = [entry.format() for entry in questions]
        page = request.args.get('page', 1, type= int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = QUESTIONS_PER_PAGE + start

        return jsonify({
          'success': True,
          'questions': formatted_questions[start: end],
          'total_questions': len(formatted_questions),
          'current_category': category
        })
      except:
        abort(404)
        

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
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
      try:
        body = request.json
        previous_questions_id = body['previous_questions']
        category = body['quiz_category']

        #getting all questions by the category
        all_questions = Question.query.filter_by(category= int(category)).all()
        all_question_id = []

        for entry in all_questions:
          all_question_id.append(entry.id)
        
        # filtering out the previous questions 
        remaining_questions = []
        for data in all_question_id:
          if data not in previous_questions_id:
            remaining_questions.append(data)

        # getting the next question
        next_question_id = random.choice(remaining_questions)
        next_question = Question.query.get(next_question_id).format()
      
        return jsonify({
          'success': True,
          'question': next_question
        })
      except:
        abort(400)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'   
      }), 400

    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not found'   
      }), 404

    @app.errorhandler(422)
    def uprocessable(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': 'Request could not be processed'   
      }), 422

    @app.errorhandler(417)
    def expectation_failed(error):
      return jsonify({
        'success': False,
        'error': 417,
        'message': 'Expectation failed'   
      }), 417

    return app

