# agents/crew/script_crew.py
from crewai import Task, Crew, Process
from .ollama_agent import OllamaAgent
from typing import Dict, Any
import json
from utils.logger import setup_logger
from utils.config_loader import load_agents_config, load_tasks_config
from datetime import datetime
import os

class ScriptCrew:
    def __init__(self):
        self.training_data_path = "data/training/"
        self.model_path = "models/"
        self.metrics_path = "metrics/"
        self.agents_config = load_agents_config()
        self.tasks_config = load_tasks_config()
        self.logger = setup_logger("ScriptCrew")
        self.metrics = {
            "task_times": {},
            "agent_performance": {},
            "error_counts": {}
        }

    def create_agents(self):
        """Create the specialized agents for script generation"""
        self.logger.debug("Creating agents")
        # Research Agent
        self.researcher = OllamaAgent(
            role=self.agents_config.get("researcher", {}).get("role", None),
            goal=self.agents_config.get("researcher", {}).get("goal", None),
            backstory=self.agents_config.get("researcher", {}).get("backstory", None),
            verbose=True,
            allow_delegation=False
        )

        self.parser = OllamaAgent(
            role=self.agents_config.get("parser", {}).get("role", None),
            goal=self.agents_config.get("parser", {}).get("goal", None),
            backstory=self.agents_config.get("parser", {}).get("backstory", None),
            verbose=True,
            allow_delegation=False
        )
        
        # Story Structure Agent
        self.storyteller = OllamaAgent(
            role=self.agents_config.get("storyteller", {}).get("role", None),
            goal=self.agents_config.get("storyteller", {}).get("goal", None),
            backstory=self.agents_config.get("storyteller", {}).get("backstory", None),
            verbose=True,
            allow_delegation=False
        )
        
        # Script Writer Agent
        self.writer = OllamaAgent(
            role=self.agents_config.get("writer", {}).get("role", None),
            goal=self.agents_config.get("writer", {}).get("goal", None),
            backstory=self.agents_config.get("writer", {}).get("backstory", None),
            verbose=True,
            allow_delegation=False
        )
        
        # # Engagement Optimizer Agent
        # self.optimizer = OllamaAgent(
        #     role=self.agents_config.get("optimizer", {}).get("role", None),
        #     goal=self.agents_config.get("optimizer", {}).get("goal", None),
        #     backstory=self.agents_config.get("optimizer", {}).get("backstory", None),
        #     verbose=True,
        #     allow_delegation=False
        # )

        self.logger.debug("Agents creation completed")

    async def generate_script(self, topic: str) -> Dict[str, Any]:
        """Generate a script using the crew of agents"""
        start_time = datetime.now()
        self.logger.info(f"Starting script generation for topic: {topic}")
        
        try:
            # Create the agents
            self.create_agents()
            
            # Define the tasks with performance tracking
            research_task = Task(
                agent=self.researcher,
                description=self.tasks_config.get("research", None).get("description", None).format(topic=topic),
                expected_output="Research findings about the topic",
                callback=lambda task: self._track_task_completion("research", task)
            )
            
            structure_task = Task(
                agent=self.storyteller,
                description=self.tasks_config.get("structure", None).get("description", None).format(topic=topic, context="{structure}"),
                context=self.tasks_config.get("structure", None).get("context", None),
                dependencies=[research_task],
                expected_output="Story structure and outline",
                callback=lambda task: self._track_task_completion("structure", task)
            )
            
            writing_task = Task(
                agent=self.writer,
                description=self.tasks_config.get("writing", None).get("description", None).format(topic=topic, context="{structure}"),
                context=self.tasks_config.get("writing", None).get("context", None),
                dependencies=[structure_task],
                expected_output="Final script content",
                callback=lambda task: self._track_task_completion("writing", task)
            )
            
            # Create the crew
            crew = Crew(
                agents=[self.researcher, self.storyteller, self.writer],
                tasks=[research_task, structure_task, writing_task],
                process=Process.sequential,
                verbose=True,
                sequential=True
            )
            
            self.logger.info("Starting crew execution")
            result = crew.kickoff()
            self.logger.info("Crew execution completed")
            
            # Calculate and log performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_performance_metrics(execution_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in script generation: {str(e)}", exc_info=True)
            self.metrics["error_counts"]["script_generation"] = self.metrics["error_counts"].get("script_generation", 0) + 1
            raise

    def _track_task_completion(self, task_name: str, task):
        """Track task completion and performance"""
        try:
            completion_time = datetime.now()
            if task_name not in self.metrics["task_times"]:
                self.metrics["task_times"][task_name] = []
            
            task_metrics = {
                "completion_time": completion_time.isoformat(),
                "output_length": len(str(task.output)) if task.output else 0,
                "success": True if task.output else False,
                "agent": task.agent.role if task.agent else "unknown"
            }
            
            self.metrics["task_times"][task_name].append(task_metrics)
            
            self.logger.info(
                f"Task '{task_name}' completed by {task_metrics['agent']} - "
                f"Output length: {task_metrics['output_length']} - "
                f"Success: {task_metrics['success']}"
            )
        except Exception as e:
            self.logger.error(f"Error tracking task completion for {task_name}: {str(e)}", exc_info=True)

    def _log_performance_metrics(self, total_execution_time: float):
        """Log performance metrics"""
        metrics = {
            "total_execution_time": total_execution_time,
            "task_metrics": self.metrics["task_times"],
            "error_counts": self.metrics["error_counts"]
        }
        
        # Save metrics to file
        os.makedirs(self.metrics_path, exist_ok=True)
        metrics_file = f"{self.metrics_path}/performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
        
        self.logger.info(f"Performance metrics saved to {metrics_file}")

    def _parse_result(self, result: str) -> Dict[str, Any]:
        """Parse the final result from the crew's execution"""
        try:
            # Extract the final optimized script from the result
            final_data = json.loads(result)
            self.logger.debug(f"Generated script after json load {result}")
            return final_data
        except Exception as e:
            print(f"Error parsing result: {str(e)}")
            return None