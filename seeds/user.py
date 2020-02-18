from flask_seeder import Seeder
from app import db
from app.models import User


class UserSeeder(Seeder):
    def __init__(self):
        super().__init__(db=db)
        self.priority = 10

    def run(self):
        user = User(username='test', email='test@example.com')
        user.set_password('test')
        db.session.add(user)
