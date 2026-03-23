class DiagnosticReport:
    def __init__(self, data):
        self.data = data

    def display(self):
        print("\n===== AGENTIC IA REFACTORING REPORT =====\n")
        for agent, content in self.data.items():
            print(f"[{agent}]")
            print("Analysis:", content["analysis"])
            print("LLM Proposal:", content["llm_proposal"])
            print("-" * 50)
