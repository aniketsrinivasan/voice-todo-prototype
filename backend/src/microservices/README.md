microservices

Components

- `llm/llm.py`: LLM wrapper using `litellm` to convert free text into a `TaskCreate` JSON.
  - Controlled by `LLM_MODEL_ID`, `temperature` (via `LLMConfig`).
  - Retries with exponential backoff; validates output with Pydantic.
  - Falls back to a heuristic (title from first line) if `litellm` is unavailable.

- `voice_model.py`: Whisper transcription using the `openai` SDK.
  - Controlled by `WHISPER_MODEL_ID`.
  - Accepts raw bytes and MIME type, returns transcription and timing metadata.

- `agent.py`: Minimal agent that can answer questions about tasks.
  - Uses `TaskRepository` to fetch tasks and synthesize an answer.
  - Designed to expand with smolagents and tools (`agent_tools/`) for DB/Web actions.

- `agent_tools/`: Tooling skeleton following smolagents' `Tool` interface.
  - `generic.py` is a template; future tools: db_search, db_insert, db_update, db_delete, web_search.

Configuration

- Requires `OPENAI_API_KEY` in the environment.
- Optional `BRAVE_API_KEY` for future web search tooling.
- `LLM_MODEL_ID` and `WHISPER_MODEL_ID` select models.

Flow overview

1) Audio `POST /add_task` → `VoiceModel.transcribe` → text
2) Text → `LLM.parse_task` → `TaskCreate`
3) Repository → persist `Task` → response
4) Questions `POST /ask` → `Agent.answer` → response (+ tasks)

