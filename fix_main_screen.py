import re

with open('app/templates/projector/main_screen.html', 'r') as f:
    content = f.read()

# Replace the whole revealAnswer function with a clean version
new_reveal_answer = """
// ── Reveal answer ─────────────────────────────────────────
function revealAnswer(correct, stats, lb) {
  clearInterval(timerInterval);
  ['A','B','C','D'].forEach(l => {
    const el = document.getElementById('proj-opt-' + l);
    if (!el) return;
    el.classList.remove('pulse-on');
    if (l === correct) el.classList.add('correct');
    else el.classList.add('wrong');
  });
  // Show distribution
  if (stats) {
    const total = Object.values(stats).reduce((a,b)=>a+b,0);
    if (total > 0) {
      document.getElementById('answer-dist').classList.add('show');
      ['A','B','C','D'].forEach(l => {
        const pct = Math.round((stats[l]||0)/total*100);
        const px = Math.max(4, Math.round(pct/100*44));
        document.getElementById('db-'+l).style.height = px+'px';
        document.getElementById('dp-'+l).textContent = pct+'%';
      });
    }
  }
  // Million dollar confetti
  if (correct && document.getElementById('proj-q-num').textContent === 'Q15') {
    launchConfetti();
  }

  // Populate results overlay
  if (lb) {
    const correctList = document.getElementById('results-correct-list');
    const wrongList = document.getElementById('results-wrong-list');
    if (correctList && wrongList) {
      correctList.innerHTML = '';
      wrongList.innerHTML = '';

      lb.forEach((p, i) => {
        const chip = document.createElement('div');
        chip.className = 'result-chip ' + (p.is_correct_last ? 'is-correct' : 'is-wrong');
        chip.style.animationDelay = (i * 0.05) + 's';
        chip.textContent = p.name;
        if (p.is_correct_last) {
          correctList.appendChild(chip);
        } else {
          wrongList.appendChild(chip);
        }
      });
      setTimeout(() => {
        document.getElementById('results-overlay').classList.add('show');
      }, 1500);
    }
  }
}
"""

pattern = r'// ── Reveal answer ──+.*?// ── Leaderboard'
content = re.sub(pattern, new_reveal_answer + "\n\n// ── Leaderboard", content, flags=re.DOTALL)

with open('app/templates/projector/main_screen.html', 'w') as f:
    f.write(content)
