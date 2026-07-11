import os
import chromadb
import distance


# Define DB path inside "memory/chroma_db"
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = 'engineering_memory'
# Persistent client for disk storage
client = chromadb.PersistentClient(path=DB_PATH)

def get_chroma_collection():
    """Helper to initialize the client and grab the target collection."""
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)

def save_case_to_vector_db(case_id: str, telemetry_summary: str, root_cause: str, dtc: str = "HEALTHY_NOMINAL"):
    """
    Saves a verified forensic diagnostic case into a local ChromaDB vector store.
    """
    collection = get_chroma_collection()
    
    # Format the text data so the AI can read its full context later
    document_content = (
        f"DIAGNOSTIC TROUBLE CODE: {dtc}\n"
        f"TELEMETRY SUMMARY: {telemetry_summary}\n"
        f"VERIFIED ROOT CAUSE: {root_cause}"
    )
    
    # Insert into ChromaDB
    collection.add(
        documents=[document_content],
        metadatas=[{"dtc": dtc, "status": "verified"}],
        ids=[case_id]
    )
    print(f"📦 ChromaDB Updated Successfully at: {DB_PATH}")
    print(f"Logged Case ID: {case_id}")

    
def clear_vector_db():
    """
    Deletes all records inside the engineering_memory collection.
    Linked directly to the 'Clear Memory' UI button.
    """
    try:
        # Initialize persistent client
        client = chromadb.PersistentClient(path=DB_PATH)

        # Delete the collection completely
        client.delete_collection(COLLECTION_NAME)

        # Recreate an empty collection immediately
        client.get_or_create_collection(COLLECTION_NAME)

        print("🗑️ ChromaDB wiped cleanly! All vector datasets purged.")
        return True
    except Exception as e:
        print(f"❌ Failed to clear vector store: {e}")
        return False
    
    
# --- 2. NEW FUNCTION: RETRIEVE ALL DATA BUTTON INTERFACE ---
def retrieve_top_matches(collection_name: str, query_dict: dict, threshold: float = 0.0):
    """
    Retrieve closest matches from ChromaDB using only 'root_cause' and 'action',
    and return % match (similarity score).

    Args:
        collection_name: Name of the collection to query
        query_dict: Dictionary containing key-value pairs
        threshold: Minimum similarity score (0.0–1.0) to accept a match

    Returns:
        dict: Dictionary with keys 'root_cause' and 'action', each holding top match info
              including %match
    """
    collection = get_chroma_collection()

    results_dict = {}

    #for key in ["signal", "recommendation"]:
    #for key in ["signal", "root_cause"]:
    for key in ["root_cause"]:
        query_text = query_dict.get(key)
        if not query_text:
            results_dict[key] = {"id": None, "document": None, "metadata": None, "%match": None}
            continue

        results = collection.query(
            query_texts=[query_text],
            n_results=1
        )

        if results["ids"] and results["documents"]:
            # ChromaDB returns distances; convert to similarity
            distance = results["distances"][0][0]

            # Convert distance to similarity
            if distance <= 1:
                # cosine distance
                similarity = 1 - distance
            else:
                # large distance penalty
                similarity = 1 / (1 + distance)

            print('distance: ',distance)
            similarity = max(0, min(1, similarity))

            percent_match = round(similarity * 100, 2)

            if similarity >= threshold:
                results_dict[key] = {
                    "id": results["ids"][0][0],
                    "document": results["documents"][0][0],
                    "metadata": results["metadatas"][0][0],
                    "%match": percent_match
                }
            else:
                results_dict[key] = {"id": None, "document": None, "metadata": None, "%match": percent_match}
        else:
            results_dict[key] = {"id": None, "document": None, "metadata": None, "%match": None}

    return results_dict



def store_dict_in_chromadb(collection_name, data_dict):
    """
    Store each key-value pair from a dictionary into ChromaDB.
    
    Args:
        collection: ChromaDB collection object
        data_dict: Dictionary with key-value pairs to store
    """
    collection = client.get_or_create_collection(collection_name)
    for key, value in data_dict.items():
        collection.add(
            ids=[key],  # unique ID based on dict key
            documents=[value],  # plain text content
            metadatas=[{"category": key}]  # optional metadata
        )
    print("Dictionary content stored successfully!")

def create_chromadb_collection(collection_name: str):
    """
    Create or get a ChromaDB collection stored inside the 'memory/chroma_db' folder.

    Args:
        collection_name (str): The name of the collection to create or retrieve.
    Returns:
        collection: The ChromaDB collection object
    """
    # Initialize persistent ChromaDB client
    client = chromadb.PersistentClient(path=DB_PATH)

    # Create or get the collection
    collection = client.get_or_create_collection(collection_name)

    print(f"Collection '{collection_name}' created or retrieved at {DB_PATH}")
    return collection

# =====================================================================
# COMPLETE LOCAL INTERACTIVE TESTING SCAFFOLD
# =====================================================================
if __name__ == "_main_":
    print("\n⚡ [DATABASE RECOVERY INTERFACE] Executing targeted system reset...")
    
    # Trigger ONLY the structural wipe routine
    clear_vector_db()
    
    print("✨ Execution context closed.\n")