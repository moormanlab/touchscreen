from touchscreen_protocol import Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED, tTone, tsColors

ir_tone = tTone(frequency = 2000, duration = 0.2, amplitude = 0.03) # tone when ir is broken
screen_tone_good = tTone(frequency = 2000, duration = 0.2, amplitude = 0.03) # tone when reward is triggered by touch
# screen_tone_bad = tTone(frequency = 4000, duration = 0.2, amplitude = 0.03) # tone for bad touches
reward_size = 1 # 10 ul

class Operant(Protocol):
	"""
	When the subject touches the square, the ability to get a reward is unlocked for 20 seconds, and a tone is played.
	The square will disapear during the 20 seconds the reward is available.
	when the subject breaks the ir beam, a reward is dispensed, a new square will randomly spawn, 
	and the window to touch the screen will reset
	"""
	def init(self):
		self.csvlogger.configure(['reward_count', 'rewards_missed', 'no_rewards'])
		self.csvlogger.start()
		self.liqrew.set_drop_amount(reward_size)
		self.csvlogger.log(event=f'{type(self).__name__} started, reward set to {reward_size*10} ul')
		self.reward_count = 0
		self.rewards_missed = 0
		self.no_rewards = 0
		self._reward_available = False
		self._duration = None
		self._start = self.now()
		width, height = self.screen.get_size()
		self.square_kwargs = {'color': (0, 65, 65), 'center': (width//3, 3*height//4), 'size': (int(height*0.25), int(height*0.25))}
	
	def allow_reward(self, duration):
		if not self._reward_available:
			self._reward_available = True
			self._duration = duration
			self._start = self.now()

	def cancel_reward(self):
		self._duration = None
		self._reward_available = False

	def reward_available(self):
		if self._duration != None:
			return self.now() - self._start <= self._duration 
		return False
	def reward_missed(self):
		if self._duration != None:
			self._reward_available = self.now() - self._start <= self._duration
			return not self._reward_available
		return False

	def sensor_handler_in(self):
		self.csvlogger.log(event='subject entered well')
		if self.reward_available():
			self.liqrew.drop()
			self.reward_count += 1
			self.csvlogger.log(event='reward given', reward_count=self.reward_count)
			self.sound.play(ir_tone)
			self.cancel_reward()
		else:
			self.no_rewards += 1
			self.csvlogger.log(event='no reward', no_rewards=self.no_rewards)


	def sensor_handler_out(self):
		self.csvlogger.log(event='subject left well')

	def main(self, event):
		if self.reward_missed():
			self.rewards_missed += 1
			self.csvlogger.log(event='reward missed', rewards_missed=self.rewards_missed)
			self.cancel_reward()

		if not self.reward_available():
			self.rect = self.draw.rect(**self.square_kwargs)

		if not self.reward_available() and event.type == POINTERPRESSED and self.rect.collidepoint(event.position):
			self.allow_reward(20)
			self.sound.play(screen_tone_good)
			self.screen.clean()

		self.screen.update()

	def end(self):
		self.csvlogger.log(event='Training ended', reward_count=self.reward_count, rewards_missed=self.rewards_missed, no_rewards=self.no_rewards)



	