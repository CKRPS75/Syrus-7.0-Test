from app.services.impact_service import ImpactService


def test_delay_model_ranges(db_session):
    impact_svc = ImpactService(db_session)
    
    low_delay = impact_svc.calculate_delay("LOW")
    med_delay = impact_svc.calculate_delay("MEDIUM")
    high_delay = impact_svc.calculate_delay("HIGH")

    assert 5 <= low_delay <= 10
    assert 10 <= med_delay <= 25
    assert 25 <= high_delay <= 60
