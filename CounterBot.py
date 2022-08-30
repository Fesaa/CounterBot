import typing
import discord
import asqlite

from discord.ext import commands

# Edit before running the file
TOKEN: str = ...  # type: ignore
BOT_ID: int = ...  # type: ignore
COMMAND_PREFIX: str = ...  # type: ignore


class CounterBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            application_id=BOT_ID,
            case_insensitive=True,
        )

    async def channels(self) -> list:
        """
        Returns all active Counter channels
        """
        async with asqlite.connect('CounterBot.db') as conn:
            async with conn.cursor() as cursor:
                res = await cursor.execute("SELECT channel_id FROM counter;")
                channels = await res.fetchall()
        return list(i[0] for i in channels)

    async def setup_hook(self) -> None:
        async with asqlite.connect('CounterBot.db') as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""CREATE TABLE IF NOT EXISTS counter (
                                        channel_id bigint unsigned NOT NULL,
                                        current_count int DEFAULT NULL,
                                        last_user_id bigint DEFAULT NULL,
                                        PRIMARY KEY (channel_id)
                                        );""")
                await cursor.execute("""CREATE TABLE IF NOT EXISTS leaderboard (
                                        channel_id bigint unsigned NOT NULL,
                                        user_id bigint NOT NULL,
                                        score bigint DEFAULT NULL,
                                        PRIMARY KEY (channel_id,user_id)
                                        );""")
                await conn.commit()

        self.add_command(_scoreboard)
        self.add_command(_start)
        self.add_command(_stop)

    async def on_ready(self) -> None:
        print(f"[{discord.utils.utcnow()}] Bot Ready: {self.user.name}")

    async def on_message(self, msg: discord.Message, /) -> None:

        if msg.author.bot:
            return

        await self.process_commands(msg)

        if msg.channel.id not in await self.channels():
            return

        if not msg.content.isdigit():
            return await msg.delete()  # Non numerical messages are deleted

        async with asqlite.connect('CounterBot.db') as conn:
            async with conn.cursor() as cursor:
                res = await cursor.execute("SELECT current_count, last_user_id FROM counter WHERE channel_id = ?;", (msg.channel.id,))
                (count, last_user_id) = await res.fetchone()

        if last_user_id == msg.author.id:  # Not allowed to count by yourself
            return await msg.delete()

        sub_count = int(msg.content)

        if count + 1 == sub_count:
            async with asqlite.connect('CounterBot.db') as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("INSERT INTO counter (channel_id, current_count, last_user_id) VALUES (?, ?, ?) ON CONFLICT DO UPDATE SET current_count = current_count + 1, last_user_id = ?;", 
                                            (msg.channel.id, count + 1, msg.author.id, msg.author.id))
                    await cursor.execute("INSERT INTO leaderboard (channel_id, user_id, score) VALUES (?, ?, ?) ON CONFLICT DO UPDATE SET score = score + 1;",
                                    (msg.channel.id, msg.author.id, 1),)
                    await conn.commit()
        else:
            await msg.delete()  # Counting increments by one

    async def on_command_error(
        self, context: commands.Context, exception: commands.errors.CommandError, /
    ) -> None:
        """
        Command Error Handler; ignoring a few common irrelevant errors
        """

        if isinstance(exception, commands.errors.CommandNotFound):
            return

        elif isinstance(exception, commands.errors.MissingPermissions):
            return

        elif isinstance(exception, commands.errors.MissingRequiredArgument):
            return

        else:
            raise exception


class CounterBotContext(commands.Context):
    """
    Custom Context for commands.Context.bot type annotation
    """

    @property
    def bot(self) -> CounterBot:
        return self.bot


@commands.command(name="start")
@commands.has_permissions(manage_messages=True)
async def _start(ctx: CounterBotContext, slowmode: bool = True):
    """
    Initiate channel for Counting, CounterBot replies with '0' as confirmation
    :param slowmode: when True, adds a slowmode of one second to the channel, defaults to True
    :type slowmode: bool, optional
    """
    if ctx.channel.id in await ctx.bot.channels():  # Game already running
        return

    if slowmode:
        try:
            await ctx.channel.edit(
                slowmode_delay=1,
                reason="Initiating Counter Channel, adding slowmode against spam",
            )
        except discord.errors.Forbidden:
            pass
    
    async with asqlite.connect('CounterBot.db') as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO counter (channel_id, current_count, last_user_id) VALUES (?, ?, ?);",
                                    (ctx.channel.id, 0, ctx.bot.user.id),)
            await conn.commit()
    await ctx.send("0")


@commands.command(name="stop")
@commands.has_permissions(manage_messages=True)
async def _stop(ctx: CounterBotContext):
    """
    Remove channel for Counter, CounterBot replies with '👌' as confirmation
    """

    if ctx.channel.id not in await ctx.bot.channels():  # No game to stop
        return

    try:
        await ctx.channel.edit(
            slowmode_delay=0, reason="Removing Counter Channel, removing slowmode"
        )
    except discord.errors.Forbidden:
        pass

    async with asqlite.connect('CounterBot.db') as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM counter WHERE channel_id = ?;",
                                    (ctx.channel.id,),)
            await conn.commit()
    await ctx.send("\U0001f44c")


@commands.command(name="scoreboard", aliases=["lb", "sc", "leaderboard"])
async def _scoreboard(
    ctx: CounterBotContext, channel: typing.Optional[discord.TextChannel]
):
    """
    Display leaderboard for a Counter channel.
    :param channel: the channel to request the scoreboard of, defaults to ctx.channel
    :type channel: discord.TextChannel, optional
    """

    channel = channel or ctx.channel

    async with asqlite.connect('CounterBot.db') as conn:
        async with conn.cursor() as cursor:
            res = await cursor.execute("SELECT user_id,score FROM leaderboard WHERE channel_id = ? ORDER BY score DESC LIMIT 15;",
                                    (channel.id,),)
            scores = await res.fetchall()

    if not scores:
        return

    author_score = False
    lb_prefix = ["🥇", "🥈", "🥉"] + [str(i) for i in range(4, 16)]
    e = discord.Embed(title=f"Scoreboard for {channel.name}", colour=0x8A2BE2)

    desc = ""

    for index, (user_id, score) in enumerate(scores):
        desc += f"{lb_prefix[index]}: <@{user_id}> - **{score}**\n"
        if user_id == ctx.author.id:
            author_score = True

    if not author_score:  # If author isn't in the top 15 -> add extra line with score
        async with asqlite.connect('CounterBot.db') as conn:
            async with conn.cursor() as cursor:
                res = await cursor.execute("SELECT score FROM leaderboard WHERE channel_id  = ? AND user_id = ?;",
                                    (ctx.channel.id, ctx.author.id))
                score = await res.fetchone()

        if score:
            desc += f"Your score: {score}"

    e.description = desc

    await ctx.send(embed=e)


bot = CounterBot()
bot.run(TOKEN)
