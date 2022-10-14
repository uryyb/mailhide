from mailhide import app, models

if __name__ == '__main__':
    with app.app_context():
        models.setup_db()