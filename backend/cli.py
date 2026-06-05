from query import answer_question

def main():
    print("Ask a question (empty line or Ctrl+C to quit).\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            break

        result = answer_question(question)
        print(f"\n{result['answer']}\n")
        if result.get("sources"):
            print(f"Sources: {', '.join(result['sources'])}\n")

if __name__ == "__main__":
    main()
