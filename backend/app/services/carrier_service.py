from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from backend.app.models.entities import Carrier, ServiceLevel, CarrierServiceZone, CarrierCalendar

class CarrierService:
    @staticmethod
    def get_all_carriers(db: Session, active_only: bool = True) -> List[Dict[str, Any]]:
        query = db.query(Carrier)
        if active_only:
            query = query.filter(Carrier.is_active == True)
        carriers = query.all()
        result = []
        for c in carriers:
            services = db.query(ServiceLevel).filter(ServiceLevel.carrier_id == c.carrier_id).all()
            result.append({
                "carrier_id": c.carrier_id,
                "carrier_name": c.carrier_name,
                "contact_email": c.contact_email,
                "phone": c.phone,
                "reliability_score": c.reliability_score,
                "is_active": c.is_active,
                "services": [{
                    "service_id": s.service_id,
                    "service_name": s.service_name,
                    "service_code": s.service_code,
                    "base_rate": s.base_rate,
                    "rate_per_kg": s.rate_per_kg,
                    "rate_per_zone": s.rate_per_zone,
                    "guaranteed_delivery": s.guaranteed_delivery
                } for s in services]
            })
        return result

    @staticmethod
    def get_eligible_services(
        db: Session,
        origin_node_id: str,
        destination_zone: str,
        weight_kg: float = 1.0
    ) -> List[Dict[str, Any]]:
        rows = (
            db.query(CarrierServiceZone, ServiceLevel, Carrier)
            .join(ServiceLevel, CarrierServiceZone.service_id == ServiceLevel.service_id)
            .join(Carrier, ServiceLevel.carrier_id == Carrier.carrier_id)
            .filter(
                CarrierServiceZone.origin_node_id == origin_node_id,
                CarrierServiceZone.destination_zone == destination_zone,
                CarrierServiceZone.is_supported == True,
                Carrier.is_active == True
            )
            .all()
        )
        
        # Extract zone number for rate calculation (e.g. "Zone 4" -> 4)
        zone_num = 1
        try:
            zone_num = int(destination_zone.replace("Zone", "").strip())
        except ValueError:
            pass

        eligible = []
        for csz, srv, car in rows:
            cost = srv.base_rate + (srv.rate_per_kg * weight_kg) + (srv.rate_per_zone * zone_num)
            eligible.append({
                "carrier_id": car.carrier_id,
                "carrier_name": car.carrier_name,
                "reliability_score": car.reliability_score,
                "service_id": srv.service_id,
                "service_name": srv.service_name,
                "service_code": srv.service_code,
                "transit_days": csz.transit_days,
                "pickup_time": csz.pickup_time,
                "shipping_cost": round(cost, 2),
                "guaranteed_delivery": srv.guaranteed_delivery
            })
        # Sort by cost ascending
        eligible.sort(key=lambda x: x["shipping_cost"])
        return eligible

    @staticmethod
    def is_carrier_operating(db: Session, carrier_id: str, check_date: date) -> bool:
        cal = db.query(CarrierCalendar).filter(
            CarrierCalendar.carrier_id == carrier_id,
            CarrierCalendar.date == check_date
        ).first()
        if cal:
            return cal.is_operating
        # Default: Sunday no pickup
        return check_date.weekday() != 6
