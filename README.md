<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
# MCP-LLM Agent Tool + Ollama Fine-Tuning

This repository contains a function-calling LLM agent system using a modular architecture (LangGraph-inspired) and supports fine-tuning an Ollama-compatible model. The goal is to build an intelligent agent capable of interacting with real-world tools and improve its domain understanding via fine-tuning.

---

## 🧠 Project Objectives

- Enable LLMs to **dynamically call functions** (tool use) with real-world integrations (e.g., Google API).
- Build an **agentic architecture** (LangGraph-style) to allow structured decision-making.
- Provide schema-based input/output formatting for agent consistency.
- Fine-tune a model using **Ollama-compatible architecture** for enhanced performance on domain-specific tasks.

---

## 📁 Project Structure
```
mcp-llm-agent/
├── function.py # Tool definitions (Google API integration, user/applicant search, etc.)
├── schema.py # Input/output schema for function calling
├── finetune.ipynb # Notebook for fine-tuning the model (Ollama)
├── inference.ipynb # Notebook to test the fine-tuned model's performance
├── data/ # Training data for fine-tuning
├── prompts/ # Prompt templates and instruction tuning samples
├── requirements.txt # Dependency list
|── README.md # This documentation file
|__ calender config folder # credential document provided from google api, replace with your
    credential key

```
## ✅ Component Overview & Progress

### `function.py`
- ✅ Google API integration implemented.
- ⚠️ Improvement needed in **applicant search logic** for better LLM tool selection and disambiguation.
- ⚠️ LangGraph-style **agent flow** defined; requires enhanced prompting to guide LLM decisions accurately.

### `schema.py`
- ✅ Completed. Defines **structured schemas** for function inputs/outputs (e.g., using `Pydantic` or manual validation).
- Provides strong consistency between agent output and callable functions.

### `finetune.ipynb`
- ✅ Architecture for fine-tuning using Ollama is implemented.
- ⚠️ Issue: **High training loss** – likely caused by dataset formatting or suboptimal hyperparameters.
- ⚠️ Limitation: High computation requirements make it difficult to run more than 100 iterations efficiently.

### `inference.ipynb`
- ✅ Contains **testing pipeline** for the fine-tuned model.
- Used for evaluating model responses and tool prediction accuracy post-finetuning.

---

## 🧪 Quick Start

### Installation

```bash
git clone https://github.com/yourname/mcp-llm-agent.git
cd mcp-llm-agent
pip install -r requirements.txt
```
### Example Use
```
from function import get_calendar_events
from schema import CalendarEventInput

query = CalendarEventInput(date="2025-08-07", user="john@example.com")
events = get_calendar_events(query)
print(events)
```

## 🔧 Fine-Tuning with Ollama
Make sure you have Ollama installed and set up.

Finetuning Steps:
Prepare dataset in ChatML / JSONL format.

Adjust hyperparameters inside finetune.ipynb.

Run fine-tuning script.
```
ollama create my-model -f ./finetune_model
```
⚠️ Tip: Use small datasets or optimized batches if you’re running on limited compute.

## 🔍 Inference Testing
Use inference.ipynb to evaluate how the fine-tuned model behaves with tool-specific queries.

Test predictions for tool names

Check adherence to schema.py definitions

Evaluate reasoning chain (action flow)

## 📌 Known Issues
Area	Issue
function.py	Applicant search lacks precision – LLM often fails to select correct users
function.py	Prompt design needs refinement for agentic flow
finetune.ipynb	Training loss remains high despite architecture being valid
finetune.ipynb	Computational cost too high for long iterations

## 🧩 Future Roadmap
 Improve retrieval-based reasoning for applicant/user disambiguation

 Refine LangGraph-inspired prompting and flow control

 Optimize dataset format and augment examples for fine-tuning

 Add evaluation metrics and comparison against baseline model

## 📄 License
MIT License — feel free to use and adapt the code with proper attribution.

## 👨‍💻 Author
Developed by Lai Yungseng
AI/ML Engineer | LLM Workflow Builder | Automation Specialist
GitHub | LinkedIn
=======
# MCP-llm-finetune
Implementing mcp to allow llm to perform task/ funtion calling. Included ollama fine tuning to tune llama.3.2 to to more adapt to function calling and reasoning.
>>>>>>> 5f02350192c0a1e0b0e8805bda552b15964f136c
=======
# MCP-llm-finetune
Implementing mcp to allow llm to perform task/ funtion calling. Included ollama fine tuning to tune llama.3.2 to to more adapt to function calling and reasoning.
>>>>>>> 5f02350192c0a1e0b0e8805bda552b15964f136c
=======
# MCP-llm-finetune
Implementing mcp to allow llm to perform task/ funtion calling. Included ollama fine tuning to tune llama.3.2 to to more adapt to function calling and reasoning.
>>>>>>> 5f02350192c0a1e0b0e8805bda552b15964f136c
