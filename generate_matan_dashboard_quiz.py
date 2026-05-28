import json
import re
import random

random.seed(42)

with open('/Users/yaroslavyarik/Project/myau/matan_ocr.json', 'r', encoding='utf-8') as f:
    matan_data = json.load(f)

quiz_data = []

for sec_idx, sec in enumerate(matan_data):
    topic_id = f"topic_{sec_idx+1}"
    title = sec.get('title', f"Раздел {sec_idx+1}")
    
    questions = []
    blocks = [b for b in sec.get('blocks', []) if b.get('type') in ['Определение', 'Теорема', 'Следствие', 'Лемма']]
    
    # We need at least 3-4 questions per topic if possible
    # We will pick a subset of blocks to form questions
    selected_blocks = random.sample(blocks, min(len(blocks), 6))
    
    for block in selected_blocks:
        text = block.get('content', '')
        # Split into sentences to form a question and answer
        sentences = re.split(r'(?<=[.?!])\s+', text)
        if len(sentences) < 2:
            # If it's a single sentence, make the question "Что гласит ..." or mask a part of it.
            # But the simplest is to just split by comma if no periods, or just skip it if it's too short
            if len(text) > 30 and ',' in text:
                parts = text.split(',', 1)
                q_text = parts[0] + "..."
                correct = parts[1].strip()
            else:
                continue
        else:
            q_text = sentences[0]
            correct = ' '.join(sentences[1:])
        
        # We need 3 wrong answers. We can pick from other blocks in the entire dataset
        wrong_answers = []
        all_blocks = [b.get('content', '') for s in matan_data for b in s.get('blocks', []) if b.get('type') in ['Определение', 'Теорема', 'Следствие', 'Лемма']]
        random.shuffle(all_blocks)
        
        for w_text in all_blocks:
            if w_text == text: continue
            w_sentences = re.split(r'(?<=[.?!])\s+', w_text)
            wrong_opt = ' '.join(w_sentences[1:]) if len(w_sentences) > 1 else w_text
            if len(wrong_opt) > 10 and wrong_opt not in wrong_answers and wrong_opt != correct:
                wrong_answers.append(wrong_opt[:120] + "..." if len(wrong_opt) > 120 else wrong_opt)
            if len(wrong_answers) == 3:
                break
        
        # Just in case we didn't find enough
        while len(wrong_answers) < 3:
            wrong_answers.append("Утверждение неверно")
            
        options = [correct[:120] + "..." if len(correct) > 120 else correct] + wrong_answers
        random.shuffle(options)
        correct_idx = options.index(correct[:120] + "..." if len(correct) > 120 else correct)
        
        questions.append({
            "question": q_text.replace('"', '\\"').replace('\n', ' '),
            "options": [o.replace('"', '\\"').replace('\n', ' ') for o in options],
            "correct": correct_idx
        })
    
    if questions:
        quiz_data.append({
            "id": topic_id,
            "title": title.replace('"', '\\"'),
            "questions": questions
        })

print("Generated Topics:", len(quiz_data))
for q in quiz_data[:2]:
    print(q["title"], len(q["questions"]), "questions")

# Format to JS string
js_out = "const quizData = [\n"
for topic in quiz_data:
    js_out += f'    {{\n        id: "{topic["id"]}",\n        title: "{topic["title"]}",\n        questions: [\n'
    for q in topic["questions"]:
        js_out += f'            {{\n                question: "{q["question"]}",\n'
        js_out += f'                options: [\n'
        for opt in q["options"]:
            js_out += f'                    "{opt}",\n'
        js_out += f'                ],\n'
        js_out += f'                correct: {q["correct"]}\n            }},\n'
    js_out += "        ]\n    },\n"
js_out += "];\n"

with open('matan_quiz_data.js', 'w', encoding='utf-8') as f:
    f.write(js_out)
print("Saved to matan_quiz_data.js")
