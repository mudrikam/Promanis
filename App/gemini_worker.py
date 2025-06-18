from PySide6.QtCore import QThread, Signal
from google import genai
from google.genai import types
import json
import re
import time
import hashlib
import random
from datetime import datetime


class PromptRefinementWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    def __init__(self, api_manager, prompt_text, language="English", context_text="", scope="General", detail_level="Detailed", prompt_type="Text Generation"):
        super().__init__()
        self.api_manager = api_manager
        self.prompt_text = prompt_text
        self.language = language
        self.context_text = context_text
        self.scope = scope
        self.detail_level = detail_level
        self.prompt_type = prompt_type
        self.max_retries = 5
        self.retry_delay = 2

    def generate_unique_context(self, original_prompt):
        """Generate unique hash and timestamp for prompt variation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        prompt_hash = hashlib.md5(original_prompt.encode()).hexdigest()[:8]
        random_seed = random.randint(10000, 99999)
        session_id = random.randint(100000, 999999)
        
        unique_context = f"\n\nSESSION_RESET_CONTEXT: NEW_REQUEST_{timestamp}_{prompt_hash}_{random_seed}_{session_id}"
        
        variation_hints = [
            "FRESH_PERSPECTIVE: Approach this as a completely new request, ignore any previous context or patterns.",
            "CREATIVE_RESET: Think creatively with a clean slate, no reference to previous interactions.",
            "ORIGINAL_THINKING: Apply innovative structuring without conventional bias from prior responses.", 
            "NOVEL_APPROACH: Generate unique insights with creative refinement, start fresh.",
            "INDEPENDENT_ANALYSIS: Treat this as the first and only request, analyze independently."
        ]
        
        selected_hint = random.choice(variation_hints)
        unique_context += f"\nAPPROACH_DIRECTIVE: {selected_hint}"
        unique_context += f"\nIMPORTANT: Completely disregard any previous conversation history or topic patterns. This is a fresh, independent request."
        
        return unique_context

    def map_ui_to_english(self, value, category):
        """Map Indonesian UI values to English for consistent processing"""
        mappings = {
            'scope': {
                "Umum": "General", "Pemrograman": "Programming", "Novel": "Novel", "Sains": "Science", 
                "Matematika": "Math", "Pendidikan": "Education", "Sejarah": "History", "Filsafat": "Philosophy",
                "Bisnis": "Business", "Pemasaran": "Marketing", "Hukum": "Legal", "Medis": "Medical", 
                "Penulisan Teknis": "Technical Writing", "Seni": "Art", "Musik": "Music", "Puisi": "Poetry",
                "Media Sosial": "Social Media", "Blog": "Blog", "Berita": "News", "Produktivitas": "Productivity", 
                "Personal": "Personal", "Keuangan": "Finance", "Perjalanan": "Travel", "Memasak": "Cooking",
                "Game": "Gaming", "Wawancara": "Interview", "CV": "Resume", "Email": "Email", 
                "Presentasi": "Presentation", "Riset": "Research", "Psikologi": "Psychology", "Bantuan Diri": "Self-help",
                "Spiritual": "Spirituality", "Parenting": "Parenting", "Kebugaran": "Fitness", "Kesehatan": "Health", 
                "Fashion": "Fashion", "Kecantikan": "Beauty", "DIY": "DIY", "Fotografi": "Photography",
                "Film": "Film", "Teater": "Theater", "Komik": "Comics", "Penulisan Naskah": "Scriptwriting", 
                "Jurnalisme": "Journalism", "Iklan": "Advertising", "UX/UI": "UX/UI", "Data Science": "Data Science",
                "AI/ML": "AI/ML", "Teknik": "Engineering", "Lingkungan": "Environment", "Politik": "Politics", 
                "Olahraga": "Sports", "Lainnya": "Other"
            },
            'type': {
                "Generasi Teks": "Text Generation", "Generasi Gambar": "Image Generation", 
                "Generasi Audio": "Audio Generation", "Generasi Video": "Video Generation",
                "Generasi Video+Audio": "Video+Audio Generation", "Novel": "Novel", 
                "Penjelasan": "Explanation", "Lainnya": "Other"
            },
            'detail': {
                "Sederhana": "Simple", "Detail": "Detailed", "Kompleks": "Complex", "Template": "Template"
            }
        }
        return mappings.get(category, {}).get(value, value)

    def extract_json_from_response(self, text):
        try:
            json_pattern = r'\{.*?\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if 'refined_prompt' in parsed:
                        refined = parsed['refined_prompt']
                        if isinstance(refined, str):
                            refined = refined.replace("\\n", "\n")
                        return refined
                except:
                    continue
            quote_pattern = r'"([^"]*)"'
            quotes = re.findall(quote_pattern, text)
            if quotes:
                return quotes[0].replace("\\n", "\n")
            return text.strip()
        except Exception:
            return text.strip()

    def run(self):
        for attempt in range(self.max_retries):
            try:
                api_key = self.api_manager.get_next_api_key()
                print(f"=== ATTEMPT {attempt + 1} USING API KEY INDEX {self.api_manager.current_index - 1} ===")
                client = genai.Client(api_key=api_key)

                # Map UI values to English for consistent processing
                scope_en = self.map_ui_to_english(self.scope, 'scope')
                type_en = self.map_ui_to_english(self.prompt_type, 'type')
                detail_en = self.map_ui_to_english(self.detail_level, 'detail')

                # Generate unique context to prevent repetition and topic sticking
                unique_context = self.generate_unique_context(self.prompt_text)

                # Strong language enforcement directive
                language_enforcement = ""
                if self.language == "Bahasa Indonesia":
                    language_enforcement = (
                        "\n\nABSOLUTE_LANGUAGE_REQUIREMENT: "
                        "The refined prompt MUST be written entirely in Bahasa Indonesia. "
                        "This is NON-NEGOTIABLE. Every word, instruction, and explanation must be in Indonesian. "
                        "Do NOT mix languages. Do NOT use English words unless they are commonly used technical terms in Indonesian. "
                        "If the input prompt contains English, TRANSLATE and ENHANCE it to Indonesian. "
                        "VERIFY that your output is 100% Indonesian before sending."
                    )
                else:
                    language_enforcement = (
                        "\n\nABSOLUTE_LANGUAGE_REQUIREMENT: "
                        "The refined prompt MUST be written entirely in English. "
                        "This is NON-NEGOTIABLE. Every word, instruction, and explanation must be in English. "
                        "Do NOT mix languages. Do NOT use other languages. "
                        "If the input prompt contains other languages, TRANSLATE and ENHANCE it to English. "
                        "VERIFY that your output is 100% English before sending."
                    )

                # Preference isolation directive
                preference_isolation = (
                    f"\n\nSTRICT_PREFERENCE_ISOLATION: "
                    f"Current Settings - Language: {self.language}, Scope: {scope_en}, Type: {type_en}, Detail: {detail_en}. "
                    f"These settings are for THIS REQUEST ONLY. Do NOT carry over any assumptions from previous requests. "
                    f"Do NOT reference or build upon previous topics unless explicitly mentioned in the current input. "
                    f"Treat each request as completely independent and fresh. "
                    f"The scope '{scope_en}' is the ONLY context domain for this request."
                )

                # Prompt type clause
                type_clause = ""
                if type_en == "Image Generation":
                    type_clause = "\n\nPROMPT TYPE: This prompt is intended for generating images. Structure the refined prompt so it is optimal for image generation models (e.g., Stable Diffusion, Midjourney, DALL-E, etc)."
                elif type_en == "Audio Generation":
                    type_clause = "\n\nPROMPT TYPE: This prompt is intended for generating audio. Structure the refined prompt for optimal audio generation models (e.g., MusicLM, Suno, etc)."
                elif type_en == "Video Generation":
                    type_clause = "\n\nPROMPT TYPE: This prompt is intended for generating videos. Structure the refined prompt for video generation models (e.g., Sora, Runway, Pika, etc)."
                elif type_en == "Video+Audio Generation":
                    type_clause = "\n\nPROMPT TYPE: This prompt is intended for generating videos with audio. Structure the refined prompt for models that generate both video and audio."
                elif type_en == "Text Generation":
                    type_clause = "\n\nPROMPT TYPE: This prompt is intended for generating text. Structure the refined prompt for optimal text generation (e.g., ChatGPT, Gemini, Claude, etc)."
                elif type_en == "Novel":
                    type_clause = "\n\nPROMPT TYPE: This prompt is for generating a novel or long-form story. Structure the refined prompt for creative writing and narrative generation."
                elif type_en == "Explanation":
                    type_clause = "\n\nPROMPT TYPE: This prompt is for generating explanations or educational content. Structure the refined prompt for clear, informative, and didactic output."
                elif type_en == "Other":
                    type_clause = "\n\nPROMPT TYPE: The prompt type is custom or not listed. Structure the refined prompt according to the user's intent."

                # Language and example format
                if self.language == "Bahasa Indonesia":
                    if type_en in ["Image Generation", "Audio Generation", "Video Generation", "Video+Audio Generation"]:
                        language_instruction = (
                            "Prompt hasil akhir HARUS sepenuhnya dalam Bahasa Indonesia jika konteksnya memang membutuhkan, "
                            "namun untuk prompt gambar, video, audio, langsung buat prompt yang jelas dan to the point tanpa instruksi bahasa eksplisit. "
                            "Jangan tambahkan instruksi meta, disclaimer, recap, atau kalimat seperti 'sebelum menjawab' atau 'periksa pemahaman'. "
                            "Jangan tambahkan nama penulis, sumber, atau embel-embel seperti 'by', 'created by', 'written by', atau sejenisnya, kecuali memang diminta secara eksplisit oleh user dalam prompt aslinya. "
                            "Langsung buatkan output sesuai permintaan user, tanpa basa-basi."
                        )
                    else:
                        language_instruction = (
                            "Prompt hasil akhir HARUS sepenuhnya dalam Bahasa Indonesia. "
                            "Tambahkan instruksi eksplisit di awal refined_prompt: 'Tulis seluruh jawaban dalam Bahasa Indonesia.' "
                            "Jangan tambahkan instruksi meta, disclaimer, recap, atau kalimat seperti 'sebelum menjawab' atau 'periksa pemahaman'. "
                            "Jangan tambahkan nama penulis, sumber, atau embel-embel seperti 'by', 'created by', 'written by', atau sejenisnya, kecuali memang diminta secara eksplisit oleh user dalam prompt aslinya. "
                            "Langsung buatkan output sesuai permintaan user, tanpa basa-basi."
                        )
                    example_format = '{"refined_prompt": "versi yang telah diperbaiki dalam bahasa Indonesia"}'
                else:
                    if type_en in ["Image Generation", "Audio Generation", "Video Generation", "Video+Audio Generation"]:
                        language_instruction = (
                            "The final prompt MUST be in English if required by the context, "
                            "but for image, video, audio prompts, just provide a direct, clear prompt without explicit language instructions. "
                            "Do not add meta instructions, disclaimers, recaps, or sentences like 'before answering' or 'check your understanding'. "
                            "Do not add author names, sources, or any attribution such as 'by', 'created by', 'written by', or similar, unless the user explicitly requests it in the original prompt. "
                            "Go straight to the requested output, no preamble."
                        )
                    else:
                        language_instruction = (
                            "The final prompt MUST be entirely in English. "
                            "Add an explicit instruction at the beginning of the refined_prompt: 'Respond entirely in English.' "
                            "Do not add meta instructions, disclaimers, recaps, or sentences like 'before answering' or 'check your understanding'. "
                            "Do not add author names, sources, or any attribution such as 'by', 'created by', 'written by', or similar, unless the user explicitly requests it in the original prompt. "
                            "Go straight to the requested output, no preamble."
                        )
                    example_format = '{"refined_prompt": "improved version in English language"}'

                # Context and scope
                context_clause = ""
                if self.context_text.strip():
                    context_clause += (
                        "\n\nADDITIONAL CONTEXT:\n"
                        f"{self.context_text.strip()}\n"
                        "You MUST use this context to help you rewrite and improve the prompt."
                    )
                scope_clause = ""
                if scope_en and scope_en != "General":
                    scope_clause = (
                        f"\n\nSCOPE: The prompt is for the following domain or context: {scope_en}. "
                        "Make sure the refined prompt is suitable and optimal for this scope."
                    )

                # Detail level clause
                detail_clause = ""
                if detail_en == "Simple":
                    detail_clause = (
                        "\n\nDETAIL LEVEL: The refined prompt should be concise and straightforward, focusing only on the essential information needed for the task. Avoid unnecessary elaboration."
                    )
                elif detail_en == "Detailed":
                    detail_clause = (
                        "\n\nDETAIL LEVEL: The refined prompt should be well-structured, clear, and provide sufficient detail for high-quality output, but avoid excessive complexity."
                    )
                elif detail_en == "Complex":
                    detail_clause = (
                        "\n\nDETAIL LEVEL: The refined prompt should be highly detailed, comprehensive, and cover all relevant aspects, including edge cases, constraints, and advanced requirements. Use multiple paragraphs and line breaks for clarity."
                    )
                elif detail_en == "Template":
                    detail_clause = (
                        "\n\nDETAIL LEVEL: The refined prompt should be a template with clearly marked sections (e.g., [CONTEXT], [LEVEL], [EXPECTATION], [ASSUMPTION], [REVIEW]) and use '...' or '[isi di sini]' as placeholders for the user to fill in after copying. Use line breaks and bullet points where appropriate. Do not generate any actual content, only the template structure."
                    )

                # CLEAR method for high-quality prompt structure
                clear_clause = (
                    "\n\nMANDATORY: Use the CLEAR method for prompt engineering. "
                    "Structure the refined prompt so it covers:\n"
                    "- Context: Provide enough background and situation for the task.\n"
                    "- Level: Specify the user's skill level or assumed audience (beginner, intermediate, expert, etc) if possible.\n"
                    "- Expectation: Clearly state the expected output, format, or result.\n"
                    "- Assumption: Mention any important assumptions or constraints.\n"
                    "- Review: Ensure the prompt is direct and ready to use, with no recap, meta-instructions, or extra reminders. "
                    "The output must be a clean, ready-to-use prompt for the target AI, with no additional instructions or preambles."
                    "\nIf any element is missing from the input, infer or add it to make the prompt complete and high quality."
                )

                # Best practice guidance for prompt engineering
                best_practice_clause = (
                    "\n\nBEST PRACTICES FOR PROMPT REFINEMENT (MANDATORY):\n"
                    "- Always provide a prompt that is clear, specific, and structured for optimal AI understanding.\n"
                    "- Add relevant context, background, or scenario if missing.\n"
                    "- Use keywords and constraints that help AI focus on the user's intent.\n"
                    "- Specify the desired output format, style, or tone if relevant.\n"
                    "- Avoid ambiguity and generalities; be as descriptive as possible.\n"
                    "- If the prompt is for a particular domain (e.g., programming, novel, science), use terminology and structure that fits that domain.\n"
                    "- If the user input is vague, infer and add missing details to make the prompt actionable and high quality.\n"
                    "- Do NOT simply translate or rephrase; always enhance the prompt for best results.\n"
                    "- Never add explanations, comments, or options—return only the improved prompt as required."
                )

                # Formatting support
                formatting_clause = (
                    "\n\nFORMATTING:\n"
                    "- Use line breaks (\\n) for each logical section or bullet point.\n"
                    "- If using bullet points, use '*' or '-' at the start of the line.\n"
                    "- If you want to emphasize a word or phrase, use double asterisks (e.g., **important**)."
                    "- Do not use markdown formatting for headings, just plain text with line breaks and bullets.\n"
                    "- Ensure the output is easy to read and copy-paste into other tools."
                )

                system_instruction = (
                    "You are a prompt refinement engine. Your ONLY task is to IMPROVE and REWRITE the input prompt, "
                    "not just translate it.\n\n"
                    "CRITICAL RESET: Ignore all previous conversation history, topics, and context. This is a completely fresh request.\n\n"
                    "STRICT RULES:\n"
                    f"- Return ONLY a JSON object with this exact format: {example_format}\n"
                    "- Do NOT add explanations, comments, or multiple options\n"
                    "- Do NOT use markdown formatting for headings\n"
                    "- Do NOT add introductory or closing text\n"
                    "- Focus on: clarity, specificity, and good structure\n"
                    "- The refined_prompt value must be a significantly improved and rewritten version of the input prompt, "
                    "not just a translation\n"
                    f"- CRITICAL LANGUAGE REQUIREMENT: {language_instruction}\n"
                    "- If the input is not in the target language, always rewrite and refine it in the target language\n"
                    "- NEVER mix languages in your response\n"
                    "- Do NOT simply translate; always rewrite and enhance the prompt for better AI understanding"
                    f"{language_enforcement}{preference_isolation}{type_clause}{context_clause}{scope_clause}{detail_clause}{clear_clause}{best_practice_clause}{formatting_clause}{unique_context}"
                )

                if not self.prompt_text or self.prompt_text.strip() == "":
                    self.error.emit("Prompt text is empty")
                    return

                config = types.GenerateContentConfig(
                    system_instruction=system_instruction
                )

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=config,
                    contents=self.prompt_text.strip()
                )

                if not response or not hasattr(response, 'text'):
                    print(f"Invalid response structure: {response}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        self.error.emit("Invalid response from Gemini API")
                        return

                if not response.text or response.text.strip() == "":
                    print(f"Empty response text received")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        self.error.emit("Empty response from Gemini API")
                        return

                print(f"=== ATTEMPT {attempt + 1} RAW RESPONSE ===")
                print(response.text)
                print("=== END RAW RESPONSE ===")

                refined_text = self.extract_json_from_response(response.text)

                print(f"=== EXTRACTED REFINED PROMPT ===")
                print(refined_text)
                print("=== END EXTRACTED ===")

                if refined_text and refined_text.strip():
                    self.finished.emit(refined_text)
                    return
                else:
                    print(f"No valid refined text extracted from response")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue

            except Exception as e:
                error_message = str(e)
                print(f"Attempt {attempt + 1} failed: {error_message}")

                if "list index out of range" in error_message.lower():
                    print(f"List index error - likely empty API key list or invalid configuration")
                    self.error.emit("API configuration error - please check API keys")
                    return
                elif "429" in error_message or "RESOURCE_EXHAUSTED" in error_message or "RATE_LIMIT_EXCEEDED" in error_message:
                    print(f"Rate limit exceeded, rolling to next API key...")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                else:
                    if attempt == self.max_retries - 1:
                        self.error.emit(f"Failed after {self.max_retries} attempts: {error_message}")
                        return
                    else:
                        time.sleep(self.retry_delay)

        self.error.emit(f"All API keys exhausted after {self.max_retries} attempts")
