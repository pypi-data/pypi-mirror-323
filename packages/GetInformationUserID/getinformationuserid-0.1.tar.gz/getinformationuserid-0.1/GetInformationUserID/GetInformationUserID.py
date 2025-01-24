from telethon import events


Class GetInformationUserID(*self(user_id), bot or client)
async def GetInformationUserIDIntefikation(user_id, bot):
    try:
        user = await bot.get_entity(user_id)
        text = f"{user.first_name or ''} {user.last_name or ''}".strip()
        full_name = {user.first_name or ''} {user.last_name or ''}.strip() or (user.username or str(user.id))
        
        if user.username:
            return f"<a href='https://t.me/{user.username}'>{full_name}</a>"
        else:
            return f"<a href='tg://openmessage?user_id={user.id}'>{full_name}</a>"
    
    except Exception as e:
        return f"<a href='tg://openmessage?user_id={user_id}'>{user_id}</a>"
