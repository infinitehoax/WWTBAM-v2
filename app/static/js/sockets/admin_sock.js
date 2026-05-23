// admin_sock.js — Admin control room socket client
const socket = io();

socket.on('connect', () => {
  console.log('[Admin] Connected:', socket.id);
  socket.emit('admin_get_state');
});

socket.on('disconnect', () => {
  console.warn('[Admin] Disconnected');
});

socket.on('player_joined', (data) => {
  if (window.onPlayerJoined) window.onPlayerJoined(data);
});

socket.on('player_left', (data) => {
  if (window.onPlayerLeft) window.onPlayerLeft(data);
});

socket.on('player_kicked', (data) => {
  if (window.onPlayerLeft) window.onPlayerLeft(data);
});

socket.on('admin_spy_update', (data) => {
  if (window.onAdminSpyUpdate) window.onAdminSpyUpdate(data);
});

socket.on('new_question', (data) => {
  if (window.onNewQuestion) window.onNewQuestion(data);
});

socket.on('timer_started', (data) => {
  if (window.onTimerStarted) window.onTimerStarted(data);
});

socket.on('answer_revealed', (data) => {
  if (window.onAnswerRevealed) window.onAnswerRevealed(data);
});

socket.on('show_leaderboard', (data) => {
  if (window.onShowLeaderboard) window.onShowLeaderboard(data);
});

socket.on('state_snapshot', (data) => {
  if (window.onStateSnapshot) window.onStateSnapshot(data);
});

socket.on('game_reset', () => {
  if (window.onGameReset) window.onGameReset();
});

socket.on('admin_error', (data) => {
  console.error('[Admin Error]', data.msg);
  if (window.toast) window.toast(data.msg, true);
});

socket.on('all_players_kicked', () => {
    if (window.onAllPlayersKicked) window.onAllPlayersKicked();
});
