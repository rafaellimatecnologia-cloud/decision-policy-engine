from decision_policy_engine.decision.router import Router
from decision_policy_engine.models import Context, CostVector, ExecutionRoute


def _base_context(network_available: bool = True) -> Context:
    return Context(
        network_available=network_available,
        rtt_ms=100,
        battery_level=0.6,
        user_present=True,
        supervised_mode=True,
    )


def test_router_forbids_cloud_when_network_off() -> None:
    context = _base_context(network_available=False)
    candidates = {
        ExecutionRoute.LOCAL: CostVector(100, 0.1, 0.1, 0.1),
        ExecutionRoute.CLOUD: CostVector(50, 0.2, 0.2, 0.2),
        ExecutionRoute.DEGRADED: CostVector(500, 0.05, 0.3, 0.0),
    }

    chosen_route, _, _ = Router.select_route(context, candidates)

    assert chosen_route != ExecutionRoute.CLOUD


def test_router_tie_break_order() -> None:
    context = _base_context()
    candidates = {
        ExecutionRoute.LOCAL: CostVector(100, 0.2, 0.2, 0.2),
        ExecutionRoute.HYBRID: CostVector(100, 0.2, 0.2, 0.2),
        ExecutionRoute.CLOUD: CostVector(100, 0.2, 0.2, 0.2),
        ExecutionRoute.DEGRADED: CostVector(100, 0.2, 0.2, 0.2),
    }

    chosen_route, _, _ = Router.select_route(context, candidates)

    assert chosen_route == ExecutionRoute.LOCAL


def test_router_expected_winner_simple_case() -> None:
    context = _base_context()
    candidates = {
        ExecutionRoute.LOCAL: CostVector(200, 0.3, 0.3, 0.3),
        ExecutionRoute.HYBRID: CostVector(150, 0.2, 0.2, 0.2),
        ExecutionRoute.CLOUD: CostVector(400, 0.4, 0.4, 0.4),
    }

    chosen_route, _, explanation = Router.select_route(context, candidates)

    assert chosen_route == ExecutionRoute.HYBRID
    assert ExecutionRoute.HYBRID in explanation.scores


def test_router_prefers_degraded_when_local_missing_and_network_off() -> None:
    context = _base_context(network_available=False)
    candidates = {
        ExecutionRoute.DEGRADED: CostVector(400, 0.2, 0.3, 0.0),
        ExecutionRoute.HYBRID: CostVector(200, 0.2, 0.2, 0.2),
    }

    chosen_route, _, _ = Router.select_route(context, candidates)

    assert chosen_route == ExecutionRoute.DEGRADED


def test_router_tie_break_with_zero_weights(monkeypatch) -> None:
    from decision_policy_engine.decision import router as router_module

    monkeypatch.setattr(
        router_module,
        "WEIGHTS",
        {"latency_ms": 0.0, "privacy_risk": 0.0, "reliability_risk": 0.0, "dollar_cost": 0.0},
    )
    context = _base_context()
    candidates = {
        ExecutionRoute.LOCAL: CostVector(300, 0.4, 0.4, 0.4),
        ExecutionRoute.HYBRID: CostVector(100, 0.1, 0.1, 0.1),
        ExecutionRoute.CLOUD: CostVector(50, 0.05, 0.05, 0.05),
    }

    chosen_route, _, _ = router_module.Router.select_route(context, candidates)

    assert chosen_route == ExecutionRoute.LOCAL
