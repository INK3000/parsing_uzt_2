import environs

env = environs.Env()
env.read_env()

TELEGRAM_ADMIN_ID = env.int("TELEGRAM_ADMIN_ID")
BOT_TOKEN = env.str("BOT_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not loaded")
