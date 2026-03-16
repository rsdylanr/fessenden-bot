import aiohttp, html

class TriviaService:
    async def get_question(self, difficulty="easy"):
        # difficulty can be 'easy', 'medium', or 'hard'
        url = f"https://opentdb.com/api.php?amount=1&type=multiple&difficulty={difficulty}"
        
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()
                if data['response_code'] == 0:
                    res = data['results'][0]
                    return {
                        "q": html.unescape(res['question']),
                        "correct": html.unescape(res['correct_answer']),
                        "all": [html.unescape(a) for a in res['incorrect_answers']] + [html.unescape(res['correct_answer'])],
                        "difficulty": res['difficulty']
                    }
                return None