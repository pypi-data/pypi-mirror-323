from .exceptions import Cancelled
from .exceptions import InvalidReply
from .exceptions import Accessblocked
from .exceptions import CancelledTask
from .exceptions import LimitedMessage
#=====================================================================

class HMessage:

    async def get05(blocked):
        if blocked is True:
            raise Accessblocked()

    async def get08(message):
        if message is True:
            raise InvalidReply()

    async def get07(taskuid, storage):
        if taskuid in storage:
            raise Cancelled()
        else:
            storage.append(taskuid)

    async def get03(taskuid, storage):
        if taskuid not in storage:
            raise Cancelled()

    async def get01(message, command):
        if message.startswith(command):
            raise Cancelled()

    async def get02(message, limit=1024):
        if len(message) > limit:
            raise LimitedMessage()

#=====================================================================

    async def get04(taskuid, storage, flocation):
        if taskuid in storage or flocation:
            pass
        else:
            raise CancelledTask()

#=====================================================================

    async def get09(update, uid=0):
        if update.reply_to_message.from_user.id == uid:
            raise InvalidReply()

#=====================================================================

    async def get06(update):
        if update.reply_to_message and update.reply_to_message.text:
            pass
        else:
            raise CancelledTask()

#=====================================================================
