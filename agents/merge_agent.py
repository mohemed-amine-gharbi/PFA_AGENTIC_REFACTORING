# agents/merge_agent.py

class MergeAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "MergeAgent"

    def merge(self, original_code, codes_list, temperature=None):
        """Fusionne le code original avec les propositions des agents"""
        if not codes_list:
            return original_code

        # Construire un prompt pour le LLM
        combined_prompt = "Fusionne les modifications suivantes avec le code original :\n\n"
        for idx, c in enumerate(codes_list):
            combined_prompt += f"Modification {idx+1}:\n{c}\n\n"

        if temperature is not None:
            merged_code = self.llm.ask(
                system_prompt="Tu es un assistant expert en refactoring de code. Fusionne les changements proposés en gardant le code fonctionnel et clair.",
                user_prompt=original_code + "\n\n" + combined_prompt,
                temperature=temperature
            )
        else:
            merged_code = self.llm.ask(
                system_prompt="Tu es un assistant expert en refactoring de code. Fusionne les changements proposés en gardant le code fonctionnel et clair.",
                user_prompt=original_code + "\n\n" + combined_prompt
            )

        return merged_code