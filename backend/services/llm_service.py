import os
import concurrent.futures
from typing import Optional, Dict, Any
from config import settings
from utils.logger import logger

# Cap every external LLM call so a stalled network can never hang a request.
# Falls back to the template synthesizer / keyword router on timeout.
LLM_TIMEOUT_SECONDS = 12.0
_LLM_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="llm")

# Try importing google.genai or fallback safely
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class LLMService:
    """
    LLM Service Abstraction for the RUDRA Smart Campus backend.
    Supports Google Gemini API with seamless fallback when API keys are absent or invalid.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model_name = model or settings.LLM_MODEL
        self.client = None

        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized LLMService with model '{self.model_name}'")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}. Falling back to template mode.")

    def is_available(self) -> bool:
        """Return true if LLM client is initialized with valid credentials."""
        return self.client is not None and bool(self.api_key)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """
        Generate text response using LLM. Returns None if LLM is unavailable or fails.
        """
        if not self.is_available():
            return None

        try:
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"

            # Run the SDK call off the event loop thread with a hard timeout so a
            # slow/unreachable Gemini API never blocks a chat request indefinitely.
            future = _LLM_EXECUTOR.submit(
                self.client.models.generate_content,
                model=self.model_name,
                contents=full_prompt,
            )
            response = future.result(timeout=LLM_TIMEOUT_SECONDS)
            if response and hasattr(response, "text") and response.text:
                return response.text.strip()
        except concurrent.futures.TimeoutError:
            logger.error(f"LLM generation timed out after {LLM_TIMEOUT_SECONDS}s")
        except Exception as e:
            logger.error(f"LLM generation error: {e}")

        return None

    def synthesize_answer(self, query: str, agent_results: Dict[str, Any]) -> str:
        """
        Synthesizes raw structured agent results into a polished natural language answer.
        If LLM is unavailable or fails, uses a clean template formatter fallback.
        """
        if self.is_available():
            prompt = (
                f"You are RUDRA, an intelligent campus AI assistant. "
                f"The user asked: '{query}'\n\n"
                f"Data collected from internal campus database agents:\n{agent_results}\n\n"
                f"Provide a clear, accurate, friendly, and concise response to the user. "
                f"Do not invent facts not present in the agent data."
            )
            llm_reply = self.generate(prompt)
            if llm_reply:
                return llm_reply

        # Clean fallback synthesis if LLM is unavailable or fails
        answers = []
        for agent_name, res in agent_results.items():
            if isinstance(res, dict) and res.get("answer"):
                answers.append(res["answer"])
            elif hasattr(res, "answer") and res.answer:
                answers.append(res.answer)

        if answers:
            return "\n\n".join(answers)
        
        return "I received your query, but could not retrieve matching campus information."
