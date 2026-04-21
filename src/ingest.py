# src/ingest.py
"""知识摄入脚本"""

import sys
from src.agent import WikiAgent

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    agent = WikiAgent()
    result = agent.ingest_source(file_path)
    print(result)
