import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Kullanıcı bakiyeleri, maaş zamanları, envanter ve meslekleri
balances = {}
last_salary_time = {}
inventories = {}
user_jobs = {}

# Roller ve maaşlar (Endonezya Rupisi - IDR)
job_salaries = {
    "Amele": 15000000,
    "Öğretmen": 50000000,
    "Doktor": 100000000,
    "Mühendis": 75000000,
    "Barista": 20000000,
    "Ofis Çalışanı": 30000000,
    "Garson": 20000000,
    "Kasiyer": 20000000,
    "Çiftçi": 35000000,
    "Polis": 60000000,
    "Taksi Şoförü": 30000000,
    "Admin": 100000000,
    "Kurucu": 200000000
}

# Market eşyaları (IDR)
market_items = {
    "Su": 2000,
    "Kahve": 5000,
    "Çay": 3000,
    "Ekmek": 2000,
    "Pizza": 10000,
    "Hamburger": 10000,
    "Sandviç": 5000,
    "Süt": 4000,
    "Tatlı": 6000,
    "Kola": 4000
}

# Maaş kontrol döngüsü
@tasks.loop(minutes=10)
async def salary_check():
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue

            now = datetime.utcnow()
            last_time = last_salary_time.get(member.id, now - timedelta(hours=6))

            # Kullanıcının mesleğine göre maaş
            job = user_jobs.get(member.id)
            if not job or job not in job_salaries:
                continue

            salary = job_salaries[job]

            # Aktif / Pasif maaş
            if member.status != discord.Status.offline:
                if (now - last_time) >= timedelta(hours=1):
                    balances[member.id] = balances.get(member.id, 0) + salary
                    last_salary_time[member.id] = now
                    print(f"{member.name} aktif maaş aldı: {salary} IDR")
            else:
                if (now - last_time) >= timedelta(hours=6):
                    balances[member.id] = balances.get(member.id, 0) + salary
                    last_salary_time[member.id] = now
                    print(f"{member.name} pasif maaş aldı: {salary} IDR")


# Kullanıcı bakiyesi
@bot.command()
async def bakiye(ctx):
    balance = balances.get(ctx.author.id, 0)
    job = user_jobs.get(ctx.author.id, "Mesleksiz")
    await ctx.send(f"💰 {ctx.author.mention}, bakiyen: {balance:,} IDR | Mesleğin: {job}")

# Para gönderme
@bot.command()
async def gonder(ctx, member: discord.Member, miktar: int):
    if balances.get(ctx.author.id, 0) < miktar:
        await ctx.send("Yeterli paran yok!")
        return
    balances[ctx.author.id] -= miktar
    balances[member.id] = balances.get(member.id, 0) + miktar
    await ctx.send(f"✅ {ctx.author.mention}, {member.mention} kullanıcısına {miktar:,} IDR gönderdi.")

# Marketi listeleme
@bot.command()
async def market(ctx):
    msg = "🛒 **Market (Yiyecek & İçecek)**\n"
    for item, price in market_items.items():
        msg += f"{item} - {price:,} IDR\n"
    await ctx.send(msg)

# Marketten satın alma
@bot.command()
async def satin_al(ctx, *, item: str):
    item = item.title()
    if item not in market_items:
        await ctx.send("❌ Böyle bir eşya yok!")
        return
    price = market_items[item]
    if balances.get(ctx.author.id, 0) < price:
        await ctx.send("❌ Yeterli paran yok!")
        return
    balances[ctx.author.id] -= price

    # Envantere ekleme
    if ctx.author.id not in inventories:
        inventories[ctx.author.id] = []
    inventories[ctx.author.id].append(item)

    await ctx.send(f"✅ {ctx.author.mention}, {item} satın aldı! -{price:,} IDR")

# Envanteri gösterme
@bot.command()
async def envanter(ctx):
    items = inventories.get(ctx.author.id, [])
    if not items:
        await ctx.send("📦 Envanterin boş!")
    else:
        msg = "📦 **Envanterin**\n" + "\n".join(items)
        await ctx.send(msg)

# Meslek atama (sadece Admin veya Kurucu)
@bot.command()
async def meslek(ctx, member: discord.Member, *, job: str):
    if not any(role.name in ["Admin", "Kurucu"] for role in ctx.author.roles):
        await ctx.send("❌ Bu komutu sadece yetkililer kullanabilir!")
        return
    job = job.title()
    if job not in job_salaries:
        await ctx.send("❌ Böyle bir meslek yok!")
        return
    user_jobs[member.id] = job
    await ctx.send(f"✅ {member.mention} artık **{job}** olarak çalışıyor!")

# Mevcut meslekleri listeleme
@bot.command()
async def meslekler(ctx):
    msg = "👔 **Mevcut Meslekler ve Maaşları (IDR)**\n"
    for job, salary in job_salaries.items():
        msg += f"{job}: {salary:,} IDR\n"
    await ctx.send(msg)

# Bot hazır olduğunda başlat
@bot.event
async def on_ready():
    salary_check.start()
    print(f"Bot giriş yaptı: {bot.user}")
load_dotenv()
# .env içinden DISCORD_TOKEN değerini al
TOKEN = os.getenv("DISCORD_TOKEN")

# Bot prefix ve izinler

# Botu başlat
bot.run(TOKEN)

