# src/query.py
"""知识查询脚本"""

import sys
from src.agent import WikiAgent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query.py <question>")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    agent = WikiAgent()
    result = agent.query(question)
    print(result)
