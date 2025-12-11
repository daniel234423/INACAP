import json
from datetime import datetime
from typing import Optional

import requests


class ApiCambioMoneda:
	"""Cliente liviano para consultar indicadores desde findic.cl."""

	BASE_URL = "https://www.findic.cl/api"

	def __init__(self, session: Optional[requests.Session] = None):
		self.session = session or requests.Session()

	@staticmethod
	def _normalizar_valor_bruto(valor_bruto):
		if valor_bruto is None:
			raise ValueError("La respuesta del indicador no contiene un valor válido")
		if isinstance(valor_bruto, (int, float)):
			return float(valor_bruto)
		texto = str(valor_bruto).replace(".", "").replace(",", ".")
		return float(texto)

	def obtener_valor(self, indicador: str, fecha: Optional[str] = None) -> Optional[float]:
		"""
		Retorna el valor numérico del indicador para la fecha dada (DD-MM-YYYY).
		Si no se entrega fecha, usa la fecha actual.
		Devuelve None si ocurre un error de red o si el dato no está disponible.
		"""

		fecha_consulta = fecha or datetime.now().strftime("%d-%m-%Y")
		indicador = indicador.strip().lower()
		url = f"{self.BASE_URL}/{indicador}/{fecha_consulta}"

		try:
			respuesta = self.session.get(url, timeout=8)
			respuesta.raise_for_status()
			datos = json.loads(respuesta.text)
			serie = datos.get("serie") or []
			if not serie:
				return None
			valor_bruto = serie[0].get("valor")
			return self._normalizar_valor_bruto(valor_bruto)
		except Exception as exc:
			print(f"No se pudo obtener el indicador {indicador}: {exc}")
			return None
