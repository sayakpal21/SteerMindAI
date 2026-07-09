import os
import chromadb

# Define where the database folder will be created on disk
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

def save_case_to_vector_db(case_id: str, telemetry_summary: str, root_cause: str, dtc: str = "HEALTHY_NOMINAL"):
    """
    Saves a verified forensic diagnostic case into a local ChromaDB vector store.
    """
    # 1. Initialize the persistent client (creates the database folder if it doesn't exist)
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # 2. Create or open the collection
    collection = client.get_or_create_collection(name="engineering_memory")
    
    # 3. Format the text data so the AI can read its full context later
    document_content = (
        f"DIAGNOSTIC TROUBLE CODE: {dtc}\n"
        f"TELEMETRY SUMMARY: {telemetry_summary}\n"
        f"VERIFIED ROOT CAUSE: {root_cause}"
    )
    
    # 4. Insert into ChromaDB (It will handle the vector math automatically)
    collection.add(
        documents=[document_content],
        metadatas=[{"dtc": dtc, "status": "verified"}],
        ids=[case_id]
    )
    print(f"📦 ChromaDB Updated Successfully at: {DB_PATH}")
    print(f"Logged Case ID: {case_id}")


# This block lets you test it by running 'python memory/seed_memory.py' directly
if __name__ == "__main__":
    print("Initializing ChromaDB seed memory check...")
    
    # Let's seed it with your dashboard's current state from the screenshot:
    save_case_to_vector_db(
        case_id="CASE_001",
        telemetry_summary=(
            "CAN-FD Channel A active at 72000 Hz. Motor Current Profile stable "
            "cycling around 5 Amps. Steering Angle Profile tracking a clean nominal sine wave. "
            "Inverter Temperature Profile showing a linear thermal rise from 42C to 45C over 3500 seconds."
        ),
        root_cause="System operations are healthy and nominal. Vehicle performance matches structural baseline criteria.",
        dtc="HEALTHY_NOMINAL"
    )