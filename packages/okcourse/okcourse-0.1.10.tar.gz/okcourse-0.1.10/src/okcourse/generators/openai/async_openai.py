"""The `async_openai` module contains the [`OpenAIAsyncGenerator`][okcourse.OpenAIAsyncGenerator] class."""

import asyncio
import base64
import io
import time
from pathlib import Path
from string import Template

from openai import APIError, APIStatusError, AsyncOpenAI, OpenAIError

from okcourse.constants import AI_DISCLOSURE, MAX_LECTURES
from okcourse.generators.base import CourseGenerator
from okcourse.models import Course, CourseLecture, CourseOutline
from okcourse.utils.audio_utils import combine_mp3_buffers
from okcourse.utils.log_utils import get_top_level_version, time_tracker
from okcourse.utils.text_utils import (
    LLM_SMELLS,
    download_tokenizer,
    sanitize_filename,
    split_text_into_chunks,
    swap_words,
    tokenizer_available,
)


class OpenAIAsyncGenerator(CourseGenerator):
    """Uses the OpenAI API to generate course content asynchronously.

    Use the `OpenAIAsyncGenerator` to generate a course outline, lectures, cover image, and audio file for a course.

    Examples:
    Generate a full course, including its outline, lectures, cover image, and audio file:

    ```python
    --8<-- "examples/snippets/async_openai_snippets.py:full_openaiasyncgenerator"
    ```

    """

    def __init__(self, course: Course):
        """Initializes the asynchronous OpenAI course generator.

        Args:
            course: The course to generate content for.

        """
        super().__init__(course)

        self.client = AsyncOpenAI()

    async def generate_outline(self, course: Course) -> Course:
        """Generates a course outline based on its `title` and other [`settings`][okcourse.models.Course.settings].

        Set the course's [`title`][okcourse.models.Course.title] attribute before calling this method.

        Returns:
            Course: The result of the generation process with its `course.outline` attribute set.

        Raises:
            ValueError: If the course has no title.

        Examples:
        ```python
        --8<-- "examples/snippets/async_openai_snippets.py:generate_outline"
        ```

        """
        if not course.title or course.title.strip() == "":
            msg = "The given Course has no title. Set the course's 'title' attribute before calling this method."
            self.log.error(msg)
            raise ValueError(msg)
        if course.settings.num_lectures > MAX_LECTURES:
            msg = f"Number of lectures exceeds the maximum allowed ({MAX_LECTURES})."
            self.log.error(msg)
            raise ValueError(msg)

        course.settings.output_directory = course.settings.output_directory.expanduser().resolve()

        outline_prompt = Template(course.settings.prompts.outline).substitute(
            num_lectures=course.settings.num_lectures,
            course_title=course.title,
            num_subtopics=course.settings.num_subtopics,
        )

        self.log.info(f"Requesting outline for course '{course.title}'...")
        with time_tracker(course.generation_info, "outline_gen_elapsed_seconds"):
            outline_completion = await self.client.beta.chat.completions.parse(
                model=course.settings.text_model_outline,
                messages=[
                    {"role": "system", "content": course.settings.prompts.system},
                    {"role": "user", "content": outline_prompt},
                ],
                response_format=CourseOutline,
            )
        self.log.info(f"Received outline for course '{course.title}'...")

        if outline_completion.usage:
            course.generation_info.outline_input_token_count += outline_completion.usage.prompt_tokens
            course.generation_info.outline_output_token_count += outline_completion.usage.completion_tokens
        generated_outline = outline_completion.choices[0].message.parsed

        # Reset the topic to what was passed in if the LLM modified the original (it sometimes adds its own subtitle)
        if generated_outline.title.lower() != course.title.lower():
            self.log.info(f"Resetting course topic to '{course.title}' (LLM returned '{generated_outline.title}'")
            generated_outline.title = course.title

        course.outline = generated_outline
        return course

    async def _generate_lecture(self, course: Course, lecture_number: int) -> CourseLecture:
        """Generates a lecture for the topic with the specified number in the given outline.

        Args:
            course: The course with a populated `outline` attribute containing lecture topics and their subtopics.
            lecture_number: The position number of the lecture to generate.

        Returns:
            A Lecture object representing the lecture for the given number.

        Raises:
            ValueError: If no topic is found for the given lecture number.

        """
        topic = next((t for t in course.outline.topics if t.number == lecture_number), None)
        if not topic:
            raise ValueError(f"No topic found for lecture number {lecture_number}")

        lecture_prompt = Template(course.settings.prompts.lecture).substitute(
            lecture_title=topic.title,
            course_title=course.title,
            course_outline=str(course.outline),
        )

        messages = []
        if course.settings.text_model_lecture.startswith("o1"):
            # Current o1 models don't have a 'system' role, only 'user'.
            lecture_prompt = f"{course.settings.prompts.system}\n\n{lecture_prompt}"
            messages = [
                {"role": "user", "content": lecture_prompt},
            ]
        else:
            messages = [
                {"role": "system", "content": course.settings.prompts.system},
                {"role": "user", "content": lecture_prompt},
            ]

        self.log.info(
            f"Requesting lecture text for topic {topic.number}/{len(course.outline.topics)}: {topic.title}...",
        )
        response = await self.client.chat.completions.create(
            model=course.settings.text_model_lecture,
            messages=messages,
            max_completion_tokens=15000,
        )
        if response.usage:
            course.generation_info.lecture_input_token_count += response.usage.prompt_tokens
            course.generation_info.lecture_output_token_count += response.usage.completion_tokens
        lecture_text = response.choices[0].message.content.strip()
        lecture_text = swap_words(lecture_text, LLM_SMELLS)

        self.log.info(
            f"Got lecture text for topic {topic.number}/{len(course.outline.topics)} "
            f"@ {len(lecture_text)} chars: {topic.title}.",
        )
        return CourseLecture(**topic.model_dump(), text=lecture_text)

    async def generate_lectures(self, course: Course) -> Course:
        """Generates the text for the lectures in the course outline in the settings.

        To generate an audio file for the Course generated by this method, call `generate_audio`.

        Returns:
            The Course with its `course.lectures` attribute set.

        """
        course.settings.output_directory = course.settings.output_directory.expanduser().resolve()
        lecture_tasks = []

        with time_tracker(course.generation_info, "lecture_gen_elapsed_seconds"):
            async with asyncio.TaskGroup() as task_group:
                for topic in course.outline.topics:
                    task = task_group.create_task(
                        self._generate_lecture(course, topic.number),
                        name=f"generate_lecture_{topic.number}",
                    )
                    lecture_tasks.append(task)

        course.lectures = [lecture_task.result() for lecture_task in lecture_tasks]

        return course

    async def generate_image(self, course: Course) -> Course:
        """Generates cover art for the course with the given outline.

        The image is appropriate for use as cover art for the course text or audio.

        Returns:
            The results of the generation process with the `image_bytes` attribute set.

        Raises:
            OpenAIError: If an error occurs during image generation.

        """
        course.settings.output_directory = course.settings.output_directory.expanduser().resolve()
        try:
            with time_tracker(course.generation_info, "image_gen_elapsed_seconds"):
                image_response = await self.client.images.generate(
                    model=course.settings.image_model,
                    prompt=Template(course.settings.prompts.image).substitute(course_title=course.title),
                    n=1,
                    size="1024x1024",
                    response_format="b64_json",
                    quality="standard",
                    style="vivid",
                )

            if not image_response.data:
                self.log.warning(f"No image data returned for course '{course.title}'")
                return None

            course.generation_info.num_images_generated += 1
            image = image_response.data[0]
            image_bytes = base64.b64decode(image.b64_json)

            course.generation_info.image_file_path = course.settings.output_directory / Path(
                sanitize_filename(course.title),
            ).with_suffix(".png")
            course.generation_info.image_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.log.info(f"Saving image to {course.generation_info.image_file_path}")
            course.generation_info.image_file_path.write_bytes(image_bytes)

            # Save the course as JSON now that we have the image path
            course.generation_info.image_file_path.with_suffix(".json").write_text(course.model_dump_json(indent=2))

            return course

        except OpenAIError as e:
            self.log.error("Encountered error generating image with OpenAI:")
            if e is APIError:
                self.log.error(f"  Message: {e.message}")
                self.log.error(f"      URL: {e.request.url}")  # e.request is an httpx.Request
                if e is APIStatusError:
                    self.log.error(
                        # Guaranteed to have a complete response as this is bubbled up from httpx
                        f"   Status: {e.response.status_code} - {e.response.reason_phrase}",
                    )
            raise e

    async def _generate_speech_for_text_chunk(
        self,
        course: Course,
        text_chunk: str,
        chunk_num: int = 1,
    ) -> tuple[int, io.BytesIO]:
        """Generates an MP3 audio segment for a chunk of text using text-to-speech (TTS).

        Get text chunks to pass to this function from ``utils.split_text_into_chunks``.

        Args:
            course: The course to generate TTS audio for.
            text_chunk: The text chunk to convert to speech.
            chunk_num: (Optional) The chunk number.

        Returns:
            An io.BytesIO of the generated audio.

        """
        self.log.info(f"Requesting TTS audio in voice '{course.settings.tts_voice}' for text chunk {chunk_num}...")
        async with self.client.audio.speech.with_streaming_response.create(
            model=course.settings.tts_model,
            voice=course.settings.tts_voice,
            input=text_chunk,
        ) as response:
            audio_bytes = io.BytesIO()
            async for data in response.iter_bytes():
                audio_bytes.write(data)
            audio_bytes.seek(0)
            course.generation_info.tts_character_count += len(text_chunk)
            self.log.info(f"Got TTS audio for text chunk {chunk_num} in voice '{course.settings.tts_voice}'.")

            return audio_bytes

    async def generate_audio(self, course: Course) -> Course:
        """Generates an audio file from the combined text of the lectures in the given course using a TTS AI model.

        Returns:
            The course with its `audio_file_path` attribute set which points to the TTS-generated file.

        """
        course.settings.output_directory = course.settings.output_directory.expanduser().resolve()
        if not tokenizer_available():
            download_tokenizer()

        # Combine all lecture texts, including titles, preceded by the disclosure that it's all AI-generated
        course_text = (
            AI_DISCLOSURE
            + "\n\n"
            + course.title
            + "\n\n".join(f"Lecture {lecture.number}:\n\n{lecture.text}" for lecture in course.lectures)
        )
        course_chunks = split_text_into_chunks(course_text)

        speech_tasks = []

        with time_tracker(course.generation_info, "audio_gen_elapsed_seconds"):
            async with asyncio.TaskGroup() as task_group:
                for chunk_num, chunk in enumerate(course_chunks, start=1):
                    task = task_group.create_task(
                        self._generate_speech_for_text_chunk(
                            course=course,
                            text_chunk=chunk,
                            chunk_num=chunk_num,
                        ),
                    )
                    speech_tasks.append(task)

            # Assemble the chunk list in the same order the tasks were created (no need to sort)
            audio_chunks = [speech_task.result() for speech_task in speech_tasks]

            # Get the MP3 tags ready
            if course.generation_info.image_file_path and course.generation_info.image_file_path.exists():
                composer_tag = f"{course.settings.text_model_lecture} & {course.settings.tts_model} & {course.settings.image_model}"
                cover_tag = io.BytesIO(course.generation_info.image_file_path.read_bytes())
            else:
                composer_tag = f"{course.settings.text_model_lecture} & {course.settings.tts_model}"
                cover_tag = None

            course.generation_info.audio_file_path = course.settings.output_directory / Path(
                sanitize_filename(course.title),
            ).with_suffix(".mp3")
            course.generation_info.audio_file_path.parent.mkdir(parents=True, exist_ok=True)

            version_string = get_top_level_version("okcourse")

            tags = {
                "title": course.title,
                "artist": f"{course.settings.tts_voice.capitalize()} & {course.settings.text_model_lecture} @ OpenAI",
                "composer": composer_tag,
                "album": "OK Courses",
                "genre": "Books & Spoken",
                "date": str(time.gmtime().tm_year),
                "author": f"Generated by AI with okcourse v{version_string}",
                "website": "https://github.com/mmacy/okcourse",
            }

            combined_mp3 = combine_mp3_buffers(
                audio_chunks,
                tags=tags,
                album_art=cover_tag,
                album_art_mime="image/png",
            )

            self.log.info(f"Saving audio to {course.generation_info.audio_file_path}")
            course.generation_info.audio_file_path.write_bytes(combined_mp3.getvalue())

        # Save the course as JSON now that we have the audio file path
        course.generation_info.audio_file_path.with_suffix(".json").write_text(course.model_dump_json(indent=2))

        return course

    async def generate_course(self, course: Course) -> Course:
        """Generates a complete course, including its outline, lectures, a cover image, and audio.

        Args:
            course: The course to generate.

        Returns:
            Course: The course with all attributes populated by the generation process.

        """
        course = await self.generate_outline(course)
        course = await self.generate_lectures(course)
        course = await self.generate_image(course)
        course = await self.generate_audio(course)

        return course
