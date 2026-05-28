import re

with open('index_matan.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('matan_quiz_data.js', 'r', encoding='utf-8') as f:
    quiz_data_js = f.read()

with open('discrete_quiz_html.txt', 'r', encoding='utf-8') as f:
    discrete_quiz_html = f.read()

# 1. Replace the quiz HTML
old_html_pattern = r'<section class="quiz-section" id="quiz">.*?</section>'
# We only want the HTML part from discrete_quiz_html.txt, not the script part.
discrete_html_only = discrete_quiz_html.split('<script>')[0].strip()

# Adjust wording for matan
discrete_html_only = discrete_html_only.replace('<div id="quiz-section">', '<section class="quiz-section" id="quiz">\n<span class="section-num">Проверка знаний</span>')
discrete_html_only = discrete_html_only + '\n</section>'

# Replace HTML using re, but wrapping repl in lambda to avoid escape issues
html = re.sub(old_html_pattern, lambda m: discrete_html_only, html, flags=re.DOTALL)

# 2. Extract discrete JS logic
# It starts at <script> and ends before <script> // --- NEW FEATURES JS ---
discrete_js = discrete_quiz_html.split('<script>')[1].split('</script>')[0].strip()
# remove the quizData from discrete_js because we have our own
discrete_js_logic = re.sub(r'const quizData = \[.*?\];', '', discrete_js, flags=re.DOTALL).strip()
# adjust localstorage key
discrete_js_logic = discrete_js_logic.replace('graph_quiz_progress', 'matan_quiz_progress')

# Add XP integration into showResults
discrete_js_logic = discrete_js_logic.replace('userProgress[currentTopicId] = score;', '''userProgress[currentTopicId] = score;
            // Add XP for first time passing
            const xpGained = score * 20;
            if (typeof addXP === "function") addXP(xpGained);
            if (score === topic.questions.length && typeof unlockAchievement === "function") unlockAchievement('perfect_quiz');''')

# 3. Replace old JS logic
# Old quizData and logic is from "const quizData = [" to "function restartQuiz() { ... }"
old_js_pattern = r'const quizData = \[\s*\{ category: "Матанализ".*?function restartQuiz\(\) \{.*?\}'
new_js = quiz_data_js + '\n\n' + discrete_js_logic
html = re.sub(old_js_pattern, lambda m: new_js, html, flags=re.DOTALL)

# 4. Remove survival mode logic and overrides (lines ~3392 to 3524)
survival_pattern = r'// Quiz custom mode injection.*?// Initialize script'
html = re.sub(survival_pattern, lambda m: '// Initialize script', html, flags=re.DOTALL)

# 5. Replace `loadQuestion();` in initialization
html = html.replace('loadQuestion();\n        renderXPWidget();', 'initDashboard();\n        renderXPWidget();')

with open('index_matan.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Injected successfully!")
