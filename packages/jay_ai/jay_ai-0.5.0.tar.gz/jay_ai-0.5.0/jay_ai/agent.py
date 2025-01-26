import os
import logging
import json
import requests
import inspect
import sentry_sdk
from pydantic import BaseModel
from logging import Logger
from typing import Awaitable, Callable, List, Any, Union
from dataclasses import field
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from jay_ai.token import generate_token
from jay_ai.cli_types import (
    LLMResponse,
    OnAgentStartedSpeakingInput,
    OnAgentStoppedSpeakingInput,
    OnUserStartedSpeakingInput,
    OnUserStoppedSpeakingInput,
    OnAgentMessageAddedInput,
    OnAgentInterruptedInput,
    OnFunctionCallsCollectedInput,
    OnFunctionCallsExecutedInput,
    OnUserMessageAddedInput,
    LLMResponseHandlerPayload,
    OnAgentMessageAddedPayload,
    OnAgentInterruptedPayload,
    OnAgentStartedSpeakingPayload,
    OnAgentStoppedSpeakingPayload,
    OnFunctionCallsCollectedPayload,
    OnFunctionCallsExecutedPayload,
    OnUserMessageAddedPayload,
    OnUserStartedSpeakingPayload,
    OnUserStoppedSpeakingPayload,
    OnAgentStartedSpeakingPayload,
    ConfigureSessionPayload,
    OnAgentMessageAddedInput,
    OnAgentInterruptedInput,
    OnFunctionCallsCollectedInput,
    OnFunctionCallsExecutedInput,
    OnUserMessageAddedInput,
    LLMResponseHandlerInput,
)
from jay_ai.cli_types import (
    SessionConfig,
    ConfigureSessionInput,
)
from jay_ai.utils import fetch_site_url, fetch_headers

logger = logging.getLogger(__name__)


async def _default_on_user_started_speaking(input: OnUserStartedSpeakingInput) -> None:
    pass


async def _default_on_user_stopped_speaking(input: OnUserStoppedSpeakingInput) -> None:
    pass


async def _default_on_agent_started_speaking(
    input: OnAgentStartedSpeakingInput,
) -> None:
    pass


async def _default_on_agent_stopped_speaking(
    input: OnAgentStoppedSpeakingInput,
) -> None:
    pass


async def _default_on_user_message_added(input: OnUserMessageAddedInput) -> None:
    pass


async def _default_on_agent_message_added(
    input: OnAgentMessageAddedInput,
) -> None:
    pass


async def _default_on_agent_interrupted(
    input: OnAgentInterruptedInput,
) -> None:
    pass


async def _default_on_function_calls_collected(
    input: OnFunctionCallsCollectedInput,
) -> None:
    pass


async def _default_on_function_calls_executed(
    input: OnFunctionCallsExecutedInput,
) -> None:
    pass


class Agent(BaseModel):
    id: str
    configure_session: Callable[[ConfigureSessionInput], Awaitable[SessionConfig]]
    llm_response_handler: Callable[[LLMResponseHandlerInput], Awaitable[LLMResponse]]
    tools: List[Callable[..., Awaitable[Any]]] = field(default_factory=list)
    on_user_started_speaking: Callable[
        [OnUserStartedSpeakingInput], Awaitable[None]
    ] = field(default=_default_on_user_started_speaking)
    on_user_stopped_speaking: Callable[
        [OnUserStoppedSpeakingInput], Awaitable[None]
    ] = field(default=_default_on_user_stopped_speaking)
    on_agent_started_speaking: Callable[
        [OnAgentStartedSpeakingInput], Awaitable[None]
    ] = field(default=_default_on_agent_started_speaking)
    on_agent_stopped_speaking: Callable[
        [OnAgentStoppedSpeakingInput], Awaitable[None]
    ] = field(default=_default_on_agent_stopped_speaking)
    on_user_message_added: Callable[[OnUserMessageAddedInput], Awaitable[None]] = field(
        default=_default_on_user_message_added
    )
    on_agent_message_added: Callable[[OnAgentMessageAddedInput], Awaitable[None]] = (
        field(default=_default_on_agent_message_added)
    )
    on_agent_interrupted: Callable[[OnAgentInterruptedInput], Awaitable[None]] = field(
        default=_default_on_agent_interrupted
    )
    on_function_calls_collected: Callable[
        [OnFunctionCallsCollectedInput], Awaitable[None]
    ] = field(default=_default_on_function_calls_collected)
    on_function_calls_executed: Callable[
        [OnFunctionCallsExecutedInput], Awaitable[None]
    ] = field(default=_default_on_function_calls_executed)


class ParsedAgent(Agent):
    def __post_init__(self) -> None:
        # Throw an error if any of the functions in `tools` is a lambda function. Named functions
        # are required because we use the function names to create API endpoints.
        for tool in self.tools:
            if inspect.isfunction(tool) and tool.__name__ == "<lambda>":
                raise ValueError(
                    "Lambda functions are not allowed in `tools`. Please define a named function instead."
                )

        # Find any duplicate function names
        tool_names = [tool.__name__ for tool in self.tools]
        duplicates = {name for name in tool_names if tool_names.count(name) > 1}
        if duplicates:
            raise ValueError(f"Duplicate tool names found: {', '.join(duplicates)}")

    def create_api(
        self, report_status: bool, skip_security_check: bool, deployment_id: str
    ):
        app = FastAPI()
        api_router = self.create_api_router()

        @app.middleware("http")
        async def middleware(request: Request, call_next):
            excluded_paths = ["/", "/health"]
            if request.url.path not in excluded_paths and skip_security_check == False:
                # Validate Agent API Key
                x_api_key = request.headers.get("X-API-Key")
                if x_api_key != os.getenv("JAY_INTERNAL__AGENT_API_KEY"):
                    raise HTTPException(status_code=401, detail="Invalid API key")
                # Report status
                if report_status:
                    report_service_status(deployment_id)
            response = await call_next(request)
            return response

        # Include our router
        app.include_router(api_router)

        # We only need this because we're calling /configureSession directly from the react app, but in production we should be calling
        # into the platform api which then forwards the request to the agent.
        # When we have that setup, we can remove this
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return app

    def create_production_api(self):
        deployment_id = os.getenv("JAY_INTERNAL__DEPLOYMENT_ID")
        sentry_dsn = os.getenv("SENTRY_DSN")
        sentry_env = os.getenv("SENTRY_ENVIRONMENT")
        if sentry_dsn and sentry_env:
            logger.info("Sentry integration initialized!")
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=sentry_env,
                # Sample rate for transactions (performance).
                traces_sample_rate=1.0,
                # Sample rate for exceptions / crashes.
                sample_rate=1.0,
                max_request_body_size="always",
                integrations=[
                    AsyncioIntegration(),
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
                ],
            )
        else:
            logger.warning(
                "Sentry integration disabled due to missing Sentry configuration. Error logging with Sentry is highly recommended: https://docs.jay.so/error-monitoring"
            )

        return self.create_api(
            report_status=True, skip_security_check=False, deployment_id=deployment_id
        )

    def create_api_router(self):
        router = APIRouter()
        agent = self

        @router.get("/")
        def root():
            return {"message": "Service running"}

        @router.head("/")
        def root_head():
            return {"message": "Service running"}

        @router.get("/health")
        def health():
            return {"status": "healthy"}

        @router.post("/configureSession")
        async def configure_session_handler(payload: ConfigureSessionPayload):
            try:
                input_data = ConfigureSessionInput({"custom_data": payload.custom_data})
                session_config = await agent.configure_session(input_data)
                token = await generate_token(
                    session_config=session_config, agent_api_url=payload.agent_api_url
                )
                return {"token": token}
            except Exception as e:
                logger.exception("Error in /configureSession endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

        @router.post("/agentResponse")
        async def llm_response_handler_endpoint(payload: LLMResponseHandlerPayload):
            try:
                input_data = LLMResponseHandlerInput(
                    {"session_data": payload.session_data, "messages": payload.messages}
                )

                response_stream = await agent.llm_response_handler(input_data)

                async def response_generator():
                    async for chunk in response_stream:
                        yield json.dumps(jsonable_encoder(chunk)).encode(
                            "utf-8"
                        ) + b"\n"

                return StreamingResponse(
                    response_generator(), media_type="application/json"
                )
            except Exception as e:
                logger.exception("Error in /agentResponse endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

        @router.post("/userStartedSpeaking")
        async def user_started_speaking_endpoint(payload: OnUserStartedSpeakingPayload):
            input_data = OnUserStartedSpeakingInput(
                {"session_data": payload.session_data}
            )
            try:
                await agent.on_user_started_speaking(input_data)
            except Exception as e:
                logger.exception("Error in /userStartedSpeaking endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/userStoppedSpeaking")
        async def user_stopped_speaking_endpoint(payload: OnUserStoppedSpeakingPayload):
            input_data = OnUserStoppedSpeakingInput(
                {"session_data": payload.session_data}
            )
            try:
                await agent.on_user_stopped_speaking(input_data)
            except Exception as e:
                logger.exception("Error in /userStoppedSpeaking endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/agentStartedSpeaking")
        async def agent_started_speaking_endpoint(
            payload: OnAgentStartedSpeakingPayload,
        ):
            input_data = OnAgentStartedSpeakingInput(
                {"session_data": payload.session_data}
            )
            try:
                await agent.on_agent_started_speaking(input_data)
            except Exception as e:
                logger.exception("Error in /agentStartedSpeaking endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/agentStoppedSpeaking")
        async def agent_stopped_speaking_endpoint(
            payload: OnAgentStoppedSpeakingPayload,
        ):
            input_data = OnAgentStoppedSpeakingInput(
                {"session_data": payload.session_data}
            )
            try:
                await agent.on_agent_stopped_speaking(input_data)
            except Exception as e:
                logger.exception("Error in /agentStoppedSpeaking endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/userMessageAdded")
        async def user_message_added_endpoint(payload: OnUserMessageAddedPayload):
            try:
                input_data = OnUserMessageAddedInput(
                    {
                        "session_data": payload.session_data,
                        "message": payload.message,
                    }
                )

                await agent.on_user_message_added(input_data)
            except Exception as e:
                logger.exception("Error in /userMessageAdded endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/agentMessageAdded")
        async def agent_message_added_endpoint(
            payload: OnAgentMessageAddedPayload,
        ):
            try:
                input_data = OnAgentMessageAddedInput(
                    {
                        "session_data": payload.session_data,
                        "message": payload.message,
                    }
                )

                await agent.on_agent_message_added(input_data)
            except Exception as e:
                logger.exception("Error in /agentMessageAdded endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/agentInterrupted")
        async def agent_interrupted_endpoint(
            payload: OnAgentInterruptedPayload,
        ):
            try:
                input_data = OnAgentInterruptedInput(
                    {
                        "session_data": payload.session_data,
                        "message": payload.message,
                    }
                )

                await agent.on_agent_interrupted(input_data)
            except Exception as e:
                logger.exception("Error in /agentInterrupted endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/functionCallsCollected")
        async def function_calls_collected_endpoint(
            payload: OnFunctionCallsCollectedPayload,
        ):
            try:
                input_data = OnFunctionCallsCollectedInput(
                    {
                        "session_data": payload.session_data,
                        "function_calls": payload.function_calls,
                    }
                )

                await agent.on_function_calls_collected(input_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        @router.post("/functionCallsExecuted")
        async def function_calls_executed_endpoint(
            payload: OnFunctionCallsExecutedPayload,
        ):
            try:
                input_data = OnFunctionCallsExecutedInput(
                    {"session_data": payload.session_data, "results": payload.results}
                )

                await agent.on_function_calls_executed(input_data)
            except Exception as e:
                logger.exception("Error in /agentInterrupted endpoint")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            return {"status": "ok"}

        def create_tool_endpoint(tool_func):
            async def _endpoint(payload: dict):
                try:
                    result = await tool_func(**payload)
                    return {"result": result}
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User logic error: {str(e)}",
                    )

            return _endpoint

        for tool_func in self.tools:
            func_name = tool_func.__name__
            endpoint_path = f"/tool/{func_name}"
            router.add_api_route(
                endpoint_path,
                create_tool_endpoint(tool_func),
                methods=["POST"],
                name=func_name,
            )

        return router


def fetch_report_status_payload(deployment_id: str):
    headers = fetch_headers(os.getenv("JAY_INTERNAL__AGENT_API_KEY"))
    url = f"{fetch_site_url()}/api/serviceStatus/report"
    payload = {
        "deployment_id": deployment_id,
    }

    return url, payload, headers


# Calls an API endpoint to report status of the service.
# This is used to implement smooth upgrade logic by decommissioning the agent api only after it has not received
# any requests after some time.
def report_service_status(deployment_id: str):
    url, payload, headers = fetch_report_status_payload(deployment_id)

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response data: {response.json()}")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        logger.error(f"Response: {response.text}")
    except Exception as err:
        logger.exception(f"An unexpected error occurred: {err}")
