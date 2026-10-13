def export_orders(orders):
    """Return orders as CSV text with the columns id,customer,note."""
    lines = ["id,customer,note"]
    for order in orders:
        lines.append(f"{order['id']},{order['customer']},{order['note']}")
    return "\n".join(lines) + "\n"
