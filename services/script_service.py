# services/script_service.py

from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
from agents.crew.script_crew import ScriptCrew
from utils.logger import setup_logger

class ScriptGenerationService:
    def __init__(self):
        self.script_crew = ScriptCrew()
        self.logger = setup_logger("ScriptService")
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_generation_time": 0,
            "total_generation_time": 0
        }
        
    async def generate_script(self, topic: str) -> Dict[str, Any]:
        """Generate a script using the crew of agents"""
        start_time = datetime.now()
        self.performance_metrics["total_requests"] += 1
        
        try:
            # Validate inputs
            if not topic or not isinstance(topic, str):
                raise ValueError("Topic must be a non-empty string")
                
            self.logger.info(f"Starting script generation for topic: {topic}")
            
            # Generate the script
            script = await self.script_crew.generate_script(topic)
            
            # Validate script output
            # if not self._validate_script(script):
            #     raise ValueError("Generated script is invalid or incomplete")
            
            # Save the training data
            self._save_training_data(topic, script)
            
            # Update performance metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            self.performance_metrics["total_generation_time"] += generation_time
            self.performance_metrics["successful_requests"] += 1
            self.performance_metrics["average_generation_time"] = (
                self.performance_metrics["total_generation_time"] / 
                self.performance_metrics["successful_requests"]
            )
            
            self.logger.info(f"Script generated successfully in {generation_time:.2f} seconds")
            return script
            
        except Exception as e:
            self.performance_metrics["failed_requests"] += 1
            self.logger.error(f"Error generating script: {str(e)}", exc_info=True)
            raise
        
    def _validate_script(self, script: Dict[str, Any]) -> bool:
        """Validate the generated script structure"""
        try:
            required_keys = ["sections", "metadata"]
            if not all(key in script for key in required_keys):
                return False
                
            if not isinstance(script["sections"], list) or not script["sections"]:
                return False
                
            for section in script["sections"]:
                if not all(key in section for key in ["title", "content"]):
                    return False
                    
            return True
        except Exception as e:
            self.logger.error(f"Error validating script: {str(e)}")
            return False
        
    def _save_training_data(self, topic: str, script: Dict[str, Any]):
        """Save the generated script as training data"""
        try:
            os.makedirs("data/training", exist_ok=True)
            input_timestamp = datetime.now().isoformat()
            data = {
                "input": {
                    "topic": topic,
                    "timestamp": input_timestamp
                },
                "output": script,
                "metrics": {
                    "generation_time": (datetime.now() - datetime.fromisoformat(input_timestamp)).total_seconds(),
                    # "script_length": sum(len(section["content"]) for section in script["sections"]),
                    # "section_count": len(script["sections"])
                }
            }
            
            filename = f"data/training/script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Training data saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving training data: {str(e)}", exc_info=True)
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get the service's performance metrics"""
        return {
            **self.performance_metrics,
            "success_rate": (
                self.performance_metrics["successful_requests"] / 
                self.performance_metrics["total_requests"]
                if self.performance_metrics["total_requests"] > 0 else 0
            )
        }