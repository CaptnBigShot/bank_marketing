from app.models import User


class TestUser:
    def test_password_hashing(self):
        # noinspection PyArgumentList
        u = User(username='garwin')
        u.set_password('correct')
        assert u.check_password('correct')
        assert not u.check_password('incorrect')


