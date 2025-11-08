from google import genai
client=genai.Client(api_key='AIzaSyAYioiyAlQFNZih4qJZdaM6N1xnkF5yj2A')
response=client.models.generate_content_stream(
    model="gemini-2.5-flash-lite",
    contents='Mô tả việt nam')
for chunk in response:
    print(chunk.text)
