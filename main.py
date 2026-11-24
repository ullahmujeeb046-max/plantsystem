from expert_system import TomatoExpertSystem

def main():
    system = TomatoExpertSystem()
    print("=" * 68)
    print(" TOMATO PLANT DISEASE DIAGNOSIS EXPERT SYSTEM")
    print("=" * 68)
    print("Describe what you observe on your tomato plant in ordinary English.")
    print("Example: 'The lower leaves have yellowing and dark brown spots with rings.'")
    print("Type 'help' for example symptoms, or 'quit' to exit.\n")

    while True:
        try:
            text = input("Describe symptoms > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if text.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break
        if text.lower() == "help":
            print("\nExamples:")
            print("- white powdery leaf coating and leaf yellowing")
            print("- plant suddenly wilts although soil is moist")
            print("- dark concentric spots on lower leaves")
            print("- root galls and stunted growth")
            print("- dark sunken patch at the bottom of fruit")
            print("- mosaic green leaves and distorted new growth\n")
            continue
        if not text:
            print("Please describe at least one symptom.\n")
            continue

        result = system.diagnose(text)
        if not result["recognized_symptoms"]:
            print("\nI could not confidently recognize a symptom from that description.")
            print("Try describing visible signs such as spots, yellowing, wilting, mold, or root galls.")
            print("Type 'help' for examples.\n")
            continue

        print("\nRecognized observations:")
        for symptom in result["recognized_symptoms"]:
            print(f"  - {symptom}")

        if not result["diagnoses"]:
            print("\nNo diagnosis rule was fully matched.")
            print("Please provide more symptoms. This does not mean the plant is healthy.\n")
            continue

        print("\nPossible diagnoses (ranked by rule evidence):")
        for i, diagnosis in enumerate(result["diagnoses"], 1):
            print(f"\n{i}. {diagnosis['name']} — evidence score: {diagnosis['score']}%")
            print(f"   Matched rules: {', '.join(diagnosis['matched_rules'])}")
            print(f"   Why: {diagnosis['explanation']}")
            print(f"   Management: {diagnosis['management']}")
            print(f"   Prevention: {diagnosis['prevention']}")
        print("\nNote: This is an educational screening result, not a confirmed diagnosis.")
        print("For serious or spreading symptoms, consult a local agricultural extension expert.\n")

if __name__ == "__main__":
    main()
