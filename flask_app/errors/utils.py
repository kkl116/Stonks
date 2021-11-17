from flask import jsonify, request, url_for

#error handling
def form_errors_400(form):
    return jsonify(form.errors), 400

def error_message(e):
    current_route = request.path
    print('*****route:', current_route, '\t error:', str(e), '*****')

def error_500_response(e):
    error_message(e)
    return jsonify({'url_500': url_for('errors.error_500')}), 500

def error_500_handler(route):
    """decorator for routes"""
    def wrapper(*args, **kwargs):
        try:
            return route(*args, **kwargs)
        except Exception as e:
            error_500_response(e)
    
    """for routes there cannot be name collisions - if the inner funcs'
    name is just WRAPPER for this decorator, it will change the route name itself
    when the decorator is used, so have to change the func name back to route name"""
    wrapper.__name__ = route.__name__
    return wrapper