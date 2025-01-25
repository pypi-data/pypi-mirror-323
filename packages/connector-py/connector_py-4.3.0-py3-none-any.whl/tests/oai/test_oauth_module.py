from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from connector.generated import (
    GetAuthorizationUrl,
    GetAuthorizationUrlRequest,
    HandleAuthorizationCallback,
    HandleAuthorizationCallbackRequest,
    HandleClientCredentials,
    HandleClientCredentialsRequest,
    OAuthCredential,
    RefreshAccessToken,
    RefreshAccessTokenRequest,
    StandardCapabilityName,
)
from connector.httpx_rewrite import AsyncClient
from connector.oai.capability import AuthRequest, get_settings
from connector.oai.errors import ConnectorError
from connector.oai.integration import DescriptionData, Integration
from connector.oai.modules.oauth_module import OAuthModule
from connector.oai.modules.oauth_module_types import (
    ClientAuthenticationMethod,
    OAuthFlowType,
    OAuthRequest,
    OAuthSettings,
    RequestDataType,
    RequestMethod,
)
from httpx import Request, Response
from pydantic import BaseModel, ValidationError


class Settings(BaseModel):
    subdomain: str


@pytest.fixture
def settings():
    return Settings(subdomain="test")


@pytest.fixture
def integration():
    """
    FIXTURE: Create an integration with an OAuthModule
    """
    return Integration(
        app_id="test_app",
        auth=OAuthCredential,
        version="0.1.0",
        exception_handlers=[],
        settings_model=Settings,
        oauth_settings=OAuthSettings(
            authorization_url="https://example.com/auth",
            token_url="https://example.com/token",
            scopes={
                StandardCapabilityName.VALIDATE_CREDENTIALS: "test:scope another:scope",
                StandardCapabilityName.LIST_ACCOUNTS: "test:scope another:scope",
            },
        ),
        description_data=DescriptionData(user_friendly_name="test_oauth_module.py", categories=[]),
    )


@pytest.fixture
def client_credentials_integration():
    return Integration(
        app_id="test_app",
        auth=OAuthCredential,
        version="0.1.0",
        exception_handlers=[],
        settings_model=Settings,
        oauth_settings=OAuthSettings(
            flow_type=OAuthFlowType.CLIENT_CREDENTIALS,
            token_url="https://example.com/token",
            scopes={
                StandardCapabilityName.VALIDATE_CREDENTIALS: "test:scope another:scope",
                StandardCapabilityName.LIST_ACCOUNTS: "test:scope another:scope",
            },
        ),
        description_data=DescriptionData(user_friendly_name="test_oauth_module.py", categories=[]),
    )


def get_oauth_module(integration: Integration) -> OAuthModule:
    """
    HELPER: Get the OAuthModule from the integration
    """
    for module in integration.modules:
        if isinstance(module, OAuthModule):
            return module
    raise ValueError("OAuthModule not found")


def test_get_scopes(integration):
    """
    Test if OAuthModule correctly returns the scopes defined in the integration settings
    """
    module = get_oauth_module(integration)
    scopes = module._get_scopes()
    assert set(scopes.split()) == {"test:scope", "another:scope"}


@pytest.mark.asyncio
async def test_dynamic_authorization_url(integration):
    """
    Test if OAuthModule correctly handles dynamic authorization URLs based on settings
    """

    def get_auth_url(args: AuthRequest) -> str:
        settings = get_settings(args, integration.settings_model)
        return f"https://{settings.subdomain}.example.com/auth"

    integration.oauth_settings.authorization_url = get_auth_url

    request = GetAuthorizationUrlRequest(
        request=GetAuthorizationUrl(
            client_id="test_client_id",
            redirect_uri="https://example.com/callback",
            state="test_state",
            scopes=["scope1"],
        ),
        settings={"subdomain": "test"},
    )

    response = await integration.capabilities[StandardCapabilityName.GET_AUTHORIZATION_URL](request)

    parsed_url = urlparse(response.response.authorization_url)
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == "test.example.com"
    assert parsed_url.path == "/auth"


@pytest.mark.asyncio
async def test_dynamic_token_url(integration):
    """
    Test if OAuthModule correctly handles dynamic token URLs based on settings
    """

    def get_token_url(args: AuthRequest) -> str:
        settings = get_settings(args, integration.settings_model)
        return f"https://{settings.subdomain}.example.com/token"

    integration.oauth_settings.token_url = get_token_url

    request = HandleAuthorizationCallbackRequest(
        request=HandleAuthorizationCallback(
            client_id="test_client_id",
            client_secret="test_secret",
            redirect_uri_with_code="https://example.com/callback?code=test_code",
        ),
        settings={"subdomain": "test"},
    )

    mock_response = Response(
        200,
        json={"access_token": "test_token", "token_type": "bearer"},
        request=Request("POST", "https://test.example.com/token"),
    )

    with patch.object(AsyncClient, "request", return_value=mock_response) as mock_request:
        await integration.capabilities[StandardCapabilityName.HANDLE_AUTHORIZATION_CALLBACK](
            request
        )

        mock_request.assert_called_once()
        assert mock_request.call_args.kwargs["url"] == "https://test.example.com/token"


@pytest.mark.asyncio
async def test_get_authorization_url(integration):
    """
    Test if OAuthModule correctly constructs the authorization URL
    """
    request = GetAuthorizationUrlRequest(
        request=GetAuthorizationUrl(
            client_id="test_client_id",
            redirect_uri="https://example.com/callback",
            state="test_state",
            scopes=["scope1", "scope2", "scope3"],
        )
    )

    response = await integration.capabilities[StandardCapabilityName.GET_AUTHORIZATION_URL](request)

    parsed_url = urlparse(response.response.authorization_url)

    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == "example.com"
    assert parsed_url.path == "/auth"

    assert "client_id=test_client_id" in parsed_url.query
    assert "redirect_uri=https://example.com/callback" in parsed_url.query
    assert "state=test_state" in parsed_url.query
    assert "scope=scope1 scope2 scope3" in parsed_url.query


@pytest.mark.asyncio
async def test_get_authorization_url_no_input_scopes(integration):
    """
    Test if OAuthModule falls back to the scopes defined in the integration settings
    if no scopes are provided in the request to the connector
    """
    request = GetAuthorizationUrlRequest(
        request=GetAuthorizationUrl(
            client_id="test_client_id",
            redirect_uri="https://example.com/callback",
            state="test_state",
            scopes=[],
        )
    )

    response = await integration.capabilities[StandardCapabilityName.GET_AUTHORIZATION_URL](request)

    parsed_url = urlparse(response.response.authorization_url)
    scopes = parse_qs(parsed_url.query).get("scope", [""])[0].split()
    assert set(scopes) == {"another:scope", "test:scope"}


@pytest.mark.asyncio
async def test_handle_authorization_callback(integration):
    """
    Test if OAuthModule correctly handles the authorization callback
    """
    request = HandleAuthorizationCallbackRequest(
        request=HandleAuthorizationCallback(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri_with_code="https://example.com/callback?code=test_code",
        ),
        include_raw_data=True,
    )

    mock_response = Response(
        200,
        json={
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",
        },
        request=Request("POST", "https://example.com/token"),
    )

    with patch.object(AsyncClient, "request", return_value=mock_response):
        response = await integration.capabilities[
            StandardCapabilityName.HANDLE_AUTHORIZATION_CALLBACK
        ](request)

    assert response.response.access_token == "test_access_token"
    assert response.response.token_type == "bearer"
    assert response.response.refresh_token == "test_refresh_token"
    assert response.raw_data is not None


@pytest.mark.asyncio
async def test_handle_client_credentials_request(client_credentials_integration):
    """
    Test if OAuthModule correctly handles the client credentials request
    """
    request = HandleClientCredentialsRequest(
        request=HandleClientCredentials(
            client_id="test_client_id",
            client_secret="test_client_secret",
            scopes=["scope1", "scope2", "scope3"],
        ),
        include_raw_data=True,
    )

    mock_response = Response(
        200,
        json={
            "access_token": "test_access_token",
            "token_type": "Bearer",
        },
        request=Request("POST", "https://example.com/token"),
    )

    with patch.object(AsyncClient, "request", return_value=mock_response):
        response = await client_credentials_integration.capabilities[
            StandardCapabilityName.HANDLE_CLIENT_CREDENTIALS_REQUEST
        ](request)

    assert response.response.access_token == "test_access_token"
    assert response.response.token_type == "bearer"
    assert response.raw_data is not None


@pytest.mark.asyncio
async def test_refresh_access_token(integration):
    """
    Test if OAuthModule correctly refreshes the access token
    """
    request = RefreshAccessTokenRequest(
        request=RefreshAccessToken(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token",
        ),
        include_raw_data=True,
    )

    mock_response = Response(
        200,
        json={
            "access_token": "new_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "new_refresh_token",
        },
        request=Request("POST", "https://example.com/token"),
    )

    with patch.object(AsyncClient, "request", return_value=mock_response):
        response = await integration.capabilities[StandardCapabilityName.REFRESH_ACCESS_TOKEN](
            request
        )

    assert response.response.access_token == "new_access_token"
    assert response.response.token_type == "bearer"
    assert response.response.refresh_token == "new_refresh_token"
    assert response.raw_data is not None


@pytest.mark.asyncio
async def test_send_authorized_request_client_secret_basic(integration):
    """
    Test if OAuthModule correctly constructs the request for the token endpoint
    when using client secret basic authentication (header auth)
    """
    module = get_oauth_module(integration)
    module.settings.client_auth = ClientAuthenticationMethod.CLIENT_SECRET_BASIC

    request = HandleAuthorizationCallbackRequest(
        request=HandleAuthorizationCallback(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri_with_code="https://example.com/callback?code=test_code",
        )
    )

    mock_response = Response(
        200,
        json={
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",
        },
        request=Request("POST", "https://example.com/token"),
    )

    mock_client = AsyncMock(spec=AsyncClient)
    mock_client.request.return_value = mock_response

    await module._send_authorized_request(
        "https://example.com/token", "authorization_code", mock_client, request
    )

    mock_client.request.assert_called_once()
    call_args = mock_client.request.call_args
    assert call_args.kwargs["auth"] is not None
    assert "client_id" not in call_args.kwargs["data"]
    assert "client_secret" not in call_args.kwargs["data"]


@pytest.mark.asyncio
async def test_send_authorized_request_query_request_type(integration):
    """
    Test if OAuthModule correctly constructs the request for the token endpoint
    when using a request type with QUERY as the data parameter
    """
    module = get_oauth_module(integration)
    module.settings.request_type = OAuthRequest(
        method=RequestMethod.GET, data=RequestDataType.QUERY
    )

    request = RefreshAccessTokenRequest(
        request=RefreshAccessToken(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token",
        )
    )

    mock_response = Response(
        200,
        json={
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",
        },
        request=Request("POST", "https://example.com/token"),
    )

    mock_client = AsyncMock(spec=AsyncClient)
    mock_client.request.return_value = mock_response

    await module._send_authorized_request(
        "https://example.com/token", "refresh_token", mock_client, request
    )

    mock_client.request.assert_called_once()
    call_args = mock_client.request.call_args
    assert call_args.kwargs["method"] == "GET"
    assert call_args.kwargs["params"] is not None
    assert call_args.kwargs["data"] is None
    assert call_args.kwargs["json"] is None


@pytest.mark.asyncio
async def test_send_authorized_request_json_request_type(integration):
    """
    Test if OAuthModule correctly constructs the request for the token endpoint
    when using a request type with JSON as the data parameter
    """
    module = get_oauth_module(integration)
    module.settings.request_type = OAuthRequest(method=RequestMethod.GET, data=RequestDataType.JSON)

    request = RefreshAccessTokenRequest(
        request=RefreshAccessToken(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token",
        )
    )

    mock_response = Response(
        200,
        json={
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",
        },
        request=Request("GET", "https://example.com/token"),
    )

    mock_client = AsyncMock(spec=AsyncClient)
    mock_client.request.return_value = mock_response

    await module._send_authorized_request(
        "https://example.com/token", "refresh_token", mock_client, request
    )

    mock_client.request.assert_called_once()
    call_args = mock_client.request.call_args
    assert call_args.kwargs["method"] == "GET"
    assert call_args.kwargs["params"] is None
    assert call_args.kwargs["data"] is None
    assert call_args.kwargs["json"] is not None


@pytest.mark.asyncio
async def test_send_authorized_request_formdata_request_type(integration):
    """
    Test if OAuthModule correctly constructs the request for the token endpoint
    when using a request type with FORMDATA as the data parameter
    """
    module = get_oauth_module(integration)
    module.settings.request_type = OAuthRequest(
        method=RequestMethod.GET, data=RequestDataType.FORMDATA
    )

    request = RefreshAccessTokenRequest(
        request=RefreshAccessToken(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token",
        )
    )

    mock_response = Response(
        200,
        json={
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",
        },
        request=Request("POST", "https://example.com/token"),
    )

    mock_client = AsyncMock(spec=AsyncClient)
    mock_client.request.return_value = mock_response

    await module._send_authorized_request(
        "https://example.com/token", "refresh_token", mock_client, request
    )

    mock_client.request.assert_called_once()
    call_args = mock_client.request.call_args
    assert call_args.kwargs["method"] == "GET"
    assert call_args.kwargs["params"] is None
    assert call_args.kwargs["data"] is not None
    assert call_args.kwargs["json"] is None


@pytest.mark.asyncio
async def test_handle_authorization_callback_error(integration):
    """
    Test if OAuthModule correctly handles errors during authorization callback
    """
    request = HandleAuthorizationCallbackRequest(
        request=HandleAuthorizationCallback(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri_with_code="https://example.com/callback?code=test_code",
        ),
        include_raw_data=True,
    )

    mock_response = Response(
        400,
        json={"error": "invalid_grant", "error_description": "Invalid authorization code"},
        request=Request("POST", "https://example.com/token"),
    )

    with patch.object(AsyncClient, "request", return_value=mock_response):
        with pytest.raises(ConnectorError):
            await integration.capabilities[StandardCapabilityName.HANDLE_AUTHORIZATION_CALLBACK](
                request
            )


@pytest.mark.asyncio
async def test_invalid_grant_type(integration):
    """
    Test if OAuthModule correctly handles an invalid grant type
    """
    module = get_oauth_module(integration)
    request = RefreshAccessTokenRequest(
        request=RefreshAccessToken(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token",
        )
    )

    mock_client = AsyncMock(spec=AsyncClient)
    with pytest.raises(ValueError, match="Unsupported grant_type"):
        await module._send_authorized_request(
            "https://example.com/token", "invalid_grant_type", mock_client, request
        )


@pytest.mark.asyncio
async def test_oauth_credentials_conversion_error(integration):
    """
    Test if OAuthModule correctly handles errors when converting raw JSON to OAuthCredentials
    """
    request = HandleAuthorizationCallbackRequest(
        request=HandleAuthorizationCallback(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri_with_code="https://example.com/callback?code=test_code",
        ),
        include_raw_data=True,
    )

    mock_response = Response(
        200,
        json={
            # Missing required fields
            "some_other_field": "value",
        },
        request=Request("POST", "https://example.com/token"),
    )

    with patch.object(AsyncClient, "request", return_value=mock_response):
        with pytest.raises(ValidationError, match="1 validation error for OauthCredentials"):
            await integration.capabilities[StandardCapabilityName.HANDLE_AUTHORIZATION_CALLBACK](
                request
            )


@pytest.mark.asyncio
async def test_handle_authorization_callback_pkce(integration):
    """
    Test if OAuthModule correctly handles the authorization callback with PKCE
    """
    module = get_oauth_module(integration)
    module.settings.pkce = True

    request = HandleAuthorizationCallbackRequest(
        request=HandleAuthorizationCallback(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri_with_code="https://example.com/callback?code=test_code",
            code_verifier="test_code_verifier",
        )
    )

    mock_response = Response(
        200,
        json={
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",
        },
        request=Request("POST", "https://example.com/token"),
    )

    mock_client = AsyncMock(spec=AsyncClient)
    mock_client.request.return_value = mock_response

    await module._send_authorized_request(
        "https://example.com/token", "authorization_code", mock_client, request
    )

    mock_client.request.assert_called_once()
    call_args = mock_client.request.call_args
    assert call_args.kwargs["data"] == {
        "grant_type": "authorization_code",
        "code": "test_code",
        "redirect_uri": "https://example.com/callback",
        "code_verifier": "test_code_verifier",  # must be included
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }


@pytest.mark.asyncio
async def test_get_authorization_url_pkce(integration):
    """
    Test if OAuthModule correctly handles the authorization URL with PKCE
    """
    module = get_oauth_module(integration)
    module.settings.pkce = True

    request = GetAuthorizationUrlRequest(
        request=GetAuthorizationUrl(
            client_id="test_client_id",
            redirect_uri="https://example.com/callback",
            state="test_state",
            scopes=["scope1"],
        )
    )

    response = await integration.capabilities[StandardCapabilityName.GET_AUTHORIZATION_URL](request)

    parsed_url = urlparse(response.response.authorization_url)
    query_params = parse_qs(parsed_url.query)
    assert "code_challenge" in query_params
    assert "code_challenge_method" in query_params
