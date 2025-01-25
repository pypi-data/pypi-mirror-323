import base64
import hashlib
import logging
import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from httpx import BasicAuth

from connector.auth_helper import parse_auth_code_and_redirect_uri
from connector.generated import (
    AuthorizationUrl,
    ErrorCode,
    GetAuthorizationUrlRequest,
    GetAuthorizationUrlResponse,
    HandleAuthorizationCallbackRequest,
    HandleAuthorizationCallbackResponse,
    HandleClientCredentialsRequest,
    HandleClientCredentialsResponse,
    OauthCredentials,
    RefreshAccessTokenRequest,
    RefreshAccessTokenResponse,
    StandardCapabilityName,
)
from connector.httpx_rewrite import AsyncClient
from connector.oai.capability import AuthRequest
from connector.oai.errors import ConnectorError
from connector.oai.modules.base_module import BaseIntegrationModule
from connector.oai.modules.oauth_module_types import (
    ClientAuthenticationMethod,
    OAuthFlowType,
    OAuthRequest,
    RequestDataType,
    RequestMethod,
)

if TYPE_CHECKING:
    from connector.oai.integration import Integration

LOGGER = logging.getLogger("integration-connectors.sdk")


class OAuthModule(BaseIntegrationModule):
    """
    OAuth module is responsible for handling the OAuth2.0 authorization flow.
    It registers the following capabilities:
    - GET_AUTHORIZATION_URL
    - HANDLE_AUTHORIZATION_CALLBACK
    - REFRESH_ACCESS_TOKEN
    """

    def __init__(self):
        super().__init__()

    def register(self, integration: "Integration"):
        if integration.oauth_settings is None:
            LOGGER.warning(
                f"OAuth settings were not provided for connector ({integration.app_id}), skipping OAuth capabilities!"
            )
            return

        self.integration = integration
        self.settings = integration.oauth_settings

        # Default available capabilities for CODE FLOW
        if self.settings.flow_type == OAuthFlowType.CODE_FLOW:
            capability_methods = {
                StandardCapabilityName.GET_AUTHORIZATION_URL: self.register_get_authorization_url,
                StandardCapabilityName.HANDLE_AUTHORIZATION_CALLBACK: self.register_handle_authorization_callback,
                StandardCapabilityName.REFRESH_ACCESS_TOKEN: self.register_refresh_access_token,
            }

        # Default available capabilities for CLIENT CREDENTIALS FLOW
        if self.settings.flow_type == OAuthFlowType.CLIENT_CREDENTIALS:
            capability_methods = {
                StandardCapabilityName.HANDLE_CLIENT_CREDENTIALS_REQUEST: self.register_handle_client_credentials_request,
                StandardCapabilityName.REFRESH_ACCESS_TOKEN: self.register_refresh_access_token,
            }

        # Register enabled capabilities
        for capability, register_method in capability_methods.items():
            if getattr(self.settings.capabilities, capability.value):
                register_method()
                self.add_capability(capability.value)

    def _get_url(self, url: str | Callable[[AuthRequest], str] | None, args: AuthRequest) -> str:
        if url is None:
            raise ConnectorError(
                message="Required URL was not provided for the OAuth flow.",
                error_code=ErrorCode.BAD_REQUEST,
            )
        if callable(url):
            return url(args)
        elif isinstance(url, str):
            return url

    def _get_scopes(self) -> str:
        """
        Get the scopes for the OAuth2.0 authorization flow from connector settings, formatted as a space delimited string.
        """
        # May contain more than one value in the string for each scope
        string_scope_values = [
            value for value in self.settings.scopes.values() if value is not None
        ]
        # parse out multiple scopes
        scope_lists = [value.split(" ") for value in string_scope_values]
        # flatten and deduplicate
        scope_values = list(set(scope for sublist in scope_lists for scope in sublist))
        return " ".join(scope_values)

    def _generate_code_challenge(self) -> tuple[str, str]:
        """
        Generate a code verifier and code challenge when using PKCE (Proof Key for Code Exchange).
        """
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("utf-8")
        code_challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())
            .rstrip(b"=")
            .decode("utf-8")
        )
        return code_verifier, code_challenge

    async def _send_authorized_request(
        self,
        url: str,
        grant_type: str,
        client: AsyncClient,
        args: HandleAuthorizationCallbackRequest
        | RefreshAccessTokenRequest
        | HandleClientCredentialsRequest,
    ) -> tuple[OauthCredentials, dict[str, Any]]:
        """
        Construct an authorized request to the token URL based on the grant type and request types.
        """

        if grant_type == "authorization_code" and isinstance(
            args, HandleAuthorizationCallbackRequest
        ):
            # Handle authorization code request
            authorization_code, original_redirect_uri = parse_auth_code_and_redirect_uri(args)
            data = {
                "grant_type": grant_type,
                "code": authorization_code,
                "redirect_uri": original_redirect_uri,
            }

            # PKCE follow-up
            if args.request.code_verifier:
                data["code_verifier"] = args.request.code_verifier

        elif grant_type == "client_credentials" and isinstance(
            args, HandleClientCredentialsRequest
        ):
            # Handle client credentials request
            data = {
                "grant_type": grant_type,
            }

            # Some Client Credentials grant providers require the scope to be sent in the body/query
            scope = " ".join(args.request.scopes) if args.request.scopes else self._get_scopes()
            if scope:
                data["scope"] = scope

        elif grant_type == "refresh_token" and isinstance(args, RefreshAccessTokenRequest):
            # Handle refresh token request
            data = {
                "grant_type": grant_type,
                "refresh_token": args.request.refresh_token,
            }
        else:
            # Unsupported grant type
            raise ValueError(f"Unsupported grant_type: {grant_type}")

        # Some OAuth providers require client ID and secret to be sent in a Authorization header
        if self.settings.client_auth == ClientAuthenticationMethod.CLIENT_SECRET_BASIC:
            auth = BasicAuth(username=args.request.client_id, password=args.request.client_secret)
        else:
            # Others expect it in the body/query
            data.update(
                {
                    "client_id": args.request.client_id,
                    "client_secret": args.request.client_secret,
                }
            )
            auth = None

        # Default to POST and BODY if not specified in connector settings
        oauth_request_type = self.settings.request_type or OAuthRequest(
            method=RequestMethod.POST, data=RequestDataType.FORMDATA
        )
        request_method, request_data_type = oauth_request_type.method, oauth_request_type.data

        # Distribute data between query params and form-body/json
        if request_data_type == RequestDataType.QUERY:
            params = data
            body = None
            json = None
        elif request_data_type == RequestDataType.JSON:
            params = None
            body = None
            json = data
        else:
            params = None
            body = data
            json = None

        # Send the request
        response = await client.request(
            method=request_method,
            url=url,
            params=params,
            json=json,
            data=body,
            auth=auth,
        )

        # Raise for status
        if response.status_code >= 300:
            try:
                error_data = response.json()
                response_message = str(error_data)
            except ValueError:
                response_message = response.text
            response_code = response.status_code

            raise ConnectorError(
                message=f"[{response_code}][{url.split('?')[0]}] OAuth request failed: {response_message}",
                error_code=ErrorCode.API_ERROR,
            )

        # Convert token_type to lowercase if not specified
        response_json = response.json()
        response_json["token_type"] = (
            response_json["token_type"].lower() if "token_type" in response_json else "bearer"
        )

        oauth_credentials = OauthCredentials.from_dict(response_json)
        if oauth_credentials is None:
            raise ConnectorError(
                message="Unable to convert raw json to OauthCredentials",
                error_code=ErrorCode.BAD_REQUEST,
            )

        return oauth_credentials, response_json

    def register_get_authorization_url(self):
        @self.integration.register_capability(StandardCapabilityName.GET_AUTHORIZATION_URL)
        async def get_authorization_url(
            args: GetAuthorizationUrlRequest,
        ) -> GetAuthorizationUrlResponse:
            url = self._get_url(self.settings.authorization_url, args)
            client_id = args.request.client_id
            redirect_uri = args.request.redirect_uri
            scope = " ".join(args.request.scopes) if args.request.scopes else self._get_scopes()
            state = args.request.state

            authorization_url = (
                f"{url}?"
                f"client_id={client_id}&"
                f"response_type=code&"
                f"scope={scope}&"
                f"redirect_uri={redirect_uri}&"
                f"state={state}"
            )

            if self.settings.pkce:
                code_verifier, code_challenge = self._generate_code_challenge()
                authorization_url += f"&code_challenge={code_challenge}"
                authorization_url += "&code_challenge_method=S256"
            else:
                code_verifier = None

            return GetAuthorizationUrlResponse(
                response=AuthorizationUrl(
                    authorization_url=authorization_url,
                    code_verifier=code_verifier,
                )
            )

        return get_authorization_url

    def register_handle_client_credentials_request(self):
        @self.integration.register_capability(
            StandardCapabilityName.HANDLE_CLIENT_CREDENTIALS_REQUEST
        )
        async def handle_client_credentials_request(
            args: HandleClientCredentialsRequest,
        ) -> HandleClientCredentialsResponse:
            async with AsyncClient() as client:
                url = self._get_url(self.settings.token_url, args)
                oauth_credentials, response_json = await self._send_authorized_request(
                    url, "client_credentials", client, args
                )

                return HandleClientCredentialsResponse(
                    response=oauth_credentials,
                    raw_data=response_json if args.include_raw_data else None,
                )

        return handle_client_credentials_request

    def register_handle_authorization_callback(self):
        @self.integration.register_capability(StandardCapabilityName.HANDLE_AUTHORIZATION_CALLBACK)
        async def handle_authorization_callback(
            args: HandleAuthorizationCallbackRequest,
        ) -> HandleAuthorizationCallbackResponse:
            async with AsyncClient() as client:
                url = self._get_url(self.settings.token_url, args)
                oauth_credentials, response_json = await self._send_authorized_request(
                    url, "authorization_code", client, args
                )

                return HandleAuthorizationCallbackResponse(
                    response=oauth_credentials,
                    raw_data=response_json if args.include_raw_data else None,
                )

        return handle_authorization_callback

    def register_refresh_access_token(self):
        @self.integration.register_capability(StandardCapabilityName.REFRESH_ACCESS_TOKEN)
        async def refresh_access_token(
            args: RefreshAccessTokenRequest,
        ) -> RefreshAccessTokenResponse:
            async with AsyncClient() as client:
                url = self._get_url(self.settings.token_url, args)
                oauth_credentials, response_json = await self._send_authorized_request(
                    url, "refresh_token", client, args
                )

                return RefreshAccessTokenResponse(
                    response=oauth_credentials,
                    raw_data=response_json if args.include_raw_data else None,
                )

        return refresh_access_token
