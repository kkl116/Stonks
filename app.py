from flask_app import create_app, scheduler
app = create_app()

if __name__ == '__main__':
    app.debug = False 
    #start apscheduler
    with app.app_context():
        from flask_app.scheduled import tasks
        scheduler.start()

    app.run(threaded=True)