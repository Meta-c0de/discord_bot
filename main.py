import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='m!', help_command=None, intents=intents)

score_file = "user_scores.json"
if not os.path.exists(score_file):
    with open(score_file, 'w') as f:
        json.dump({}, f)

def load_scores():
    with open(score_file, 'r') as f:
        return json.load(f)

def save_scores(scores):
    with open(score_file, 'w') as f:
        json.dump(scores, f)

question_bank = {
    # ... твой блок вопросов тут без изменений ...
}

@bot.event
async def on_ready():
    await bot.wait_until_ready()  # На всякий случай, если запуск медленный
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка при синхронизации команд: {e}")
    print(f"Бот запущен как {bot.user}")


@bot.command()
async def help(ctx):
    await ctx.send(
        "**Команды:**\n"
        "`m!question <easy|normal|hard|impossible>` — задать вопрос по выбранной сложности.\n"
        "`m!help` — список команд.\n"
        "Очки начисляются за правильные ответы и снимаются за ошибки."
    )

@bot.command()
async def question(ctx, difficulty: str):
    difficulty = difficulty.lower()
    if difficulty not in question_bank:
        await ctx.send("Пожалуйста, выбери сложность: easy, normal, hard, impossible.")
        return

    question = random.choice(question_bank[difficulty])
    options = question["options"]
    correct = question["answer"]
    author_id = str(ctx.author.id)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    options_text = "\n".join(f"{i + 1}. {opt}" for i, opt in enumerate(options))
    await ctx.send(f"**{question['question']}**\n{options_text}\nВведите номер ответа (1-4):")

    try:
        msg = await bot.wait_for("message", check=check, timeout=30.0)
        answer = int(msg.content.strip()) - 1
    except (ValueError, TimeoutError):
        await ctx.send("Неверный ввод или время вышло.")
        return

    scores = load_scores()
    scores.setdefault(author_id, 0)

    if answer == correct:
        scores[author_id] += 1
        await ctx.send("✅ Правильно! +1 балл.")
    else:
        scores[author_id] -= 1
        await ctx.send(f"❌ Неверно. Правильный ответ: {correct + 1}. -1 балл.")

    save_scores(scores)

@bot.tree.command(name="ping", description="Проверка пинга")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

bot.run(os.getenv("DISCORD_TOKEN"))




