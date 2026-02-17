import sys
from core.orchestrator import Orchestrator

def main():
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "database.db"   # default

    system = Orchestrator(db_path)

    print("=== Reflex-Driven Neuro-Symbolic SQL Engine ===")

    while True:
        user_input = input("\nAsk your question (or type 'exit'): ")
        if user_input.lower() == "exit":
            break

        result = system.handle_query(user_input)
        print("\nFinal Answer:")
        print(result)

if __name__ == "__main__":
    main()