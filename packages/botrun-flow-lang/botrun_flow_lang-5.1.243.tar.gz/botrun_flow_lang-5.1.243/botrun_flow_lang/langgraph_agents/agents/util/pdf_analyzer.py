import anthropic
import base64
from pathlib import Path


def analyze_pdf(pdf_path: str, user_input: str):
    """
    Analyze a PDF file using Claude API

    Args:
        pdf_path: Path to the PDF file
        user_input: User's query about the PDF content

    Returns:
        str: Claude's analysis of the PDF content based on the query
    """
    try:
        # Read and encode the local PDF file
        with open(pdf_path, "rb") as pdf_file:
            pdf_data = base64.b64encode(pdf_file.read()).decode("utf-8")

        # Initialize Anthropic client
        client = anthropic.Anthropic()

        # Send to Claude
        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=4096,  # Increased token limit for detailed analysis
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_data,
                            },
                        },
                        {"type": "text", "text": user_input},
                    ],
                }
            ],
        )

        return message.content[0].text

    except Exception as e:
        print(f"Error analyzing PDF: {str(e)}")
        return None
