import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import tiktoken
import os
from dotenv import load_dotenv

load_dotenv()
client=OpenAI()


def fetch_and_clean_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'} 
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup=BeautifulSoup(response.text,"html.parser")

        for element in soup(["scripts","nav","style","header","footer","aside"]):
            element.decompose()
        text=soup.get_text(separator=" ",strip=True)
        lines=(line.strip() for line in text.splitlines())
        text=" ".join(line for line in lines if line)

        return text[:15000]

    except Exception as e:
        return f"Error fetching page:{str(e)}"


def count_tokens(text):
    encoding=tiktoken.encoding_for_model("gpt-4o-mini")
    return len(encoding.encode(text))


def summarize_text(text,max_length=300):
    if not text or "Error" in text:
        return text
    token_count=count_tokens(text)
    print(f"Text_length:{token_count} token")


    prompt = f"""
    Summarize the following article in a clear, concise, and engaging way.
    Include the main points, key arguments, and conclusion if present.
    Use bullet points for readability when appropriate.
    Keep the summary under {max_length} words.
    
    Article:
    {text}
    """

    try:
        response=client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are excpert Summarizer"},
                {"role":"user","content":prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"API Error: {str(e)}"

if __name__ == "__main__":
    url = input("Enter website URL: ").strip()
    print("Fetching and cleaning content...")
    text = fetch_and_clean_text(url)
    
    print("Generating summary...")
    summary = summarize_text(text)
    print("\n" + "="*50)
    print("SUMMARY:")
    print(summary)

