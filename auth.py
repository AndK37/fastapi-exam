import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from config import settings

class AuthHandler:
    security = HTTPBearer()

    context = CryptContext(
        schemes=['bcrypt'],
        deprecated='auto'
    )

    secret = settings.JWT_SECRET_KEY

    def get_password_hash(self, password):
        return self.context.hash(password)

    def verify_password(self, plain, hashed):
        return self.context.verify(plain, hashed)

    def encode_token(self, data):
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc),
            'sub': data
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=['HS256']
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, 'Просрочено')
        except jwt.InvalidTokenError:
            raise HTTPException(401, 'Плохой токен')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)