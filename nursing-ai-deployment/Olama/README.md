# Nursing AI – Local Deployment with Ollama

This guide explains how to run the Mistral-based Nursing AI assistant locally using [Ollama](https://ollama.com).

## 🧰 Requirements

- Windows, macOS, or Linux
- Ollama installed → https://ollama.com/download
- Model: `mistral:7b-instruct` (automatically pulled by Ollama)

## 📁 Included Files

- `Modelfile` – defines system behavior (AI as nurse trainer)
- `prompt.txt` – full prompt content (duplicated in `Modelfile`)
- `README.md` – you're reading it 🙂

## ⚙️ Setup Steps

1. **Download or clone this folder**
2. Open Terminal or CMD in this folder
3. Run the following command:

```bash
ollama create nursing-ai -f Modelfile
