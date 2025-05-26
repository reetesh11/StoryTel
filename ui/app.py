import streamlit as st
import sys
import os
import asyncio
from typing import List
import uuid
from datetime import datetime

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents import (
    ScriptWriterAgent,
)
from config.schema import VideoConfig, VideoSection
from utils.logger import setup_logger

# Initialize session state for process tracking
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'video_path' not in st.session_state:
    st.session_state.video_path = None

# Set up logger
logger = setup_logger("app")

st.set_page_config(
    page_title="AI Video Creator",
    page_icon="🎥",
    layout="wide"
)

async def create_script(config: VideoConfig):
    """Create video using the configured agents"""
    logger.info(f"Starting video creation process for topic: {config.topic}")
    
    try:
        # Initialize agents
        logger.debug("create_script: Initializing video creation agents")

        script_writer = ScriptWriterAgent(config.dict())

        logger.info("create_script: All agents initialized successfully")

        # Step 2: Generate script
        logger.info("create_script: Step 1: Generating script")
        script = await script_writer.run({
            "topic": config.topic,
            # "category": classification["category"]
        })
        logger.debug(f"create_script: Script generation completed with {len(script['sections'])} sections")
        
        return script
    except Exception as e:
        logger.error(f"Error in video creation process: {str(e)}", exc_info=True)
        raise

def display_script_sections(sections: List[VideoSection]):
    """Display script sections in a user-friendly format"""
    if not sections:
        st.error("No script sections available. Please try again.")
        return
        
    st.subheader("Generated Script")
    
    try:
        # Create tabs for each section
        tabs = st.tabs([section.title for section in sections])
        
        for tab, section in zip(tabs, sections):
            with tab:
                # Display section content with proper formatting
                st.markdown("---")
                st.markdown(section.content)
    except Exception as e:
        st.error(f"Error displaying script sections: {str(e)}")
        logger.error(f"Error in display_script_sections: {str(e)}", exc_info=True)

def run_async(coro):
    """Run an async function in a synchronous context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def main():
    """Main application function"""
    logger.info("Starting AI Video Creator application")
    st.title("🎥 AI Video Creator")
    
    # Initialize session state for search IDs if not exists
    if 'search_id' not in st.session_state:
        st.session_state.search_id = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = {}
    
    # Sidebar for configuration
    with st.sidebar:
        logger.debug("main: Initializing sidebar configuration")
        st.header("Configuration")
        
        # Topic input
        topic = st.text_input("Enter your topic")
        if topic:
            # Generate new search ID when topic changes
            if st.session_state.search_id is None or topic != st.session_state.get('last_topic'):
                st.session_state.search_id = str(uuid.uuid4())
                st.session_state.last_topic = topic
                # Store search in history with timestamp
                st.session_state.search_history[st.session_state.search_id] = {
                    'topic': topic,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            logger.info(f"main: User entered topic: {topic} with search_id: {st.session_state.search_id}")
        
        # Display search history
        if st.session_state.search_history:
            st.markdown("---")
            st.subheader("Search History")
            for search_id, search_data in st.session_state.search_history.items():
                st.markdown(f"**Topic:** {search_data['topic']}  \n**Time:** {search_data['timestamp']}")
        
    # Main content area
    if topic and not st.session_state.is_processing:
        st.session_state.is_processing = True
        logger.info(f"Processing video creation for topic: {topic}")
        st.header(f"Creating video about: {topic}")
        
        # Create config
        config = VideoConfig(topic=topic)
        
        try:
            logger.info(f"User initiated script generation for search_id: {st.session_state.search_id}")
            
            # Create a placeholder for the status message
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            # Show initial status
            status_placeholder.info("Initializing script generation...")
            
            # Initialize agents
            try:
                script_writer = ScriptWriterAgent(config.dict())
            except RuntimeError as e:
                st.error(str(e))
                st.info("To fix this:\n1. Open a terminal\n2. Run 'ollama serve'\n3. Wait for Ollama to start\n4. Refresh this page")
                return
            
            # Update status
            status_placeholder.info("Generating script content...")
            
            # Show a spinner while processing
            with st.spinner("Generating script... This may take a few minutes."):
                script = run_async(script_writer.run({
                    "topic": config.topic,
                }))
            
            # Store script in session state with search_id
            if 'scripts' not in st.session_state:
                st.session_state.scripts = {}
            st.session_state.scripts[st.session_state.search_id] = {
                'script': script,
                'config': config
            }
            
            # Clear the status and progress placeholders
            status_placeholder.empty()
            progress_placeholder.empty()
            
            # Display the script
            display_script_sections(script["sections"])
            
            st.success("Script generated successfully!")
            
        except Exception as e:
            error_msg = f"Error generating script: {str(e)}"
            logger.error(error_msg, exc_info=True)
            st.error(error_msg)
            if "Ollama" in str(e):
                st.info("Please ensure Ollama is running and try again.")
            st.exception(e)
        finally:
            st.session_state.is_processing = False

if __name__ == "__main__":
    try:
        logger.info("Application started")
        main()
    except Exception as e:
        logger.critical(f"Critical error in application: {str(e)}", exc_info=True)
        st.error("An unexpected error occurred. Please check the logs for details.") 