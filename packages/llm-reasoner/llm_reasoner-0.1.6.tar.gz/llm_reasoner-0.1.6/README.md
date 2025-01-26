# 🤔 LLM-Reasoner

Transform any LLM into a methodical thinker that excels at systematic reasoning like OpenAI o1 and DeepSeek R1

## 🚀 Getting Started

Install LLM-Reasoner with pip:
```bash
pip install llm-reasoner
```

Configure your API keys:
```bash
# Using OpenAI? Pop this in:
export OPENAI_API_KEY="your-key"

# Team Google? Here you go:
export VERTEX_PROJECT="your-project"
export VERTEX_LOCATION="your-location"

# Claude fan? Got you covered:
export ANTHROPIC_API_KEY="your-key"
```

## 🎮 Quick Play

Try these commands to get started:

```bash
# Check out what models you can use
llm-reasoner models

# Ask it something cool
llm-reasoner reason "Why do planes stay up in the air?"

# Want a nice UI to play with?
llm-reasoner ui
```

## 🛠️ Using It In Your Code

Here's how to use LLM-Reasoner in your Python code:

```python
from llm_reasoner import ReasonChain
import asyncio

async def main():
    # Initialize with default model (GPT-3.5 Turbo)
    chain = ReasonChain()
    
    # Get reasoning steps with basic content
    async for step in chain.generate("How does evolution work?"):
        print(f"Step {step.number}: {step.content}")

asyncio.run(main())
```

For more detailed output and control:

```python
from llm_reasoner import ReasonChain

chain = ReasonChain(
    model="gpt-4",              # Choose your model
    max_tokens=750,             # Set max tokens per response
    temperature=0.2,            # Control randomness
    timeout=30.0                # Set API timeout in seconds
)

async def show_detailed_reasoning():
    query = "How do computers learn?"
    async for step in chain.generate_with_metadata(query):
        print(f"\nStep {step.number}: {step.title}")
        print(f"Confidence: {step.confidence:.2f}")
        print(f"Thinking time: {step.thinking_time:.2f}s")
        print(step.content)
        if step.is_final:
            print("\nFinal Answer!")

asyncio.run(show_detailed_reasoning())
```

## 📜 License

MIT License - See LICENSE file for details.

---

Made with ❤️ for those who believe AI should show its work! ✍️
