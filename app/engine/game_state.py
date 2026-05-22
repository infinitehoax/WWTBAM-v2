"""
Game State Engine — The Brain
Tracks all active game state in memory. Survives socket disconnections.
"""
import threading
import time
from datetime import datetime


class GameState:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.phase = 'lobby'           # lobby | question | reveal | leaderboard | ended
            self.current_question = None   # Full question dict
            self.current_q_index = -1
            self.question_order = []       # List of question IDs for this session
            self.timer_started_at = None
            self.time_limit = 30
            self.answers = {}              # {sid: {'answer': 'A', 'locked': True, 'time': float}}
            self.lifelines_used = {}       # {sid: ['5050', 'audience']}
            self.eliminated_options = []   # For 50:50: options to hide ['B', 'C']
            self.audience_votes = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
            self.audience_poll_active = False
            self.players = {}              # {sid: {name, score, active}}
            self.room_code = None
            self.sound_command = None      # Last sound triggered by admin
            self.prize_ladder = [
                '₦1,000', '₦2,000', '₦3,000', '₦5,000', '₦7,500',
                '₦10,000', '₦15,000', '₦20,000', '₦30,000', '₦50,000',
                '₦75,000', '₦150,000', '₦300,000', '₦500,000', '₦1,000,000'
            ]
            self.current_prize_index = -1
            self.safe_havens = [4, 9]  # Indices 4 (₦10k) and 9 (₦50k)

    def add_player(self, sid, name):
        with self._lock:
            # Check if player name already existed
            existing_sid = None
            for old_sid, p in self.players.items():
                if p['name'] == name:
                    existing_sid = old_sid
                    break

            if existing_sid is not None:
                # Reconnect: transfer state
                player_data = self.players.pop(existing_sid)
                player_data['sid'] = sid
                player_data['active'] = True
                self.players[sid] = player_data
                
                # Transfer lifelines
                if existing_sid in self.lifelines_used:
                    self.lifelines_used[sid] = self.lifelines_used.pop(existing_sid)
                else:
                    self.lifelines_used[sid] = []

                # Transfer answers
                if existing_sid in self.answers:
                    self.answers[sid] = self.answers.pop(existing_sid)
            else:
                # New player
                self.players[sid] = {
                    'name': name,
                    'score': 0,
                    'correct': 0,
                    'answered': 0,
                    'active': True,
                    'sid': sid,
                    'joined_at': datetime.utcnow().isoformat()
                }
                self.lifelines_used[sid] = []

    def remove_player(self, sid):
        with self._lock:
            if sid in self.players:
                self.players[sid]['active'] = False

    def set_question(self, question_dict, index):
        with self._lock:
            self.current_question = question_dict
            self.current_q_index = index
            self.answers = {}
            self.eliminated_options = []
            self.audience_votes = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
            self.audience_poll_active = False
            self.timer_started_at = time.time()
            self.time_limit = question_dict.get('time_limit', 30)
            self.phase = 'question'
            if index < len(self.prize_ladder):
                self.current_prize_index = index

    def record_answer(self, sid, answer):
        with self._lock:
            if sid not in self.answers:
                elapsed = time.time() - (self.timer_started_at or time.time())
                self.answers[sid] = {
                    'answer': answer,
                    'locked': True,
                    'time': elapsed
                }
                return True
            return False

    def get_time_remaining(self):
        if self.timer_started_at is None:
            return 0
        elapsed = time.time() - self.timer_started_at
        return max(0, self.time_limit - elapsed)

    def get_answer_stats(self):
        counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for data in self.answers.values():
            ans = data.get('answer')
            if ans in counts:
                counts[ans] += 1
        return counts

    def apply_5050(self, correct_answer):
        """Remove two wrong answers, keep correct + one random wrong."""
        import random
        wrong = [o for o in ['A', 'B', 'C', 'D'] if o != correct_answer]
        to_remove = random.sample(wrong, 2)
        with self._lock:
            self.eliminated_options = to_remove
        return to_remove

    def start_audience_poll(self):
        with self._lock:
            self.audience_poll_active = True
            self.audience_votes = {'A': 0, 'B': 0, 'C': 0, 'D': 0}

    def vote_audience(self, option):
        with self._lock:
            if self.audience_poll_active and option in self.audience_votes:
                self.audience_votes[option] += 1

    def reveal_answer(self, correct_answer):
        with self._lock:
            self.phase = "reveal"
            # Reset last results for all players
            for p in self.players.values():
                p["last_answer"] = None
                p["is_correct_last"] = False

            # Update scores and record results
            for sid, data in self.answers.items():
                if sid in self.players:
                    ans = data["answer"]
                    self.players[sid]["last_answer"] = ans
                    self.players[sid]["answered"] += 1
                    if ans == correct_answer:
                        pts = (self.current_q_index + 1) * 100
                        self.players[sid]["score"] += pts
                        self.players[sid]["correct"] += 1
                        self.players[sid]["is_correct_last"] = True
                    else:
                        self.players[sid]["is_correct_last"] = False

    def get_leaderboard(self):
        players = [p for p in self.players.values() if p.get('active')]
        return sorted(players, key=lambda x: x['score'], reverse=True)

    def get_snapshot(self, sid=None):
        """Full state snapshot for reconnecting clients."""
        with self._lock:
            my_answer = None
            my_lifelines = []
            if sid is not None:
                if sid in self.answers:
                    my_answer = self.answers[sid]
                if sid in self.lifelines_used:
                    my_lifelines = self.lifelines_used[sid]

            return {
                'phase': self.phase,
                'current_question': self.current_question,
                'current_q_index': self.current_q_index,
                'time_remaining': self.get_time_remaining(),
                'eliminated_options': self.eliminated_options,
                'audience_poll_active': self.audience_poll_active,
                'audience_votes': self.audience_votes if self.audience_poll_active else None,
                'players': list(self.players.values()),
                'current_prize': self.prize_ladder[self.current_prize_index] if self.current_prize_index >= 0 else None,
                'prize_ladder': self.prize_ladder,
                'safe_havens': self.safe_havens,
                'my_answer': my_answer,
                'my_lifelines': my_lifelines,
            }


# Singleton
game_state = GameState()
