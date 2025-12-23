# Gemini-ADK-Duckduckgo-Weather-AI-Agent

**Gemini-ADK-Duckduckgo-Weather-AI-Agent** is an advanced agentic AI application built using the **Google ADK (Generative AI)** framework and **DuckDuckGo** for real-time web search. It leverages the power of Gemini 2.5 Flash Lite to intelligently orchestrate tools for fetching weather data and local time.

## Key Technologies & Tools

-   **Google ADK / GenAI**: Powered by `google.generativeai` for agentic reasoning and tool calling.
-   **DuckDuckGo**: Integrated via `ddgs` for real-time, privacy-focused web search capabilities.
-   **Open-Meteo**: High-precision weather data provider without API key requirements.
-   **Python 3.10+**: Core runtime environment.

## Features

-   **Agentic Orchestration**: Uses Google's Agent Development Kit patterns to autonomously decide which tools to use.
-   **Real-time Weather**: Accurate global weather forecasts.
-   **Local Time w/ ZoneInfo**: Precise time zone calculations.
-   **Web Search (DDG)**: Answers general queries with live web data.
-   **Robust Error Handling**: Includes fixes for specific Python environment issues (e.g., Python 3.14 protobuf compatibility).

## Prerequisites

-   Python 3.10 or higher
-   A Google Cloud API Key with access to Gemini models.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/weathersense-ai.git
    cd weathersense-ai
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, install manually: `pip install google-generativeai requests duckduckgo-search python-dotenv`)*

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your Google API key:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

## Usage

Run the agent script:

```bash
python agent.py
```

**Example Interaction:**

```text
Initializing Weather & Time Agent...
Agent ready! (Type 'quit' to exit)
You: What's the weather like in Tokyo?
[Tool] Getting weather for: Tokyo
Agent: Weather in Tokyo: Partly cloudy, 15.2 °C
You: What time is it there?
[Tool] Getting time for: Tokyo
Agent: Current time in Tokyo (Asia/Tokyo): 2023-10-27 14:30:00
```

## Project Structure

-   `agent.py`: Main application script containing the agent logic and tool definitions.
-   `tools.py`: (Optional) Separate module for tool functions if you choose to modularize further.
-   `.env`: Configuration file for API keys (do not commit this file).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is open-source and available under the [MIT License](LICENSE).
