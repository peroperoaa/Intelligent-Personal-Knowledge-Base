try:
    from langchain.chains import RetrievalQA
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
    import langchain
    print(f"Langchain file: {langchain.__file__}")
    try:
        import langchain.chains
        print(f"Langchain chains file: {langchain.chains.__file__}")
    except ImportError as e2:
        print(f"Could not import langchain.chains: {e2}")
