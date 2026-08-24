from quota import QuotaGate


async def public_request(tenant: str, gate: QuotaGate) -> int:
    if not await gate.allow(tenant):
        return 429
    return 200


async def admin_request(tenant: str) -> int:
    return 200
