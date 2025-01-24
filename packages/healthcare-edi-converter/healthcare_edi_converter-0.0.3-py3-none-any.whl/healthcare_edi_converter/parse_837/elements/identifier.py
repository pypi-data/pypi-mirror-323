from typing import Optional

from ..elements import Element


class Identifier(Element):

	def __set__(self, obj, value):
		if obj.identification != value:
			raise ValueError('class identifier does not match segment identifier.')

		value = self.parser(value)
		setattr(obj, self.private_name, value)

	def parser(self, value: str) -> Optional[str]:
		return value
