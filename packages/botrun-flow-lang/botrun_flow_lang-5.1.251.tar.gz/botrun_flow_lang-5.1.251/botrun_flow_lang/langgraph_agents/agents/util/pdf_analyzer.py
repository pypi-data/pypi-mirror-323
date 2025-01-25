import anthropic
import base64
import httpx


def analyze_pdf(pdf_url: str, user_input: str):
    """
    Analyze a PDF file using Claude API

    Args:
        pdf_url: URL to the PDF file
        user_input: User's query about the PDF content

    Returns:
        str: Claude's analysis of the PDF content based on the query
    """
    try:
        # Download and encode the PDF file from URL
        pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")

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
