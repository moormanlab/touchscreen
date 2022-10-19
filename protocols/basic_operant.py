from touchscreen_protocol import Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED, tTone, tsColors

ir_tone = tTone(frequency = 2000, duration = 0.2, amplitude = 0.03) # tone when ir is broken
screen_tone_good = tTone(frequency = 2000, duration = 0.2, amplitude = 0.03) # tone when reward is triggered by touch
# screen_tone_bad = tTone(frequency = 4000, duration = 0.2, amplitude = 0.03) # tone for bad touches
reward_size = 1 # 10 ul

class Operant(Protocol):
	"""
	When the subject touches the square, the ability to get a reward is unlocked for 5 seconds, and a tone is played.
	The square will disapear during the 20 seconds the reward is available.
	when the subject breaks the ir beam, a reward is dispensed, a new square will spawn, 
	and the window to touch the screen will reset
	"""
	def init(self):
		self.csvlogger.configure(['datetime', 'runtime', 'info', 'x', 'y', 'reward_count', 'rewards_missed', 'no_rewards'], replace=True)
		self.csvlogger.start()
		self.liqrew.set_drop_amount(reward_size)
		self.csvlogger.log(info=f'{type(self).__name__} started, reward set to {reward_size*10} ul')
		self.reward_count = 0
		self.rewards_missed = 0
		self.no_rewards = 0
		self._reward_available = False
		self._duration = None
		self._start = self.now()
		width, height = self.screen.get_size()
		self.square_kwargs = {'color': (255, 255, 255), 'center': (width//3, 3*height//4), 'size': (int(height*0.25), int(height*0.25))}
		self.blank_square_kwargs = self.square_kwargs.copy()
		self.blank_square_kwargs['color'] = (0, 0, 0)
		self.frame_kwargs = {'color': (255, 255, 255), 'center': (width//3, 3*height//4), 'size': (int(height*0.25)+10, int(height*0.25)+10)}
		

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

		if self.reward_available():
			self.liqrew.drop()
			self.reward_count += 1
			self.csvlogger.log(info='subject entered well: reward given', reward_count=self.reward_count)
			self.sound.play(ir_tone)
			self.cancel_reward()
		else:
			self.no_rewards += 1
			self.csvlogger.log(info='subject entered well: no reward', no_rewards=self.no_rewards)


	def sensor_handler_out(self):
		self.csvlogger.log(info='subject left well')

	def main(self, event):
		self.frame = self.draw.rect(**self.frame_kwargs)
		if self.reward_missed():
			self.rewards_missed += 1
			self.csvlogger.log(info='reward missed', rewards_missed=self.rewards_missed)
			self.cancel_reward()

		if not self.reward_available():
			self.draw.rect(**self.blank_square_kwargs)
			
		
		if not self.reward_available() and event.type == POINTERPRESSED and self.frame.collidepoint(event.position):
			self.allow_reward(5)
			self.sound.play(screen_tone_good)
			self.draw.rect(**self.square_kwargs)
			self.csvlogger.log(info='pointer pressed', x=event.position[0], y=event.position[1])
		elif event.type == POINTERPRESSED and self.frame.collidepoint(event.position):
			self.csvlogger.log(info='invalid press', x=event.position[0], y=event.position[1])
		self.screen.update()

	def end(self):
		self.csvlogger.log(event='Training ended', reward_count=self.reward_count, rewards_missed=self.rewards_missed, no_rewards=self.no_rewards)


