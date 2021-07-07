import sys
import traceback
from contextlib import suppress

from discord.ext.commands import *

async def error_handler(ctx, error):
    ignored = (CommandNotFound, )
    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return
    elif isinstance(error, MissingRequiredArgument):
        await ctx.reply(f'Missing Required Argument!\nMissing Arguments: `{error.param}`\n> Usage: `{ctx.prefix}{ctx.invoked_with} {ctx.command.usage}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, TooManyArguments):
        await ctx.reply(f'Too Many Arguments!\n> Usage: `{ctx.prefix}{ctx.invoked_with} {ctx.command.usage}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, MessageNotFound):
        await ctx.reply(f'Unable to find Message!\n> Argument passed: `{error.argument}`')
    elif isinstance(error, MemberNotFound):
        await ctx.reply(f'Unable to find Member!\n> Argument passed: `{error.argument}`')
    elif isinstance(error, UserNotFound):
        await ctx.reply(f'Unable to find User!\n> Argument passed: `{error.argument}`')
    elif isinstance(error, ChannelNotFound):
        await ctx.reply(f'Unable to find Channel!\n> Argument passed: `{error.argument}`')
    elif isinstance(error, ChannelNotReadable):
        await ctx.reply(f'I am missing Permissions to read a Required Channel!\n> Channel: `{error.argument.mention}`')
    elif isinstance(error, BadColourArgument):
        await ctx.reply(f'The Color argument is not Valid.\n> Color: `{error.argument}`')
    elif isinstance(error, RoleNotFound):
        await ctx.reply(f'Unable to find Role!\n> Argument passed: `{error.argument}`')
    elif isinstance(error, BadInviteArgument):
        await ctx.reply(f'The Invite is either Invalid or Expired!')
    elif isinstance(error, EmojiNotFound):
        await ctx.reply(f'Unable to find Emoji!\n> Argument passed: `{error.argument}`')
    elif isinstance(error, PartialEmojiConversionFailure):
        await ctx.reply(f'Emoji does not match the correct format!\n> Arguments passed: `{error.argument}`')
    elif isinstance(error, BadBoolArgument):
        await ctx.reply(f'Boolean Argument does not match the valid format!\n> Arguments passed: `{error.argument}`')
    elif isinstance(error, BadFlagArgument):
        await ctx.reply('Flag failed tO convert a value!')
    elif isinstance(error, MissingFlagArgument):
        await ctx.reply('Missing Flag Argument! Flag did not get a value')
    elif isinstance(error, TooManyFlags):
        await ctx.reply('Flag recieved too many Values!')
    elif isinstance(error, MissingRequiredFlag):
        await ctx.reply('Missing Required Flag!')
    elif isinstance(error, BadLiteralArgument):
        await ctx.send(f'Passed Invalid Value in Literal!\n> Parameter Failed: {error.param}\n> Valid Literals: `{", ".join(i for i in error.literals)}`')
    elif isinstance(error, BadUnionArgument):
        await ctx.reply(f'Invaild Inupt type passed in Arguments!\n> Parameter failed: {error.param}\n> Valid Input Types: {", ".join(i for i in error.converters)}\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, UnexpectedQuoteError):
        await ctx.reply(f'Found Unexpected Quote mark inside non-quoted string!\n Quote: `{error.quote}`')
    elif isinstance(error, InvalidEndOfQuotedStringError):
        await ctx.reply(f'Expected space after closing quote but `{error.char}` found!')
    elif isinstance(error, ExpectedClosingQuoteError):
        await ctx.reply(f'Expected `{error.close_quote}` Closing quote but not Found!')
    elif isinstance(error, CheckAnyFailure):
        pass
    elif isinstance(error, PrivateMessageOnly):
        await ctx.reply('This command or an Operation in this command works in Private Messages (DMs) only!')
    elif isinstance(error, NoPrivateMessage):
        with suppress(Exception):
            await ctx.author.send('This command or an Operation in this command do not work in Private Messages (DMs)!')
    elif isinstance(error, NotOwner):
        await ctx.reply('This is a **Developer Only** Command!')
    elif isinstance(error, MissingPermissions):
        await ctx.reply(f'You are Missing Permissions to use this Command!\n> Missing Permissions: `{", ".join(str(i).replace("_", " ").capitalize() for i in error.missing_perms)}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, BotMissingPermissions):
        await ctx.reply(f'I am Missing Permissions to execute this Command!\n> Missing Permissions: `{", ".join(str(i).replace("_", " ").capitalize() for i in error.missing_perms)}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, MissingRole):
        await ctx.reply(f'You are Missing required Role to use this Command!\n> Missing Role Parameter: `{error.missing_role}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, BotMissingRole):
        await ctx.reply(f'I am Missing required Role to execute this Command!\n> Missing Role Parameter: `{error.missing_role}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, MissingAnyRole):
        await ctx.reply(f'You are Missing required Role to use this Command! You need to have atleast one role out of the Missing Roles to run this Command.\n> Missing Roles Parameters: `{", ".join(i for i in error.missing_roles)}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error,BotMissingAnyRole):
        await ctx.reply(f'I am Missing required Role to use this Command! I need to have atleast one role out of the Missing Roles to execute this Command.\n> Missing Roles Parameters: `{", ".join(i for i in error.missing_roles)}`\nNeed more info? Use `{ctx.prefix}help {ctx.invoked_with}`')
    elif isinstance(error, NSFWChannelRequired):
        await ctx.reply('This command can only be used in NSFW channels!')
    elif isinstance(error, DisabledCommand):
        await ctx.reply('This command is Disabled!')
    elif isinstance(error, CommandInvokeError):
        await ctx.reply(f'Oops! Some error occured while invoking the command!\n> Error: `{error.__cause__}`')
    elif isinstance(error, CommandOnCooldown):
        await ctx.reply(f'Woah! Looks like you\'re in hurry! This command is on `{error.cooldown.tpye}` type Cooldown! Try again in `{error.retry_after:,.0f}` seconds.')
    elif isinstance(error, MaxConcurrencyReached):
        await ctx.reply(f'Woah! Looks like this command is being used a lot...\nThe command reached it\'s Max Concurrency of `{error.number}` invokers per `{error.per}`. Try again in a few seconds...')
    elif isinstance(error, ExtensionAlreadyLoaded):
        await ctx.reply('Extension is Already Loaded!')
    elif isinstance(error, ExtensionNotLoaded):
        await ctx.reply('Extension is not Loaded!')
    elif isinstance(error, NoEntryPointError):
        await ctx.reply('The Extension do not have a `setup` entry point function.')
    elif isinstance(error, ExtensionNotFound):
        await ctx.reply('Unable to find the Extension!')
    elif isinstance(error, CommandRegistrationError):
        await ctx.reply(f'Command with name `{error.name}` cannot be addded because it\'s name is already taken by a different Command.\n> Alias Conflict: `{error.alias_conflict}`')
    else:
        await ctx.reply(f'Oops! Some error Occured...\n> Error: `{error}`')
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)