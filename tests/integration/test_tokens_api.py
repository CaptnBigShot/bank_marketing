from requests.auth import _basic_auth_str
from datetime import datetime


class TestTokensApi:
    def test_get_token(self, app, user):
        with app.test_client() as client:
            authorization = _basic_auth_str(user.username, app.config['TEST_PASSWORD'])
            response = client.post("/api/tokens", headers={"Authorization": authorization})
            data = response.get_json()
            assert response.status_code == 200
            assert user.token == data['token']

    def test_get_token_as_unauthorized_user(self, app, user):
        with app.test_client() as client:
            authorization = _basic_auth_str(user.username, app.config['TEST_PASSWORD'] + 'x')
            response = client.post("/api/tokens", headers={"Authorization": authorization})
            data = response.get_json()
            assert response.status_code == 401
            assert data == {'error': 'Unauthorized'}

    def test_revoke_token(self, app, user):
        with app.test_client() as client:
            response = client.delete("/api/tokens", headers={"Authorization": 'Bearer ' + user.get_token()})
            assert response.status_code == 204
            assert user.token_expiration < datetime.utcnow()
