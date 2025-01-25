from datetime import datetime, timedelta, timezone

import jwt
from connector.generated import JWTClaims, JWTCredential, JWTHeaders
from connector.utils.jwt_utils import sign_jwt

# Create test credentials
test_claims = JWTClaims(iss="test-issuer", aud="test-audience")
test_headers = JWTHeaders(kid="test-key-id", alg="HS256")
credentials = JWTCredential(secret="test-secret", claims=test_claims, headers=test_headers)


def test_sign_jwt():
    # Sign JWT
    token = sign_jwt(credentials)

    # Decode and verify token
    decoded = jwt.decode(
        token,
        "test-secret",
        algorithms=["HS256"],
        audience="test-audience",
        options={"verify_signature": True},
    )

    # Verify claims
    assert decoded["iss"] == "test-issuer"
    assert decoded["aud"] == "test-audience"

    # Verify timestamps
    now = datetime.now(timezone.utc)

    # iat is the current time
    assert abs(decoded["iat"] - int(now.timestamp())) < 2  # Allow 2 sec difference

    # exp is the current time + 20 minutes
    assert abs(decoded["exp"] - int((now + timedelta(minutes=20)).timestamp())) < 2


def test_sign_jwt_custom_expiration():
    # Sign JWT with custom expiration
    token_custom = sign_jwt(credentials, expiration_minutes=30)

    # Verify custom expiration
    decoded_custom = jwt.decode(
        token_custom,
        "test-secret",
        algorithms=["HS256"],
        audience="test-audience",
        options={"verify_signature": True},
    )

    # Verify custom expiration
    now = datetime.now(timezone.utc)

    # exp is the current time + custom set expiration time 30 minutes
    assert abs(decoded_custom["exp"] - int((now + timedelta(minutes=30)).timestamp())) < 2
