import streamlit as st

from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# check if the API key is set
if 'OPENAI_API_KEY' not in os.environ:
    st.error('Please set the OPENAI_API_KEY environment variable.')
    st.stop()

def get_transcript(youtube_url):
    video_id = youtube_url.split("v=")[-1]
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try fetching the manual transcript
    try:
        transcript = transcript_list.find_manually_created_transcript()
        language_code = transcript.language_code  # Save the detected language
    except:
        # If no manual transcript is found, try fetching an auto-generated transcript in a supported language
        try:
            generated_transcripts = [trans for trans in transcript_list if trans.is_generated]
            transcript = generated_transcripts[0]
            language_code = transcript.language_code  # Save the detected language
        except:
            # If no auto-generated transcript is found, raise an exception
            raise Exception("No suitable transcript found.")

    full_transcript = " ".join([part['text'] for part in transcript.fetch()])
    return full_transcript, language_code  # Return both the transcript and detected language

def summarize_with_langchain_and_openai(transcript, language_code, model_name='gpt-3.5-turbo'):
    # Split the document if it's too long
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    texts = text_splitter.split_text(transcript)
    text_to_summarize = " ".join(texts[:4]) # Adjust this as needed

    # Prepare the prompt for summarization
    system_prompt = 'I want you to act as a Life Coach that can create good summaries!'
    prompt = f'''Summarize the following text in {language_code}.
    Text: {text_to_summarize}

    Add a title to the summary in {language_code}.
    Include an INTRODUCTION, BULLET POINTS if possible, and a CONCLUSION in {language_code}.

    The BULLET POINTS should be in the form of emojis followed by a sentence. The emoji should represent the main point of the sentence.

    Use the example below as the format for the summary:

    <example>

    # Title: The Future of the World Depends on Quality Education

    ## Introduction
    The future of the world depends on providing quality education to every child, regardless of their background, and the importance of addressing mental health issues, even among successful individuals.

    ## Main points
    🎙 FWE is continuing the legacy of its founder, Mr. Paul Kelly, by working with business leaders, education researchers, and policymakers to connect countries and promote international citizenship through education.

    🌍 Disadvantaged population students need to contribute to their own country, FWE is planning to promote mass education internationally, and they are working with scholars to develop webinars and research programs. FWE is focused on promoting mass education and building an international network to support vocational education.

    🌍 Switzerland is promoting vocational education to support young students and has a partnership with the US to learn from Swiss companies' successful workforce development.
    👥 We need to change and learn from other countries in order to improve education, and the speaker is grateful for the support.

    🌍 Chen Davis and Dr. Susan Scani have been instrumental in gathering scholars and young leaders from around the world to improve the quality of education.

    🌍 Every child deserves access to quality education regardless of location, ethnicity, or income for a better future.

    🎯 We work hard to champion the continued focus on the quality of education in schools to improve it for every child.

    🌍 We work with educators and the business community to ensure opportunities for all children and look forward to learning and improving together.

    ## Conclusion

    The future of the world depends on providing quality education to every child, regardless of their background, and the importance of addressing mental health issues, even among successful individuals.

    </example>

    The OUTPUT should be in the form of a markdown file. The bullet points should have two new lines between them.

    '''

    client = OpenAI()

    # Start summarizing using OpenAI

    chat_completion = client.chat.completions.create(
      messages=[
          {
              "role": "system",
              "content": system_prompt,
          },
          {
              "role": "user",
              "content": prompt,
          }
      ],
      temperature=1,
      model=model_name,
    )

    return chat_completion.choices[0].message.content


def main():
    st.title('YouTube video summarizer')
    link = st.text_input('Enter the link of the YouTube video you want to summarize:')

    # add options for the model
    model_option = st.selectbox('Select the model:', ['gpt-3.5-turbo', 'gpt-4-turbo'])

    if st.button('Start'):
        if link:
            try:
                progress = st.progress(0)
                status_text = st.empty()

                status_text.text('Loading the transcript...')
                progress.progress(25)

                # Getting both the transcript and language_code
                transcript, language_code = get_transcript(link)

                status_text.text(f'Creating summary...')
                progress.progress(75)

                model_name = model_option
                summary = summarize_with_langchain_and_openai(transcript, language_code, model_name)

                status_text.text('Summary:')
                print(summary)
                st.markdown(summary)
                progress.progress(100)
            except Exception as e:
                st.write(str(e))
        else:
            st.write('Please enter a valid YouTube link.')

if __name__ == "__main__":
    main()
