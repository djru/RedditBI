from application import application
import db

if __name__ == "__main__":
    db.create_table()
    application.run()