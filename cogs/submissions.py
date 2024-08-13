import discord
from discord.ext import commands

def get_tag(channel, id:int):
    avail_tags = channel.available_tags
    for tag in avail_tags:
        if id == tag.id:
            return tag;
    else:
        return None

class SubmissionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_thread_update(self, before, after):
        newthread = after.parent.get_thread(after.id)
        print("a thread has been updated submission")
        change = before != after
        print("change?:" , change)
        print("tags before:")
        for tag in before.applied_tags: print(tag)
        print("tags after:")
        for tag in after.applied_tags: print(tag)
        print("new thread tags:")
        for tag in newthread.applied_tags: print(tag)
    #@commands.Cog.listener()
    async def on_raw_thread_update(self, payload):
        thread = payload.thread
        if thread.parent.type == discord.ChannelType.forum:
            tagIDs = payload.data["applied_tags"]
            tags = []
            tagNames = []
            for tagID in tagIDs:
                tag = get_tag(thread.parent,int(tagID))
                print(tagID, tag)
                tags.append(tag)
                tagNames.append(tag.name)
            statusMessage = ''
            if "Accepted" in tagNames:
                statusMessage = "This form has been accepted!"
            if "Denied" in tagNames:
                statusMessage = "this form has been denied."
            if "Needs Change" in tagNames:
                statusMessage = "this form requires some edits, Please make changes and then add the updated tag to this post"
            if "Updated" in tagNames or "Recruiting" in tagNames:
                await thread.unarchive()
            if statusMessage != '':
                threadMessage = await thread.fetch_message(thread.id)
                await thread.send(content=statusMessage, reference=threadMessage.to_reference())