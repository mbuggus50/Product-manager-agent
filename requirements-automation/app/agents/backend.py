```plaintext
validation_service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── agents/
│   │   └── validation_agent.py
│   ├── services/
│   │   ├── form_validator.py
│   │   ├── content_validator.py
│   │   ├── prompt_builder.py
│   │   ├── llm_client.py
│   │   ├── memory_saver.py
│   │   └── session_store.py
│   └── models/
│       ├── domain.py
│       └── schemas.py
├── requirements.txt
└── README.md
```

---
# app/config.py
```python
"""
Configuration module for the Validation Service.

Loads environment variables (e.g., OpenAI API key) at startup and
enforces that critical settings are provided.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the OpenAI API key is present; fail fast otherwise
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY environment variable is required for LLMClient operations"
    )
```

# app/models/domain.py
```python
"""
Domain definitions for the Validation Service.

Contains dataclasses representing the core entities (Submission,
AgentResponse, Clarification, etc.) and enums for status codes.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

@dataclass
class FieldDefinition:
    """
    Defines a single form field's metadata used in schema validation.

    Attributes:
        name: The unique key for this field.
        type: Data type (e.g., "string", "date").
        required: Whether the UI enforces presence.
        pattern: Optional regex to further validate format.
        hint: Optional help text for UI placeholders.
    """
    name: str
    type: str = "string"
    required: bool = True
    pattern: Optional[str] = None
    hint: Optional[str] = None

@dataclass
class FormValidationResult:
    """
    Result of running basic form-level validations.

    Attributes:
        is_valid: True if no missing or invalid fields.
        missing: List of required fields that were absent or blank.
        errors: Human-readable error messages.
    """
    is_valid: bool
    missing: List[FieldDefinition]
    errors: List[str]

@dataclass
class Clarification:
    """
    Represents a request to the user to clarify or expand a field's content.

    Attributes:
        field: The key for the field needing clarification.
        message: A user-facing instruction explaining what's missing.
    """
    field: str
    message: str

@dataclass
class ContentValidationResult:
    """
    Outcome of LLM-driven semantic validation.

    Attributes:
        is_valid: True if LLM found no semantic gaps.
        clarifications: Field-specific guidance returned by the LLM.
    """
    is_valid: bool
    clarifications: List[Clarification]

class ResponseStatus(str, Enum):
    """
    Enum of overall response statuses for the ValidationAgent.
    """
    OK = "OK"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    ERROR = "ERROR"

@dataclass
class Submission:
    """
    Input payload from the UI or subsequent clarification rounds.

    Attributes:
        session_id: UUID of the current conversation/session.
        fields: A mapping of field names to their input values.
    """
    session_id: Optional[UUID]
    fields: Dict[str, str]

@dataclass
class AgentResponse:
    """
    Standardized response object from ValidationAgent to the API layer.

    Attributes:
        status: ResponseStatus indicating next steps.
        clarifications: List of Clarification objects if further input needed.
        validated_data: Echo of fields if validation passed.
    """
    status: ResponseStatus
    clarifications: List[Clarification]
    validated_data: Optional[Dict[str, str]] = None

@dataclass
class SessionContext:
    """
    Persisted session state for multi-turn interactions.

    Attributes:
        session_id: Unique ID for this session.
        history: List of Submissions to maintain context.
        last_response: Most recent AgentResponse for idempotency.
    """
    session_id: UUID
    history: List[Submission] = field(default_factory=list)
    last_response: Optional[AgentResponse] = None
```

# app/models/schemas.py
```python
"""
Pydantic schemas for request/response validation at the API boundary.

Defines:
  - ClarificationModel
  - AgentResponseModel
  - ValidateRequestModel
"""
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.domain import ResponseStatus

class ClarificationModel(BaseModel):
    """Serializable version of Clarification domain class."""
    field: str
    message: str

class AgentResponseModel(BaseModel):
    """Schema for API responses from the validation endpoint."""
    session_id: UUID
    status: ResponseStatus
    clarifications: List[ClarificationModel]
    validated_data: Optional[Dict[str, str]] = None

class ValidateRequestModel(BaseModel):
    """Schema for incoming validation requests."""
    session_id: Optional[UUID] = None
    fields: Dict[str, str]
```

# app/services/form_validator.py
```python
"""
Performs basic schema-level checks on the incoming fields.
Ensures required fields are present and non-blank.
"""
from typing import List, Dict
from app.models.domain import FieldDefinition, FormValidationResult

class FormValidator:
    def __init__(self, schema: List[FieldDefinition]):
        """Initialize with a list of FieldDefinitions to enforce."""
        self.schema = schema

    def validate(self, fields: Dict[str, str]) -> FormValidationResult:
        """
        Check for missing required fields.

        Returns FormValidationResult indicating success or listing issues.
        """
        missing: List[FieldDefinition] = []
        errors: List[str] = []
        for fd in self.schema:
            value = fields.get(fd.name)
            if fd.required and (value is None or not value.strip()):
                missing.append(fd)
                errors.append(f"Field '{fd.name}' is required.")
        is_valid = len(missing) == 0
        return FormValidationResult(is_valid=is_valid, missing=missing, errors=errors)
```

# app/services/prompt_builder.py
```python
"""
Constructs a structured prompt for semantic validation.

Separates prompt templating from the LLM client to allow easy
externalization of templates or multi-model usage.
"""
from typing import Dict

class PromptBuilder:
    def __init__(self, template: str):
        """Store the template string with placeholders."""
        self.template = template

    def build(self, data: Dict[str, str]) -> str:
        """
        Interpolate user-provided data into the prompt template.

        This decouples prompt construction logic from LLM calls.
        """
        return self.template.format(**data)
```

# app/services/llm_client.py
```python
"""
Abstraction around an LLM provider (e.g., OpenAI).

Handles API key configuration and wraps chat-completion calls.
"""
import openai
from app.config import OPENAI_API_KEY

# Set the global OpenAI key once
openai.api_key = OPENAI_API_KEY

class LLMClient:
    def __init__(self, model_name: str = "gpt-4"):
        """Allow swapping models by changing this parameter."""
        self.model_name = model_name

    def send_prompt(self, prompt: str) -> str:
        """
        Send the constructed prompt to the LLM and return raw content.

        Uses a system-level instruction to focus the assistant on validation tasks,
        and sets a low temperature to improve repeatability of JSON output.
        """
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant focused on validating PRD content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
```

# app/services/content_validator.py
```python
"""
Drives semantic/content validation using the LLM.

Parses the LLM's JSON response into structured Clarification objects.
"""
import json
from typing import Dict
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import LLMClient
from app.models.domain import Clarification, ContentValidationResult

class ContentValidator:
    def __init__(self, prompt_builder: PromptBuilder, llm_client: LLMClient):
        """Inject dependencies for testability and flexibility."""
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

    def validate_content(self, data: Dict[str, str]) -> ContentValidationResult:
        """
        Build a prompt, invoke the LLM, then interpret its output.

        Expects the LLM to return a JSON array of {field, message} objects.
        Falls back to a generic error Clarification if parsing fails.
        """
        prompt = self.prompt_builder.build(data)
        raw = self.llm_client.send_prompt(prompt)
        try:
            clarifications = [Clarification(**c) for c in json.loads(raw)]
        except Exception:
            clarifications = [
                Clarification(
                    field="all",
                    message="Unable to parse LLM response as JSON. Review prompt or model output."
                )
            ]
        is_valid = len(clarifications) == 0
        return ContentValidationResult(is_valid=is_valid, clarifications=clarifications)
```

# app/services/memory_saver.py
```python
"""
Lightweight in-memory storage for persisting arbitrary session data.

Used by the ValidationAgent to checkpoint progress between turns.
"""
from typing import Any, Dict
from uuid import UUID

class MemorySaver:
    def __init__(self):
        """Initialize an empty in-process dictionary store."""
        self.store: Dict[UUID, Any] = {}

    def save(self, session_id: UUID, data: Any) -> None:
        """Overwrite or create a memory entry for this session."""
        self.store[session_id] = data

    def load(self, session_id: UUID) -> Any:
        """Retrieve persisted data, or None if not found."""
        return self.store.get(session_id)
```

# app/services/session_store.py
```python
"""
Manages SessionContext objects in-memory.

Abstracts session lifecycle: creation, retrieval, updates.
"""
from uuid import UUID, uuid4
from typing import Dict
from app.models.domain import SessionContext, Submission, AgentResponse

class SessionStore:
    def __init__(self):
        """Initialize with an empty session map."""
        self.sessions: Dict[UUID, SessionContext] = {}

    def create(self) -> SessionContext:
        """
        Generate a new session and persist its context.

        Ensures a unique UUID and empty history/last_response.
        """
        sid = uuid4()
        ctx = SessionContext(session_id=sid)
        self.sessions[sid] = ctx
        return ctx

    def get(self, session_id: UUID) -> SessionContext:
        """Retrieve an existing session context, or None if missing."""
        return self.sessions.get(session_id)

    def update(self, session_id: UUID, ctx: SessionContext) -> None:
        """Overwrite the session context for subsequent turns."""
        self.sessions[session_id] = ctx
```

# app/agents/validation_agent.py
```python
"""
Orchestrates the validation workflow:
 1. Optional session lookup or creation.
 2. Form-level checks via FormValidator.
 3. Semantic checks via ContentValidator.
 4. Returns structured AgentResponse for the API.
"""
from typing import Optional
from uuid import UUID
from app.services.form_validator import FormValidator
from app.services.content_validator import ContentValidator
from app.services.memory_saver import MemorySaver
from app.services.session_store import SessionStore
from app.models.domain import Submission, AgentResponse, ResponseStatus, FieldDefinition

class ValidationAgent:
    def __init__(
        self,
        form_validator: FormValidator,
        content_validator: ContentValidator,
        session_store: SessionStore,
        memory_saver: MemorySaver,
        schema_fields: list[FieldDefinition]
    ):
        """Inject all dependencies for easy testing and swapping implementations."""
        self.form_validator = form_validator
        self.content_validator = content_validator
        self.session_store = session_store
        self.memory_saver = memory_saver
        self.schema_fields = schema_fields

    def handle_submission(self, sub: Submission) -> AgentResponse:
        """
        Main entrypoint for each validation API call.

        Ensures session context, runs form checks, then content checks,
        and returns an AgentResponse with appropriate status and messages.
        """
        # Session management: reuse or create new
        if sub.session_id:
            ctx = self.session_store.get(sub.session_id)
            if not ctx:
                ctx = self.session_store.create()
                sub.session_id = ctx.session_id
        else:
            ctx = self.session_store.create()
            sub.session_id = ctx.session_id

        # Persist the current submission
        ctx.history.append(sub)

        # 1) Basic schema-level validation
        form_result = self.form_validator.validate(sub.fields)
        if not form_result.is_valid:
            # Build clarifications for missing fields
            clarifications = [
                FieldDefinition(
                    name=fd.name,
                    type=fd.type,
                    required=fd.required,
                    hint=fd.hint
                ) for fd in form_result.missing
            ]
            resp = AgentResponse(
                status=ResponseStatus.NEEDS_CLARIFICATION,
                clarifications=[
                    c for c in clarifications
                ],
            )
            ctx.last_response = resp
            self.session_store.update(ctx.session_id, ctx)
            return resp

        # 2) LLM-driven semantic validation
        content_result = self.content_validator.validate_content(sub.fields)
        if not content_result.is_valid:
            resp = AgentResponse(
                status=ResponseStatus.NEEDS_CLARIFICATION,
                clarifications=content_result.clarifications
            )
            ctx.last_response = resp
            self.session_store.update(ctx.session_id, ctx)
            return resp

        # Success path: everything validated
        resp = AgentResponse(
            status=ResponseStatus.OK,
            clarifications=[],
            validated_data=sub.fields
        )
        ctx.last_response = resp
        self.session_store.update(ctx.session_id, ctx)
        return resp
```

# app/main.py
```python
"""
Entrypoint for the FastAPI application exposing a /validate endpoint.

Wires up all components and handles request/response transformation.
"""
from fastapi import FastAPI
from app.models.schemas import ValidateRequestModel, AgentResponseModel, ClarificationModel
from app.models.domain import FieldDefinition, Submission
from app.services.form_validator import FormValidator
from app.services.prompt_builder import PromptBuilder
from app.services.llm_client import LLMClient
from app.services.content_validator import ContentValidator
from app.services.memory_saver import MemorySaver
from app.services.session_store import SessionStore
from app.agents.validation_agent import ValidationAgent

# Define the canonical PRD schema fields
schema_fields = [
    FieldDefinition(name="title"),
    FieldDefinition(name="business_need"),
    FieldDefinition(name="acceptance_criteria"),
    FieldDefinition(name="delivery_date"),
]

# Instantiate each service layer with dependencies
form_validator = FormValidator(schema_fields)
prompt_template = """
Validate the following product requirement details.
Return JSON list of {field, message} objects if any semantic issues:

Title: {title}
Business Need: {business_need}
Acceptance Criteria: {acceptance_criteria}
Delivery Date: {delivery_date}
"""
prompt_builder = PromptBuilder(prompt_template)
llm_client = LLMClient(model_name="gpt-4")
content_validator = ContentValidator(prompt_builder, llm_client)
session_store = SessionStore()
memory_saver = MemorySaver()
agent = ValidationAgent(
    form_validator,
    content_validator,
    session_store,
    memory_saver,
    schema_fields
)

app = FastAPI()

@app.post("/validate", response_model=AgentResponseModel)
async def validate(req: ValidateRequestModel):  # noqa: E501
    """
    Validate incoming PRD fields in two stages:
      1. Schema-level (presence/format) via FormValidator
      2. Semantic/content via ContentValidator + LLM

    Returns:
      - NEEDS_CLARIFICATION with list of fields and messages, or
      - OK with validated data echo if no issues.
    """
    sub = Submission(session_id=req.session_id, fields=req.fields)
    resp = agent.handle_submission(sub)
    # Transform domain response into API schema
    return AgentResponseModel(
        session_id=sub.session_id,
        status=resp.status,
        clarifications=[
            ClarificationModel(field=c.field, message=c.message)
            for c in resp.clarifications
        ],
        validated_data=resp.validated_data
    )
```

# requirements.txt
```text
fastapi
uvicorn
openai
python-dotenv
```

# README.md
```markdown
# Validation Service

A microservice for validating product requirement inputs in two layers:

1. **FormValidator**: Ensures required fields (title, business_need, acceptance_criteria, delivery_date) are non-empty.
2. **ContentValidator**: Uses an LLM to check semantic clarity and completeness.

## Setup

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Design Decisions

- **Two-layer validation**: UI/enforced presence vs. LLM-driven semantics keeps trivial checks off the model.
- **Low LLM temperature**: Improves consistency of JSON output parsing.
- **Dependency Injection**: Each component is initialized in `main.py` for clear separation and testability.
- **In-memory stores**: Simple for PoC; swap out for Redis or DB in production.
```
