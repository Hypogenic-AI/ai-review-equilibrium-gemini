import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ReviewerAgent:
    def __init__(self, model_name, name, system_prompt=None):
        self.model_name = model_name
        self.name = name
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_KEY") or os.getenv("OPENROUTER_API_KEY"),
        )
        self.system_prompt = system_prompt or "You are an expert reviewer for ICLR, a top-tier machine learning conference."
        
    def review(self, paper_text):
        prompt = f"""
Please review the following paper text.
Focus on novelty, significance, soundness, and clarity.

PAPER TEXT:
{paper_text}

Provide your review in strict JSON format with the following keys:
- \"summary\": A brief summary of the paper.
- \"strengths\": A list of key strengths.
- \"weaknesses\": A list of key weaknesses.
- \"score\": An integer score from 1 (Strong Reject) to 10 (Strong Accept).
- \"decision\": \"Accept\" or \"Reject\".
- \"reasoning\": Your main argument for the score.

JSON Output:
"""
        response = self._call_api(prompt)
        return self._parse_json(response)

    def update_review(self, paper_text, previous_review, other_reviews):
        other_reviews_text = ""
        for i, r in enumerate(other_reviews):
            other_reviews_text += f"\n--- Reviewer {i+1} ---\nScore: {r.get('score')}\nArgument: {r.get('reasoning')}\n"

        prompt = f"""
You previously reviewed this paper and gave it a score of {previous_review.get('score')}.

Here are reviews from other experts:
{other_reviews_text}

Please re-evaluate the paper. You should consider their arguments.
If they raise valid points you missed, adjust your score and reasoning.
If you disagree, explain why and maintain your position.

Provide your UPDATED review in strict JSON format (same structure as before).
"""
        response = self._call_api(prompt)
        return self._parse_json(response)

    def _call_api(self, user_prompt):
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7, # Some creativity but not too wild
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"API Error for {self.name}: {e}")
            return "{}"

    def _parse_json(self, response_text):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: try to find JSON block
            try:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end != -1:
                    return json.loads(response_text[start:end])
            except:
                pass
            print(f"JSON Parse Error for {self.name}. Response: {response_text[:100]}...")
            return {"score": 5, "decision": "Reject", "reasoning": "Failed to generate review", "summary": "", "strengths": [], "weaknesses": []}
