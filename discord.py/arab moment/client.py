import discord, json, math, asyncio, owner_ids, constants
from datetime import datetime

client = discord.Client()

token = constants.token
prefix = constants.prefix

async def unmute(m, t, r, role):
    await asyncio.sleep(t*60*60)
    await m.remove_roles(role, reason=r)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=constants.game)
    print("Successfully logged in. Credentials:")
    print(client.user.name + "#" + client.user.discriminator)
    print(client.user.id)
    print(token)


@client.event
async def on_message(msg):
    muted_role = False
    if msg.author.bot:
        return
    if not msg.content.startswith(prefix):
        return
    args = msg.content[len(prefix):len(msg.content)].strip().split(" ")
    cmd = args[0].lower()
    args.pop(0)
    c = msg.channel
    g = msg.guild
    m = msg.author
    for role in g.roles:
        if role.name.lower() == "muted":
            muted_role = role
            break
    if cmd == "ping":
        start = datetime.now()
        message = await c.send("Client Ping: " + str(int(client.latency*1000)))
        await message.edit(content="Client Ping: " + str(int(client.latency*1000)) + "\nAPI Ping: " + str(int((datetime.now().microsecond-start.microsecond)/1000)))
    if cmd == "ban":
        if not g.me.guild_permissions.ban_members:
            return await c.send("I lack the permissions to ban members.")
        if not m.guild_permissions.ban_members:
            return await c.send("You must have the `BAN_MEMBERS` permission to do this.")
        if not msg.mentions:
            return await c.send("Please provide a member to ban.")
        member = msg.mentions[0]
        reason = " ".join(args[1:len(args)]) or "None"
        if g.me.top_role < member.top_role:
            return await c.send("I am at a lower level on the role hierarchy than this member.")
        if m.top_role < member.top_role:
            return await c.send("This member has a higher role than you.")
        try:
            await member.ban(reason=reason)
            await c.send("{0}, I have **banned** {1}.\nReason: {2}".format(m.name, member.name, reason))
        except Exception as e:
            await c.send("Error while banning user: " + e)
    if cmd == "kick":
        if not g.me.guild_permissions.kick_members:
            return await c.send("I lack the permissions to kick members.")
        if not m.guild_permissions.kick_members:
            return await c.send("You must have the `KICK_MEMBERS` permission to do this.")
        if not msg.mentions:
            return await c.send("Please provide a member to kick.")
        member = msg.mentions[0]
        reason = " ".join(args[1:len(args)]) or "None"
        if g.me.top_role < member.top_role:
            return await c.send("I am at a lower level on the role hierarchy than this member.")
        if m.top_role < member.top_role:
            return await c.send("This member has a higher role than you.")
        try:
            await member.kick(reason=reason)
            await c.send("{0}, I have **kicked** {1}.\nReason: {2}".format(m.name, member.name, reason))
        except Exception as e:
            await c.send("An error occured while banning this user.")
    if cmd == "mute":
        if not g.me.guild_permissions.mute_members:
            return await c.send("I lack the permissions to mute members.")
        if not m.guild_permissions.mute_members:
            return await c.send("You must have the `MUTE_MEMBERS` permission to do this.")
        if not muted_role:
            return await c.send("No muted role exists. Please create one.")
        if not msg.mentions:
            return await c.send("Please mention a valid member.")
        mem = msg.mentions[0]
        if g.me.top_role < mem.top_role:
            return await c.send("I am at a lower level on the role hierarchy than this member.")
        if m.top_role < mem.top_role:
            return await c.send("This member has a higher role than you.")
        if muted_role in mem.roles:
            return await c.send("That member is already muted.")
        if not len(args) > 1:
            return await c.send("Please provide an amount of time to mute this user for.")
        if math.isnan(float(args[1])):
            return await c.send("Please provide a valid number.")
        reason = " ".join(args[2:len(args)]) or "None"
        time = float(args[1])
        try:
            await mem.add_roles(muted_role, reason=reason)
            await c.send("Successfully muted {} for {} hours. Reason: {}".format(mem.name, str(time), reason))
            await unmute(mem, time, "Mute time expired", muted_role)
        except Exception as e:
            await c.send("Error while muting member: " + str(e))
    if cmd == "unmute":
        if not muted_role:
            return await c.send("No muted role exists.")
        if not msg.mentions:
            return await c.send("Please mention a valid member.")
        mem = msg.mentions[0]
        if g.me.top_role < mem.top_role:
            return await c.send("I am at a lower level on the role hierarchy than this member.")
        if m.top_role < mem.top_role:
            return await c.send("This member has a higher role than you.")
        reason = " ".join(args[1:len(args)]) or "None"
        if not muted_role in mem.roles:
            return await c.send("This member is not muted.")
        await mem.remove_roles(muted_role, reason=reason)
        await c.send("Successfully unmuted {}. Reason: {}".format(mem.name, reason))
    if cmd == "eval":
        if not m.id in owner_ids.ids:
            return await c.send("You must be a bot owner to use this command.")
        if not len(args) > 0:
            return await c.send("You must include code to eval!")
        try:
            code = " ".join(args)
            result = eval(code)
            await c.send("Eval```python\n{0}```Returns```python\n{1}```".format(code, result))
        except Exception as e:
            await c.send("Eval```python\n{0}```Error```python\n{1}```".format(" ".join(args), e))
    if cmd == "help":
        helpEmb = discord.Embed()
        if not len(args) > 0:
            helpEmb.title = "All commands"
            helpEmb.description = "Here is a list of all commands I have."
            helpEmb.add_field(
                name="ping", value="Get the current Client ping and API ping", inline=False)
            helpEmb.add_field(name="ban", value="Ban a user", inline=False)
            helpEmb.add_field(name="kick", value="Kick a user", inline=False)
            helpEmb.add_field(name="mute", value="Mute a user", inline=False)
            helpEmb.add_field(
                name="unmute", value="Unmute a user", inline=False)
        elif args[0] == "ping":
            helpEmb.title = "ping"
            helpEmb.description = "Grab the Client and API ping."
            helpEmb.add_field(name="Usage", value="~ping", inline=False)
        elif args[0] == "ban":
            helpEmb.title = "ban"
            helpEmb.description = "Ban a user from the server."
            helpEmb.add_field(name="Usage", value="~ban (user) (reason || None)", inline=False)
            helpEmb.add_field(name="Examples", value="~ban @AA dumb stupid\n~ban @DDD", inline=False)
        elif args[0] == "kick":
            helpEmb.title = "kick"
            helpEmb.description = "Kick a user from the server."
            helpEmb.add_field(name="Usage", value="~kick (user) (reason || None)", inline=False)
            helpEmb.add_field(name="Examples", value="~kick @AA don't do that again\n~kick @DDD", inline=False)
        elif args[0] == "mute":
            helpEmb.title = "mute"
            helpEmb.description = "Mute a user for a certain amount of time."
            helpEmb.add_field(name="Usage", value="~mute (user) (time in hours) (reason || None)", inline=False)
            helpEmb.add_field(name="Example", value="~mute @AA 24 stop spamming\n~mute @DDD 0.5", inline=False)
        elif args[0] == "unmute":
            helpEmb.title = "unmute"
            helpEmb.description = "Unmute a user."
            helpEmb.add_field(name="Usage", value="~unmute (user) (reason || None)", inline=False)
            helpEmb.add_field(name="Examples", value="~unmute @AA said sorry in dms\n~unmute @DDD", inline=False)
        else:
            helpEmb.title = "Invalid command!"
            helpEmb.description = "The command you entered, {}, is invalid.".format(args[0])
            helpEmb.set_footer(text="Use ~help for a list of commands.", icon_url=client.user.avatar_url)
        await c.send(embed=helpEmb)
def login():
    try:
        client.run(token)
    except discord.errors.LoginFailure as err:
        print("Failed to login. Token: {}\n{}".format(token, err))
login()