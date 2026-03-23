from core.graphrag_retriever import GraphRAGRetriever

r = GraphRAGRetriever()
pack = r.retrieve("TemperatureConfig and LangGraphOrchestrator refactoring context", k_seeds=4, hops=2, max_chunks=5)

print("Symbols:", pack.get("symbols"))
print("Seeds:", pack.get("seeds"))
print("\n--- CONTEXT ---\n")
print(r.format_context(pack))