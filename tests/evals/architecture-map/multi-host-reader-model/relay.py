class OfficialRelay:
    def __init__(self, devices, gate, resend):
        self.devices = devices
        self.gate = gate
        self.resend = resend

    def deliver(self, token, idempotency_key, message):
        recipient = self.devices.authenticate(token)
        reservation = self.gate.reserve(recipient, idempotency_key)
        if not reservation.accepted:
            return reservation.response
        return self.resend.send(recipient.email, message, idempotency_key)
