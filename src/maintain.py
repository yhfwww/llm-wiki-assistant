# src/maintain.py
"""知识维护脚本"""

from src.agent import WikiAgent

if __name__ == "__main__":
    agent = WikiAgent()
    result = agent.maintain()
    print(result)
