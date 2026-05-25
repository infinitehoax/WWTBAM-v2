"""
Game State Engine — The Brain
Tracks all active game state in memory. Survives socket disconnections.
"""
import threading
import time
import uuid
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
            self.audience_sids = set()
            self.current_friend_sid = None
            self.players = {}              # {sid: {name, score, active, token, is_eliminated}}
            self.room_code = None
            self.sound_command = None      # Last sound triggered by admin
            self.prize_ladder = [
                1000, 2000, 3000, 5000, 7500,
                10000, 15000, 20000, 30000, 50000,
                75000, 150000, 300000, 500000, 1000000
            ]
            self.current_prize_index = -1
            self.safe_havens = [4, 9]  # Indices 4 (₦10k) and 9 (₦50k)
            self.active_set = 'Default Set'

    def add_player(self, sid, name, token=None):
        with self._lock:
            # Check if player with this token already exists
            existing_sid = None
            if token:
                for old_sid, p in self.players.items():
                    if p.get('token') == token:
                        existing_sid = old_sid
                        break
            else:
                # Check by name if no token provided (first time join)
                for old_sid, p in self.players.items():
                    if p['name'] == name and not p.get('active'):
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

                return player_data['token']
            else:
                # New player
                new_token = str(uuid.uuid4())
                self.players[sid] = {
                    'name': name,
                    'score': 0,
                    'correct': 0,
                    'answered': 0,
                    'active': True,
                    'is_eliminated': False,
                    'sid': sid,
                    'token': new_token,
                    'joined_at': datetime.utcnow().isoformat()
                }
                self.lifelines_used[sid] = []
                return new_token

    def remove_player(self, sid):
        with self._lock:
            if sid in self.players:
                self.players[sid]['active'] = False
    def kick_all_players(self):
        with self._lock:
            self.players = {}
            self.answers = {}
            self.lifelines_used = {}


    def add_audience(self, sid):
        with self._lock:
            self.audience_sids.add(sid)

    def remove_audience(self, sid):
        with self._lock:
            if sid in self.audience_sids:
                self.audience_sids.remove(sid)
            if self.current_friend_sid == sid:
                self.current_friend_sid = None

    def pick_random_friend(self):
        import random
        with self._lock:
            if not self.audience_sids:
                return None
            candidates = list(self.audience_sids)
            self.current_friend_sid = random.choice(candidates)
            return self.current_friend_sid

    def set_question(self, question_dict, index):
        with self._lock:
            self.current_question = question_dict
            self.current_q_index = index
            self.current_friend_sid = None
            self.answers = {}
            self.eliminated_options = []
            self.audience_votes = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
            self.audience_poll_active = False
            self.timer_started_at = None  # Don't start timer yet
            self.time_limit = question_dict.get('time_limit', 30)
            self.phase = 'question'
            if index < len(self.prize_ladder):
                self.current_prize_index = index

    def start_timer(self):
        with self._lock:
            if self.phase == 'question' and self.timer_started_at is None:
                self.timer_started_at = time.time()
                return True
        return False

    def record_answer(self, sid, answer):
        with self._lock:
            # Cannot answer if timer hasn't started or already expired
            if self.timer_started_at is None:
                return False

            elapsed = time.time() - self.timer_started_at
            if elapsed > self.time_limit:
                return False

            # Eliminated players cannot answer
            if self.players.get(sid, {}).get('is_eliminated'):
                return False

            if sid not in self.answers:
                self.answers[sid] = {
                    'answer': answer,
                    'locked': True,
                    'time': elapsed
                }
                return True
            return False

    def get_time_remaining(self):
        if self.timer_started_at is None:
            return self.time_limit
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
            self.phase = 'reveal'
            self.audience_poll_active = False
            self.current_friend_sid = None
            # Reset last results for all players
            for p in self.players.values():
                p["last_answer"] = None
                p["is_correct_last"] = False

            # Update scores for players who were not already eliminated
            for sid, p in self.players.items():
                if not p.get('active') or p.get('is_eliminated'):
                    continue

                # Check if they answered this question
                ans_data = self.answers.get(sid)
                if ans_data:
                    p['last_answer'] = ans_data['answer']
                    p['answered'] += 1
                    if ans_data['answer'] == correct_answer:
                        # Correct: set score to current prize level
                        p['score'] = self.prize_ladder[self.current_q_index]
                        p['correct'] += 1
                        p['is_correct_last'] = True
                    else:
                        # Wrong: Eliminated! Drop to safe haven
                        p['is_eliminated'] = True
                        p['score'] = self._get_safe_haven_value(self.current_q_index)
                        p['is_correct_last'] = False
                else:
                    # Didn't answer: In WWTBAM this is like getting it wrong if the timer is up
                    p['is_eliminated'] = True
                    p['score'] = self._get_safe_haven_value(self.current_q_index)
                    p['is_correct_last'] = False

    def _get_safe_haven_value(self, q_index):
        if q_index < 4:
            return 0
        elif q_index < 9:
            return self.prize_ladder[4]
        else:
            return self.prize_ladder[9]

    def get_leaderboard(self):
        players = [p for p in self.players.values() if p.get('active')]
        # Sort by score primarily, then by number of correct answers
        sorted_players = sorted(players, key=lambda x: (x['score'], x['correct']), reverse=True)
        # Add formatted score to each player dict for the UI
        for p in sorted_players:
            p['score_formatted'] = self.format_naira(p['score'])
        return sorted_players

    def format_naira(self, amount):
        return f"₦{amount:,}"

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

            prize_ladder_formatted = [self.format_naira(p) for p in self.prize_ladder]

            # Prepare players with formatted scores
            player_list = []
            for p in self.players.values():
                pd = p.copy()
                pd['score_formatted'] = self.format_naira(p['score'])
                player_list.append(pd)

            return {
                'phase': self.phase,
                'current_question': self.current_question,
                'current_q_index': self.current_q_index,
                'time_remaining': self.get_time_remaining(),
                'timer_started': self.timer_started_at is not None,
                'eliminated_options': self.eliminated_options,
                'audience_poll_active': self.audience_poll_active,
                'audience_votes': self.audience_votes if self.audience_poll_active else None,
                'players': player_list,
                'current_prize': self.format_naira(self.prize_ladder[self.current_prize_index]) if self.current_prize_index >= 0 else None,
                'prize_ladder': prize_ladder_formatted,
                'safe_havens': self.safe_havens,
                'my_answer': my_answer,
                'my_lifelines': my_lifelines,
                'is_friend': sid == self.current_friend_sid if sid else False
            }


# Singleton
game_state = GameState()
