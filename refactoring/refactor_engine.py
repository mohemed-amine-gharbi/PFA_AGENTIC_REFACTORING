class RefactorEngine:
    def __init__(self):
        self.refactored_code = ""

    def apply(self, llm_proposals):
        code_sections = []
        for agent, content in llm_proposals.items():
            if content["llm_proposal"].strip() != "No refactoring needed.":
                code_sections.append(content["llm_proposal"])
        self.refactored_code = "\n\n".join(code_sections)
        return self.refactored_code
