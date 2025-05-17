def render_inventory_status_message(session, action: str) -> str:
    session_number = str(session.id).zfill(5)
    created_at_str = session.created_at.strftime("%d.%m.%Y %H:%M")

    if action == "finished":
        return f"✅ Инвентаризация №{session_number} от {created_at_str} успешно завершена."
    elif action == "cancelled":
        return f"❌ Инвентаризация №{session_number} от {created_at_str} была отменена."
    else:
        return f"ℹ️ Инвентаризация №{session_number} от {created_at_str} — статус: {action}"
