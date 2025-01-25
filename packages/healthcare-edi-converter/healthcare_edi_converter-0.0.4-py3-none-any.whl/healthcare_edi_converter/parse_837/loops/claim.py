from typing import Iterator, Tuple, Optional, List
from warnings import warn

from ..segments.claim import Claim as ClaimSegment
from ..segments.entity import Entity as EntitySegment
from ..segments.reference import Reference as ReferenceSegment
from ..segments.date import Date as DateSegment
from ..segments.amount import Amount as AmountSegment
from ..segments.utilities import find_identifier
from ..segments.diagnosis import Diagnosis as DiagnosisSegment
from ..segments.note import Note as NoteSegment

from ..loops.payer import Payer as PayerLoop

from ..segments.subscriber import Subscriber as SubscriberSegment
from ..loops.subscriber import Subscriber as SubscriberLoop

from ..segments.patient import Patient as PatientSegment
from ..segments.billingprovider import Billingprovider as BillingproviderSegment
from ..segments.utilities import split_segment  

from ..segments.serviceline import ServiceLine as ServiceLineSegment

# 837 claims are institutional claims
from ..loops.service import ServiceInstitutional as InstitutionalServiceLoop

# 837P claims are professional claims
from ..loops.service import ServicelineSegmentProfessionalSegment as ProfessionalServiceLoop


class Claim:
	initiating_identifier = ClaimSegment.identification
	terminating_identifiers = [
		ClaimSegment.identification,
		PatientSegment.identification,
		'SE'
	]

	def __init__(
			self,
			claim: ClaimSegment = None,
			entities: List[EntitySegment] = None,
			services: List[ServiceLineSegment] = None,
			references: List[ReferenceSegment] = None,
			dates: List[DateSegment] = None,
			amount: AmountSegment = None,
			patient: PatientSegment = None,
			billingprovider: BillingproviderSegment = None,
			subscriber:SubscriberSegment=None,
			subscriber_other:SubscriberLoop=None,
			attending_provider_taxonomy:BillingproviderSegment=None,
			service_facility_location:PayerLoop=None,
			submitter:PayerLoop=None,
			receiver:PayerLoop=None,
			diagnosis:List[DiagnosisSegment]=None,
			note:NoteSegment=None,
	):
		self.claim = claim
		self.entities = entities if entities else []
		self.services = services if services else []
		self.references = references if references else []
		self.dates = dates if dates else []
		self.amount = amount
		self.patient=patient
		self.billingprovider=billingprovider
		self.subscriber=subscriber
		self.subscriber_other=subscriber_other 
		self.attending_provider_taxonomy=attending_provider_taxonomy 
		self.submitter=submitter 
		self.receiver=receiver 
		self.diagnosis=self.diagnosis = diagnosis if diagnosis else []
		self.note=note
		self.service_facility_location=service_facility_location



	def __repr__(self):
		return '\n'.join(str(item) for item in self.__dict__.items())

	@property
	def rendering_provider(self) -> Optional[EntitySegment]:
		rendering_provider = [e for e in self.entities if e.entity == 'rendering provider']
		assert len(rendering_provider) <= 1

		if len(rendering_provider) == 1:
			return rendering_provider[0]

	@property
	def claim_statement_period_start(self) -> Optional[DateSegment]:
		statement_period_start = [d for d in self.dates if d.qualifier == 'claim statement period start']
		assert len(statement_period_start) <= 1

		if len(statement_period_start) == 1:
			return statement_period_start[0]

	@property
	def claim_statement_period_end(self) -> Optional[DateSegment]:
		statement_period_end = [d for d in self.dates if d.qualifier == 'claim statement period end']
		assert len(statement_period_end) <= 1

		if len(statement_period_end) == 1:
			return statement_period_end[0]

	@classmethod
	def build(cls, segment: str, segments: Iterator[str]) -> Tuple['Claim', Optional[Iterator[str]], Optional[str]]:
		claim = Claim()
		claim.claim = ClaimSegment(segment)
		identifier2=split_segment(segment)
		
		segment = segments.__next__()
		
		while True:

			try:
				if segment is None:
					segment = segments.__next__()
				
				identifier  = find_identifier(segment)
				identifier2 = split_segment(segment)

				if (identifier == InstitutionalServiceLoop.initiating_identifier):
					service, segment, segments = InstitutionalServiceLoop.build(segment, segments)
					claim.services.append(service)

				elif (identifier2[0] == EntitySegment.identification and   identifier2[1] != '77')  :
					entity = EntitySegment(segment)
					claim.entities.append(entity)
					segment = None
				elif identifier == SubscriberLoop.initiating_identifier:

					sub, segments, segment = SubscriberLoop.build(segment, segments)
					
					claim.subscriber_other=sub

				elif identifier == ReferenceSegment.identification:
					reference = ReferenceSegment(segment)
					claim.references.append(reference)
					segment = None

				elif identifier == DateSegment.identification:
					date = DateSegment(segment)
					claim.dates.append(date)
					segment = None

				elif identifier == AmountSegment.identification:
					amount = AmountSegment(segment)
					claim.amount = amount
					segment = None

				elif identifier == BillingproviderSegment.identification:
					taxonomy=BillingproviderSegment(segment)
					claim.attending_provider_taxonomy = taxonomy
					segment = None
				elif (identifier2[0]== PayerLoop.initiating_identifier and identifier2[1] == '77' ):
					service_facility, segments, segment = PayerLoop.build(segment, segments)

					claim.service_facility_location = service_facility

				elif identifier == DiagnosisSegment.identification:
					diagnosis = DiagnosisSegment(segment)
					claim.diagnosis.append(diagnosis)
					segment = None

				elif identifier == NoteSegment.identification:
					claim.note=NoteSegment(segment)
					segment = None

				elif identifier in cls.terminating_identifiers:
					
					return claim, segments, segment

				else:
					message = f'Identifier: {identifier} not handled in claim loop.'
					segment = None
					warn(message)

			except StopIteration:
				return claim, None, None
