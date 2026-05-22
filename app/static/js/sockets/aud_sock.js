// aud_sock.js — Audience voting socket client
const socket = io();

socket.on('connect', () => {
  console.log('[Audience] Connected:', socket.id);
  socket.emit('audience_join');
});

socket.on('audience_init', (data) => {
  if (window.audienceUI) {
    window.audienceUI.showPoll(data.poll_active, data.question);
    if (data.votes) {
      window.audienceUI.updateBars(data.votes);
    }
    if (data.is_friend && data.question) {
        window.audienceUI.showFriendCall(data.question, 'The contestant');
    }
  }
});

socket.on('audience_poll_started', (data) => {
  if (window.audienceUI) {
      window.audienceUI.showPoll(true, data.question);
  }
});

socket.on('audience_votes_update', (data) => {
  if (window.audienceUI) {
    window.audienceUI.updateBars(data.votes);
  }
});

socket.on('you_are_the_friend', (data) => {
    if (window.audienceUI) {
        window.audienceUI.showFriendCall(data.question, data.student_name);
    }
});

socket.on('new_question', (data) => {
  if (window.audienceUI) {
    window.audienceUI.showPoll(false);
    window.audienceUI.hideFriendCall();
  }
});

socket.on('answer_revealed', () => {
    if (window.audienceUI) {
        window.audienceUI.showPoll(false);
        window.audienceUI.hideFriendCall();
    }
});

socket.on('game_reset', () => {
    if (window.audienceUI) {
        window.audienceUI.showPoll(false);
        window.audienceUI.hideFriendCall();
    }
});
