# agents/crew/ollama_agent.py
from crewai import Agent
import requests
import json
from dotenv import load_dotenv
from .ollama_llm import OllamaLLM
from utils.logger import setup_logger
from datetime import datetime
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import Field
from typing import Dict
load_dotenv()
logger = setup_logger("Ollama Agents")

class OllamaAgent(Agent):

    performance_metrics: Dict = Field(default={})

    def __init__(self, *args, **kwargs):
        load_dotenv()
        ollama_llm = OllamaLLM()
        performance_metrics = {
            "api_calls": 0,
            "total_tokens": 0,
            "errors": 0,
            "response_times": []
        }

        # Set a dummy OpenAI API key to satisfy CrewAI's requirements
        kwargs['openai_api_key'] = "dummy-key"
        # Set a dummy model to prevent OpenAI API calls
        kwargs['llm'] = ollama_llm
        kwargs.setdefault('performance_metrics', performance_metrics)
            
        super().__init__(*args, **kwargs)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_ollama(self, prompt: str) -> str:
        """Make a call to Ollama API with retry logic"""
        start_time = time.time()
        self.performance_metrics["api_calls"] += 1
        logger.debug(f"Ollama API call triggered with promt {prompt}")
        try:
            response = requests.post(
                f"{self.llm.openai_api_base}/api/generate",
                json={
                    "model": self.llm.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30000  # Add timeout
            )
            response.raise_for_status()
            result = response.json()["response"]
            
            # Track performance metrics
            response_time = time.time() - start_time
            self.performance_metrics["response_times"].append(response_time)
            self.performance_metrics["total_tokens"] += len(result.split())
            logger.debug(f"Ollama API call completed in {response_time:.2f}s")
            logger.debug(f"Ollama API call completed and output is {result}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Ollama API call timed out")
            self.performance_metrics["errors"] += 1
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            self.performance_metrics["errors"] += 1
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Ollama call: {str(e)}")
            self.performance_metrics["errors"] += 1
            raise
            
    def execute_task(self, task: str, context=None, tools=None) -> str:
        """Override the execute_task method to use Ollama with performance tracking"""
        start_time = time.time()
        
        # Create a prompt that includes the agent's role and the task
        task_description = task

        # If there are tools, append them to the task description
        if tools:
            tools_description = "\n\nAvailable tools:\n" + "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
            task_description = f"{task_description}{tools_description}"

        prompt = f"""
        Role: {self.role}
        Goal: {self.goal}
        Backstory: {self.backstory}
        {f"Input data : {context}" if context else ""}
        Task: {task_description}
        
        Please provide your response in a clear and structured format.
        """
        
        try:
            # Call Ollama and get the response
            response = self._call_ollama(prompt)
            execution_time = time.time() - start_time
            logger.info(f"{self.role} executed the task in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}", exc_info=True)
            raise

    def get_performance_metrics(self):
        """Get the agent's performance metrics"""
        if not self.performance_metrics["response_times"]:
            return self.performance_metrics
            
        avg_response_time = sum(self.performance_metrics["response_times"]) / len(self.performance_metrics["response_times"])
        return {
            **self.performance_metrics,
            "average_response_time": avg_response_time,
            "success_rate": 1 - (self.performance_metrics["errors"] / self.performance_metrics["api_calls"]) if self.performance_metrics["api_calls"] > 0 else 0
        }