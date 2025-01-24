import commanding
import time

cliManager = commanding.CLIManager("> ")

@cliManager.commandManager.registerCommand("test")
def textCommand(text: str = "text"): cliManager.info(text)

cliManager.start()



while True:
    # time.sleep(1)
    # cliManager.info("asdf")
    # time.sleep(1)
    # cliManager.warn("asdf")
    # time.sleep(1)
    # cliManager.error("asdf")
    # time.sleep(1)
    # cliManager.debug("asdf")
    ...