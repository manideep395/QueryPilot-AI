import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import Orchestrator
from evaluation.test_cases import TEST_CASES
import matplotlib.pyplot as plt

def normalize_sql(sql):
    return sql.lower().replace(" ", "").strip()

def evaluate_and_plot():
    system = Orchestrator()

    total = len(TEST_CASES)
    exact_match = 0
    execution_success = 0
    reflex_used = 0

    for nl_query, gold_sql in TEST_CASES:
        result = system.handle_query(nl_query)
        generated_sql = result["sql"]

        # Execution success
        if "result" in result:
            execution_success += 1

        # Exact match
        if normalize_sql(generated_sql) == normalize_sql(gold_sql):
            exact_match += 1

        # Reflex usage
        if result["confidence"] < 1.0:
            reflex_used += 1

    exact_match_acc = exact_match / total * 100
    execution_acc = execution_success / total * 100
    reflex_rate = reflex_used / total * 100

    print("\n=== FINAL METRICS ===")
    print(f"Exact Match Accuracy : {exact_match_acc:.2f}%")
    print(f"Execution Accuracy   : {execution_acc:.2f}%")
    print(f"Reflex Usage Rate    : {reflex_rate:.2f}%")

    # Plot graph (NO custom colors as per rules)
    labels = ["Exact Match Accuracy", "Execution Accuracy", "Reflex Usage Rate"]
    values = [exact_match_acc, execution_acc, reflex_rate]

    plt.figure()
    plt.bar(labels, values)
    plt.ylim(0, 100)
    plt.ylabel("Percentage")
    plt.title("Evaluation Metrics of Neuro-Symbolic SQL Engine")
    plt.show()

if __name__ == "__main__":
    evaluate_and_plot()