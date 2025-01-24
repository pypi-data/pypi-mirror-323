from typing import Optional, Union

from ..elements import Element


class Integer(Element):

	def parser(self, value: str) -> Optional[Union[int, str]]:
		if value == '':
			return None

		try:
			value = int(value)
		except:
			pass

		return value
