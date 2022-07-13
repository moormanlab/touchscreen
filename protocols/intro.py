from touchscreen_protocol import Protocol, POINTERPRESSED, POINTERMOTION, POINTERRELEASED, tTone, tsColors

ir_tone = tTone(frequency = 2000, duration = 0.2, amplitude = 0.03) # tone when ir is broken
screen_tone = tTone(frequency = 4000, duration = 0.2, amplitude = 0.03) # tone when screen is touched
reward_size = 1 # 10 ul
class ClassicalConditioning(Protocol):
	"""
	STAGE 1
	---
	Every minute, a reward is given (regardless of ir status).
	If the subject breaks the ir beam, they will recieve a reward.
	There is no lockout period for rewards.
	There are no tones and no visual stimuli.
	"""
	def init(self):
		self.csvlogger.configure(header=['reward_count', 'drops_available', 'drops_dispensed'])
		self.csvlogger.start()
		self.liqrew.set_drop_amount(reward_size)
		self.csvlogger.log(event=f'{type(self).__name__} started, reward set to {reward_size*10} ul')
		self.reward_count = 0 # number of times mouse broke ir beam
		self.liqrew.drop()
		self.drops_dispensed = 1 # total number of drops dispensed automatically and my subject
		self.drops_available = 1 # number of drops available at time of ir beam break
		self.timer = self.now()

	def sensor_handler_in(self):
		self.csvlogger.log(event='subject entered well')
		self.liqrew.drop()
		self.reward_count += 1
		self.drops_dispensed += 1
		self.drops_available += 1
		self.csvlogger.log(event='reward accepted', reward_count=self.reward_count, drops_available=self.drops_available)

	def sensor_handler_out(self):
		self.csvlogger.log(event='subject left well')
		self.drops_available = 0

	def main(self, event):
		if self.now() - self.timer >= 60: # give drop ~every minute
			self.liqrew.drop()
			self.timer = self.now()
			self.drops_dispensed += 1
			self.drops_available += 1


	def end(self):
		self.csvlogger.log(event='Training ended', drops_dispensed=self.drops_dispensed, reward_count=self.reward_count, drops_available=self.drops_available)

class ObservationalLearning(Protocol):
	"""
	STAGE 2
	---
	Every time the subject breaks the ir beam, they recieve a reward.
	There is a 1 second lockout period for rewards.
	When the ir beam is broken and a reward is given, a tone will play and the screen will flash.
	"""
	def init(self):
		self.csvlogger.configure(['reward_count'])
		self.csvlogger.start()
		self.liqrew.set_drop_amount(reward_size)
		self.csvlogger.log(event=f'{type(self).__name__} started, reward set to {reward_size*10} ul')
		self.reward_count = 0
		self._lockout = False
		self._duration = None
		width, height = self.screen.get_size()
		self.square_kwargs = {'color': (0, 65, 65), 'center': (width//2, height//2), 'size': (height*0.3, height*0.3)}
		self._start = self.now()
		self.wait = False

	def set_lockout(self, duration):
		if not self._lockout:
			self._duration = duration
			self._lockout = True
			self._start = self.now()

	def is_lockout(self):
		if self._duration != None:
			self._lockout = self.now() - self._start <= self._duration
		return self._lockout

	def sensor_handler_in(self):
		self.csvlogger.log(event='subject entered well')
		if not self.is_lockout():
			self.liqrew.drop()
			self.reward_count += 1
			self.csvlogger.log(event='reward given', reward_count=self.reward_count)
			self.sound.play(ir_tone)
			self.draw.rect(**self.square_kwargs)
			self.screen.update()
			self.wait = True
			self.set_lockout(1)

	def sensor_handler_out(self):
		self.csvlogger.log(event='subject left well')

	def main(self, event):
		if self.wait:
			self.pause(0.2)
			self.screen.clean()
			self.screen.update()
			self.wait = False

	def end(self):
		self.csvlogger.log(event='Training ended', reward_count=self.reward_count)

class OperantConditioningEasy(Protocol):
	"""
	STAGE 3
	---
	Every time the subject touches the screen, a reward is given (regardless of ir status).
	There is a 1 second lockout period for rewards to prevent too much reward/stimuli if subject climbs on screen.
	When the screen is pressed, a tone will play and the screen will flash.
	#When the subject breaks the ir beam after a reward was dispensed, a tone is played??
	"""
	def init(self):
		self.csvlogger.configure(['reward_count', 'drops_available', 'drops_dispensed'])
		self.csvlogger.start()
		self.liqrew.set_drop_amount(reward_size)
		self.csvlogger.log(event=f'{type(self).__name__} started, reward set to {reward_size*10} ul')
		self.last_press_time = 0
		self.reward_count = 0
		self.drops_dispensed = 0
		self.drops_available = 0
		self.rect_start_time = 0
		width, height = self.screen.get_size()
		self.square_kwargs = {'color': (0, 65, 65), 'center': (width//2, height//2), 'size': (height*0.3, height*0.3)}

	def sensor_handler_in(self):
		self.csvlogger.log(event='subject entered well')
		if self.drops_available > 0:
			self.sound.play(ir_tone)
			self.reward_count += 1
			self.csvlogger.log(event='reward accepted', reward_count=self.reward_count, drops_available=self.drops_available)
			self.drops_available = 0

	def sensor_handler_out(self):
		self.csvlogger.log(event='subject left well')

	def main(self, event):
		if self.now() - self.rect_start_time > 0.2:
			self.screen.clean()

		if self.now() - self.last_press_time > 1 and event.type == POINTERPRESSED:
			self.liqrew.drop()
			self.drops_dispensed += 1
			self.drops_available += 1
			self.csvlogger.log(event='reward dispensed', drops_dispensed=self.drops_dispensed, drops_available=self.drops_available)
			self.sound.play(screen_tone)
			self.draw.rect(**self.square_kwargs)
			self.rect_start_time = self.now()
			self.last_press_time = self.now()
		self.screen.update()

	def end(self):
		self.csvlogger.log(event='Training ended', reward_count=self.reward_count, drops_dispensed=self.drops_dispensed, drops_available=self.drops_available)

class OperantConditioning(Protocol):
	"""
	STAGE 4
	---
	When the subject touches the screen, the ability to get a reward is unlocked for 20 seconds.
	The reward will be available for 20 seconds after *first screen touch*. Touching the screen again during the 20 seconds will not extend the window.
	When the reward is unlocked (by screen touch), the screen will turn on (for the 20 seconds), and a tone will be played.
	when the subject breaks the ir beam, the screen will turn off, and the window to touch the screen will reset
	#When the subject breaks the ir beam and a reward was dispensed, a tone is played??
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
		self.square_kwargs = {'color': (0, 65, 65), 'center': (width//2, height//2), 'size': (height*0.3, height*0.3)}
	
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
			self.screen.clean()

		if not self.reward_available() and event.type == POINTERPRESSED:
			self.allow_reward(20)
			self.sound.play(screen_tone)
			self.draw.rect(**self.square_kwargs)

		self.screen.update()

	def end(self):
		self.csvlogger.log(event='Training ended', reward_count=self.reward_count, rewards_missed=self.rewards_missed, no_rewards=self.no_rewards)
