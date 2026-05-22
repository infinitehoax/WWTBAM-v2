// stud_sock.js — Student podium socket client
const socket = io();

// Join on connect
socket.on('connect', () => {
  console.log('[Student] Connected:', socket.id);
  const name = sessionStorage.getItem('playerName');
  if (!name) { window.location.href = '/play'; return; }
  socket.emit('student_join', { name });
});

socket.on('disconnect', () => {
  console.warn('[Student] Disconnected — will reconnect...');
});

// Server sends current state on (re)connect
socket.on('state_snapshot', (data) => {
  if (!window.podium) return;
  const phase = data.phase || 'lobby';
  const myName = sessionStorage.getItem('playerName');

  // Restore score from players list
  if (data.players && myName) {
    const me = data.players.find(p => p.name === myName);
    if (me) window.podium.setScore(me.score || 0);
  }

  // Restore lifelines used
  if (data.my_lifelines && data.my_lifelines.length) {
    data.my_lifelines.forEach(ll => window.podium.setLifelineUsed(ll));
  }

  // Restore prize label
  if (data.current_prize) window.podium.setPrize(data.current_prize);

  if (phase === 'question' && data.current_question) {
    // Render the question, resuming from current server time
    window.podium.renderQuestion(data.current_question, data.time_remaining);
    // Restore 50:50 if already applied
    if (data.eliminated_options && data.eliminated_options.length) {
      window.podium.apply5050(data.eliminated_options);
    }
    // Restore locked-in answer if player had already answered
    if (data.my_answer && data.my_answer.answer) {
      window.podium.restoreAnswer(data.my_answer.answer);
    }
    // Restore audience poll if active
    if (data.audience_poll_active && data.audience_votes) {
      window.podium.updateAudiencePoll(data.audience_votes);
    }

  } else if (phase === 'reveal' && data.current_question) {
    // Show the question with answer highlighted
    window.podium.renderQuestion(data.current_question, 0);
    if (data.eliminated_options && data.eliminated_options.length) {
      window.podium.apply5050(data.eliminated_options);
    }
    if (data.my_answer && data.my_answer.answer) {
      window.podium.restoreAnswer(data.my_answer.answer);
    }
    // Show correct answer reveal immediately
    const correctAnswer = data.current_question.correct_answer;
    if (correctAnswer) {
      window.podium.showAnswerResult(correctAnswer);
    }

  } else if (phase === 'leaderboard') {
    const lb = (data.players || [])
      .filter(p => p.active)
      .sort((a, b) => (b.score || 0) - (a.score || 0));
    window.podium.showLeaderboard(lb);

  } else {
    window.podium.showScreen('waiting');
  }
});

// New question pushed
socket.on('new_question', (data) => {
  if (window.podium) {
    window.podium.renderQuestion(data);
    window.podium.setPrize(data.prize);
  }
});

// Answer locked in (confirmed by server)
socket.on('answer_locked', (data) => {
  console.log('[Student] Answer locked:', data.answer);
});

// Answer revealed — update score from leaderboard
socket.on('answer_revealed', (data) => {
  if (!window.podium) return;
  window.podium.showAnswerResult(data.correct_answer);
  // Update our score from the leaderboard
  const myName = sessionStorage.getItem('playerName');
  if (myName && data.leaderboard) {
    const me = data.leaderboard.find(p => p.name === myName);
    if (me) window.podium.setScore(me.score || 0);
  }
});

// Leaderboard — update score too
socket.on('show_leaderboard', (data) => {
  if (!window.podium) return;
  const lb = data.leaderboard || [];
  window.podium.showLeaderboard(lb);
  // Update our score
  const myName = sessionStorage.getItem('playerName');
  if (myName) {
    const me = lb.find(p => p.name === myName);
    if (me) window.podium.setScore(me.score || 0);
  }
});

// 50:50 lifeline
socket.on('lifeline_5050', (data) => {
  if (window.podium) {
    window.podium.apply5050(data.eliminated || []);
    window.podium.setLifelineUsed('5050');
  }
});

// Audience poll started
socket.on('audience_poll_started', () => {
  if (window.podium) window.podium.setLifelineUsed('audience');
});

// Audience poll update
socket.on('audience_votes_update', (data) => {
  if (window.podium) window.podium.updateAudiencePoll(data.votes);
});

// Phone hint
socket.on('phone_hint', (data) => {
  if (window.podium) {
    window.podium.showHint(data.hint);
    window.podium.setLifelineUsed('phone');
  }
});

// Kicked
socket.on('player_kicked', (data) => {
  if (data.sid === socket.id) {
    sessionStorage.removeItem('playerName');
    window.location.href = '/play';
  }
});

// Game reset
socket.on('game_reset', () => {
  if (window.podium) {
    window.podium.setScore(0);
    window.podium.showScreen('waiting');
  }
});

// Phase change
socket.on('phase_change', (data) => {
  if (data.phase === 'lobby' && window.podium) window.podium.showScreen('waiting');
});
