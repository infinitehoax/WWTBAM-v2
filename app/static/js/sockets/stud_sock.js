// stud_sock.js — Student podium socket client
const socket = io();

socket.on('connect', () => {
    console.log('[Student] Connected:', socket.id);
    const token = sessionStorage.getItem('session_token');
    const name = sessionStorage.getItem('playerName') || 'Student';
    const room = sessionStorage.getItem('roomCode') || '';
    socket.emit('student_join', { name, room_code: room, token });
});

socket.on('join_success', (data) => {
    if (data.token) {
        sessionStorage.setItem('session_token', data.token);
    }
});

socket.on('join_error', (data) => {
    alert(data.msg);
    window.location.href = '/play';
});

socket.on('state_snapshot', (data) => {
    if (window.podium) {
        window.podium.setScore(data.players.find(p => p.sid === socket.id)?.score_formatted || '₦0');
        window.podium.setPrize(data.current_prize);

        if (data.phase === 'question' && data.current_question) {
            window.podium.renderQuestion(data.current_question, data.time_remaining, data.timer_started);
            if (data.my_answer) {
                window.podium.restoreAnswer(data.my_answer.answer);
            }
        } else if (data.phase === 'lobby') {
            window.podium.showScreen('waiting');
        }

        // Restore lifelines
        if (data.my_lifelines) {
            data.my_lifelines.forEach(ll => window.podium.setLifelineUsed(ll));
        }

        // Restore poll
        if (data.audience_poll_active && data.audience_votes) {
            window.podium.updateAudiencePoll(data.audience_votes);
        }
    }
});

socket.on('new_question', (data) => {
    if (window.podium) {
        window.podium.renderQuestion(data, data.time_limit, false);
        window.podium.setPrize(data.prize);
    }
});

socket.on('timer_started', (data) => {
    if (window.podium) {
        window.podium.startTimer(data.time_limit);
    }
});

socket.on('answer_locked', (data) => {
    // Already handled locally by UI, but good to have
});

socket.on('answer_revealed', (data) => {
    if (window.podium) {
        window.podium.showAnswerResult(data.correct_answer);
    }
});

socket.on('show_leaderboard', (data) => {
    if (window.podium) {
        window.podium.showLeaderboard(data.leaderboard);
    }
});

socket.on('lifeline_5050', (data) => {
    if (window.podium) {
        window.podium.apply5050(data.eliminated);
    }
});

socket.on('audience_poll_started', (data) => {
    // Just show empty bars
    if (window.podium) {
        window.podium.updateAudiencePoll({'A':0,'B':0,'C':0,'D':0});
    }
});

socket.on('audience_votes_update', (data) => {
    if (window.podium) {
        window.podium.updateAudiencePoll(data.votes);
    }
});

socket.on('friend_called', (data) => {
    if (window.podium) {
        if (data.success) {
            window.podium.showHint("Calling an audience member... Please wait.");
        } else {
            alert(data.msg || "Failed to call a friend.");
        }
    }
});

socket.on('lifeline_phone_answer', (data) => {
    if (window.podium) {
        window.podium.showHint(`Your friend suggests: ${data.answer}`);
    }
});

socket.on('phone_hint', (data) => {
    if (window.podium) {
        window.podium.showHint(data.hint);
    }
});

socket.on('player_left', (data) => {
    // Can ignore
});

socket.on('game_reset', () => {
    window.location.reload();
});

socket.on('player_kicked', (data) => {
    if (data.sid === socket.id) {
        sessionStorage.clear();
        window.location.href = '/play';
    }
});

socket.on('all_players_kicked', () => {
    sessionStorage.clear();
    window.location.href = '/play';
});
