from touchscreen_protocol import Protocol, tsColors, POINTERPRESSED
import time
class LoadingTest(Protocol):
	"""
	Training Protocol has a loading bar go from 100% to 0% full. when the bar hits 0% a button below it turns green
	if the button is pressed while green, treats are dispensed and the bar is set back to 100%. if the button is pressed prematurly, the bar is reset and a noise is played
	"""
	def init(self):
		self.liqrew.set_drop_amount(3)
		self.log('starting test')
		size = self.screen.get_size()
		self.bar_center = (int(size[0] * 0.5), int(size[1] * 0.2))
		self.bar_size = (int(size[0] * 0.6), int(size[1] * 0.2))
		self.bar_border_size = (self.bar_size[0]-(self.bar_size[0]*0.05), self.bar_size[1]-(self.bar_size[1]*0.025))
		self.button_center = (int(size[0]*0.5), int(size[1]*0.5))
		self.radius = int(size[0] * 0.075)
		self.bar_start=(self.bar_center[0] - self.bar_border_size[0] / 2, self.bar_center[1] - self.bar_border_size[1] / 2)
		self.color_bad = tsColors['purple']
		self.color_good = tsColors['green']
		self.set_progress(1)
		self.duration = 15
		self.beamBroken = False
		self.log(f'wait duration set to {self.duration} second(s)')

	def set_progress_bar(self):
		size = (self.bar_border_size[0] * self.progress, self.bar_border_size[1])
		self.draw.rect(color=self.color_bad, start=self.bar_start, size=size)

	def set_progress(self, progress):
		self.progress = progress
		if self.progress < 0:
			self.progress = 0
		if self.progress == 1:
			self.start = time.time()
			self.log('progress bar reset to 100%')

	def redraw(self):
		self.screen.clean()
		# border
		self.draw.rect(color=tsColors['white'], center=self.bar_center, size=self.bar_size)
		# internal background color
		self.draw.rect(color=self.screen.backcolor, center=self.bar_center, size=self.bar_border_size)
		color = self.color_bad if self.progress != 0 else self.color_good
		self.reward_button=self.draw.circle(color=color, center=self.button_center, radius=self.radius)
		self.set_progress_bar()
		self.screen.update()

	def sensor_handler_in(self):
		self.log(f'IRbeam was broken at {self.progress*100}% full')
		self.beamBroken = True

	def sensor_handler_out(self):
		self.log(f'IRbeam was released at {self.progress*100}% full')
		self.beamBroken = False

	def main(self, event):
		self.redraw()
		if self.reward_button.collidepoint(event.position) and event.type == POINTERPRESSED: # event.type == POINTERPRESSED and 
			self.log(f'button pressed at location: {event.position} at time: {self.now()}')
			if self.progress == 0:
				while not self.beamBroken:
					pass
				self.liqrew.drop()
				self.log(f'reward dispensed at {self.now()}')
				time.sleep(1)
			else:
				self.log(f'sound played at {self.now()}')
				self.sound.play(frequency=18000)
			self.set_progress(1)
			self.redraw()
		time_delta = time.time() - self.start
		step = self.duration - time_delta
		self.set_progress(step/self.duration)

	def end(self):
		self.set_note()
		self.log('Ended training')
