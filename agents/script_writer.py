from .base_agent import BaseAgent
from typing import Dict, Any, List
from config.schema import VideoCategory, VideoSection
import requests
import json
import os
from dotenv import load_dotenv
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

class ScriptWriterAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "mistral:latest")
        self.logger = setup_logger("script_writer")
        
        # Verify Ollama connection on initialization
        self._verify_ollama_connection()

    def _verify_ollama_connection(self):
        """Verify that Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            response.raise_for_status()
            self.logger.info("Successfully connected to Ollama API")
        except requests.exceptions.ConnectionError:
            self.logger.error("Could not connect to Ollama. Please ensure Ollama is running.")
            raise RuntimeError(
                "Ollama is not running. Please start Ollama by running 'ollama serve' in your terminal."
            )
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Error connecting to Ollama API: {str(e)}")
            raise RuntimeError(
                f"Error connecting to Ollama API: {str(e)}. Please check if Ollama is running correctly."
            )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a script for the video based on the topic and category
        """
        self.logger.info(f"ScriptWriterAgent: Starting script generation for topic: {input_data.get('topic')}")
        self.logger.debug(f"ScriptWriterAgent: Input data: {input_data}")
        
        topic = input_data.get("topic", "")
        
        try:
            # Define the structure based on category
            self.logger.info("ScriptWriterAgent: Generating script")
            sections = await self._generate_script(topic)
            # total_duration = sum(section.duration for section in sections)
            # self.logger.info(f"Script generation completed. Total duration: {total_duration} seconds")
            
            return {
                "sections": sections,
                # "total_duration": total_duration
            }
        except Exception as e:
            self.logger.error(f"ScriptWriterAgent: Error in script generation: {str(e)}", exc_info=True)
            raise

    async def _get_ollama_response(self, prompt: str) -> str:
        """Get response from Ollama API"""
        try:
            self.logger.debug(f"Sending request to Ollama API at {self.ollama_base_url}")
            
            # First, verify the model is available
            try:
                response = requests.get(f"{self.ollama_base_url}/api/tags")
                response.raise_for_status()
                available_models = [model['name'] for model in response.json()['models']]
                
                if self.model_name not in available_models:
                    self.logger.warning(f"Model {self.model_name} not found. Available models: {available_models}")
                    # Fallback to phi if available, otherwise use the first available model
                    if 'phi' in available_models:
                        self.model_name = 'phi'
                    elif available_models:
                        self.model_name = available_models[0]
                    else:
                        raise RuntimeError("No models available in Ollama. Please pull a model first.")
            except Exception as e:
                self.logger.error(f"Error checking available models: {str(e)}")
                raise RuntimeError("Could not verify available models. Please check Ollama installation.")
            
            # Now make the actual request
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            self.logger.debug("Successfully received response from Ollama API")
            return response.json()["response"]
            
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to Ollama. Please ensure Ollama is running."
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error calling Ollama API: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def _generate_script(self, topic: str) -> List[VideoSection]:
        """Generate script for real incidents"""
        prompt = f"""
        Create an engaging, story-like script for a video about {topic}. Write it as if explaining to a curious 15-year-old student.

        Format the response as a JSON object with the following structure:
        {{
            "sections": [
                {{
                    "title": "Introduction",
                    "content": "Detailed content here",
                    "duration": 30,
                    "tone": "curious",
                    "key_points": ["point1", "point2"],
                    "visual_hints": ["description of visual 1", "description of visual 2"],
                    "engagement_hooks": ["question1", "fact1"],
                    "transition_to_next": "smooth transition text"
                }}
            ],
            "metadata": {{
                "target_audience": "15-year-old students",
                "learning_objectives": ["objective1", "objective2"],
                "key_terms": ["term1", "term2"],
                "estimated_engagement_score": 0.85
            }}
        }}

        Enhanced Storytelling Guidelines:

        1. Section Structure:
        - Title: Clear and engaging
        - Content: Main narrative
        - Duration: Estimated time in seconds
        - Tone: emotional tone (curious, excited, thoughtful, etc.)
        - Key Points: Main takeaways
        - Visual Hints: Suggestions for visuals
        - Engagement Hooks: Questions or facts to maintain interest
        - Transition: Smooth connection to next section

        2. Narrative Elements:
        - Hook: Start with a surprising fact or question
        - Context: Background information
        - Main Story: Core content
        - Visual Descriptions: Help create mental images
        - Interactive Elements: Questions and prompts
        - Conclusion: Summary and call to action

        3. Engagement Techniques:
        - Rhetorical Questions
        - "Did you know?" facts
        - Real-world connections
        - Personal stories
        - Analogies and metaphors
        - Visual descriptions

        4. Learning Objectives:
        - Clear understanding of the topic
        - Critical thinking prompts
        - Real-world applications
        - Connection to current events
        - Encouragement for further research

        5. Visual Planning:
        - Key moments for visuals
        - Suggested imagery
        - Text overlay points
        - Transition effects
        - Background music suggestions

        6. Pacing Guidelines:
        - Introduction: 30 seconds
        - Main sections: 2-3 minutes each
        - Conclusion: 30 seconds
        - Total duration: 5-7 minutes

        7. Language Style:
        - Conversational tone
        - Simple explanations
        - Active voice
        - Present tense
        - Short sentences
        - Clear transitions

        8. Quality Checks:
        - Is it engaging?
        - Is it educational?
        - Is it age-appropriate?
        - Is it well-structured?
        - Does it flow naturally?
        """

        try:
            response = await self._get_ollama_response(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"ScriptWriterAgent: Error generating script: {str(e)}", exc_info=True)

    def _parse_json_response(self, response: str) -> List[VideoSection]:
        """Parse JSON response into VideoSection objects"""
        try:
            self.logger.debug("ScriptWriterAgent: Parsing JSON response")
            # Extract JSON from the response
            json_str = response[response.find("{"):response.rfind("}")+1]
            data = json.loads(json_str)
            
            # Validate the response structure
            if not data or "sections" not in data:
                self.logger.error("Invalid response structure: missing 'sections'")
                # Return a default structure if parsing fails
                return [
                    VideoSection(
                        title="Introduction",
                        content="Unable to generate script. Please try again.",
                        duration=30
                    )
                ]
            
            sections = []
            for section_data in data["sections"]:
                # Validate each section
                if not isinstance(section_data, dict):
                    continue
                    
                # Ensure required fields exist
                title = section_data.get("title", "Untitled Section")
                content = section_data.get("content", "No content available")
                
                sections.append(VideoSection(
                    title=title,
                    content=content,
                    duration=section_data.get("duration", 30)
                ))
            
            # If no valid sections were created, return a default section
            if not sections:
                return [
                    VideoSection(
                        title="Introduction",
                        content="Unable to generate script. Please try again.",
                        duration=30
                    )
                ]
            
            return sections
        
        except Exception as e:
            self.logger.error(f"ScriptWriterAgent: Error parsing JSON response: {str(e)}", exc_info=True)
            # Return a default section in case of error
            return [
                VideoSection(
                    title="Error",
                    content="An error occurred while generating the script. Please try again.",
                    duration=30
                )
            ]

    # ... (keep the fallback methods as they are) 
