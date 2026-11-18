from dataclasses import dataclass, field


@dataclass
class Household:
	"""A family whose benefits we want to calculate."""

	adults: int
	child_ages: list = field(default_factory=list)
	annual_earnings: float = 0
	rent_monthly: float = 0
	childcare_paid_monthly: float = 0

	@property
	def size(self):
		return self.adults + len(self.child_ages)

	@property
	def monthly_earnings(self):
		return self.annual_earnings / 12
