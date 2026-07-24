import asyncio
import uuid
import sys
import os

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

from app.core.logging_config import configure_logging, get_logger
configure_logging()

from app.graph.builder import get_compiled_graph
from langgraph.checkpoint.memory import MemorySaver
from app.core.firebase import initialize_firebase
from app.schemas.state import create_initial_state

logger = get_logger(__name__)

async def run_test():
    logger.info("Initializing Firebase...")
    try:
        initialize_firebase()
    except Exception as e:
        logger.error(f"Firebase failed: {e}")
        # Proceed anyway if we don't strictly require it for the local test
        
    logger.info("Building LangGraph...")
    checkpointer = MemorySaver()
    graph = get_compiled_graph(checkpointer=checkpointer)
    
    project_id = f"test_proj_{uuid.uuid4().hex[:8]}"
    job_id = "test_job_1"
    logger.info(f"Starting test generation workflow for project {project_id}...")
    
    # Create entries in the DB first so updates succeed
    from app.database.repositories.project_repository import ProjectRepository
    from app.database.repositories.job_repository import JobRepository
    
    project_repo = ProjectRepository()
    project_repo.create({
        "id": project_id, 
        "title": "Test Project",
        "input_type": "text", 
        "input_text": "Generate exactly 1 simple scene explaining 1+1=2."
    })
    # Override id since create() generates a random one
    # Actually wait, ProjectRepository.create() ignores the 'id' parameter and generates a new UUID.
    # Let me just use the created project's ID.
    project_doc = project_repo.create({
        "title": "Test Project",
        "input_type": "text", 
        "input_text": "Generate exactly 1 simple scene explaining 1+1=2."
    })
    project_id = project_doc["id"]
    
    job_repo = JobRepository()
    job_doc = job_repo.create(project_id)
    job_id = job_doc["id"]

    initial_state = create_initial_state(
        project_id=project_id,
        job_id=job_id,
        input_type="text",
        input_text="Generate exactly 1 simple scene explaining 1+1=2. Keep it incredibly short, maximum 1 object and 1 animation.",
    )
    
    config = {"configurable": {"thread_id": project_id}}
    
    try:
        # Run the graph
        logger.info("Invoking graph...")
        # Ainvoke triggers the asynchronous LangGraph execution
        result = await graph.ainvoke(initial_state, config)
        
        logger.info("Graph execution completed.")
        logger.info(f"Final Status: {result.get('status')}")
        if result.get("error_message"):
            logger.error(f"Error Message: {result.get('error_message')}")
            sys.exit(1)
            
        logger.info(f"Final Video Path: {result.get('final_video_path')}")
        logger.info("Workflow test successful.")
        sys.exit(0)
        
    except Exception as e:
        logger.exception(f"Workflow test failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_test())
