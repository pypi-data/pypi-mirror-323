def Chatbot():
    try:
        from empire_chain.streamlit import Chatbot
        return Chatbot
    except ImportError as e:
        raise ImportError("Could not import Chatbot. Please install required dependencies: pip install openai") from e

def VisionChatbot():
    try:
        from empire_chain.streamlit import VisionChatbot
        return VisionChatbot
    except ImportError as e:
        raise ImportError("Could not import VisionChatbot. Please install required dependencies: pip install groq pillow") from e

def PDFChatbot():
    try:
        from empire_chain.streamlit import PDFChatbot
        return PDFChatbot
    except ImportError as e:
        raise ImportError("Could not import PDFChatbot. Please install required dependencies: pip install chromadb qdrant-client") from e 