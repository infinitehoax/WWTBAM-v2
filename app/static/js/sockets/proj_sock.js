// proj_sock.js — Projector / audience big screen socket client
const socket = io();

socket.on('connect', () => {
  console.log('[Projector] Connected:', socket.id);
  socket.emit('projector_connect');
});

socket.on('disconnect', () => {
  console.warn('[Projector] Disconnected');
});

// Full state on (re)connect
socket.on('state_snapshot', (data) => {
  if (window.proj) window.proj.applyStateSnapshot(data);
});

// New question
socket.on('new_question', (data) => {
  if (!window.proj) return;
  window.proj.renderQuestion(data, false, 0);
  window.proj.playSound('suspense');
});

socket.on('timer_started', (data) => {
    if (window.proj) {
        window.proj.startTimer(data.time_limit);
    }
});

// Answer revealed
socket.on('answer_revealed', (data) => {
  if (!window.proj) return;
  window.proj.revealAnswer(data.correct_answer, data.answer_stats, data.leaderboard);
  window.proj.playSound('correct');
  if (data.leaderboard) {
    // Update footer player count
    const count = data.leaderboard.length;
    document.getElementById('player-count').textContent = count;
    document.getElementById('footer-players').textContent = count;
  }
});

// Leaderboard
socket.on('show_leaderboard', (data) => {
  if (window.proj) {
    window.proj.renderLeaderboard(data.leaderboard || []);
    window.proj.playSound('million');
  }
});

// Sound command
socket.on('play_sound', (data) => {
  if (window.proj) window.proj.playSound(data.sound, data.loop);
});

// 50:50
socket.on('lifeline_5050', (data) => {
  if (window.proj) window.proj.apply5050(data.eliminated || []);
});

// Audience poll started
socket.on('audience_poll_started', () => {
  if (window.proj) window.proj.updateAudiencePoll({A:0,B:0,C:0,D:0});
});

// Audience votes update
socket.on('audience_votes_update', (data) => {
  if (window.proj) window.proj.updateAudiencePoll(data.votes);
});

// Phone hint
socket.on('phone_hint', (data) => {
  if (window.proj) window.proj.showPhoneHint(data.hint);
});

// Player joined — show on lobby screen
socket.on('player_joined', (data) => {
  if (window.proj) window.proj.addPlayer(data.sid, data.name);
});

// Player left
socket.on('player_left', (data) => {
  if (window.proj) window.proj.removePlayer(data.sid);
});
socket.on('player_kicked', (data) => {
  if (window.proj) window.proj.removePlayer(data.sid);
});

// Phase change
socket.on('phase_change', (data) => {
  if (window.proj) window.proj.showPhase(data.phase);
});

// Game reset
socket.on('game_reset', () => {
  if (window.proj) window.proj.showPhase('lobby');
});

socket.on('all_players_kicked', () => {
    if (window.proj) {
        // Clear the internal player object
        for (let sid in projPlayers) {
            delete projPlayers[sid];
        }
        // Update the UI
        document.getElementById('player-count').textContent = 0;
        document.getElementById('footer-players').textContent = 0;
        const names = document.getElementById('joining-names');
        if (names) {
            names.innerHTML = '<span style="color:rgba(255,255,255,0.2);font-style:italic;">Waiting for players to join...</span>';
        }
    }
});
