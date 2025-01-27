# llm-jina-research

[![PyPI](https://img.shields.io/pypi/v/llm-jina-research.svg)](https://pypi.org/project/llm-jina-research/)
[![Changelog](https://img.shields.io/github/v/release/simonw/llm-jina-research?include_prereleases&label=changelog)](https://github.com/simonw/llm-jina-research/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/llm-jina-research/blob/main/LICENSE)

LLM plugin for comprehensive research using Jina AI's Search Foundation APIs

## Installation

Install this plugin in the same environment as LLM:

```bash
llm install llm-jina-research
```

Set your Jina AI API key:

```bash
export JINA_API_KEY="your_api_key_here"
```

Get your Jina AI API key for free: https://jina.ai/?sui=apikey

## Usage

Perform comprehensive research using Jina AI's APIs:

```bash
llm research "What are the latest advancements in AI safety?"
```

Options:
- `query`: The research question to investigate
- `--output`: Path to save results as JSON file

## Features

- 🔍 Web search with relevance filtering
- 📥 Advanced content extraction with reader API
- 🧬 Query embedding generation
- 🔬 Document reranking based on relevance
- 📊 Interactive terminal report generation
- 📄 JSON output for programmatic use
- 📝 Automatic research session logging

## Example

```bash
llm research "What are the latest advancements in AI safety?" --output results.json
```

This will:
1. Search the web for relevant information
2. Extract and process content from top results
3. Analyze and rank the content
4. Generate an interactive report
5. Save the results to a JSON file

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```bash
cd llm-jina-research
python -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
pytest
```

## Contributing

Contributions to llm-jina-research are welcome! Please refer to the [GitHub repository](https://github.com/simonw/llm-jina-research) for more information on how to contribute.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.