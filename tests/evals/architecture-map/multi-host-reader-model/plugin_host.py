from app_core import DailyPipeline, Scheduler


class PluginAdapters:
    def __init__(self, obsidian):
        self.storage = obsidian.vault
        self.http = obsidian.request


def build_plugin(obsidian, source, llm, state, history, delivery):
    adapters = PluginAdapters(obsidian)
    pipeline = DailyPipeline(adapters.storage, source, llm)
    scheduler = Scheduler(state, history, pipeline, delivery.send_digest)
    return {"dashboard": True, "scheduler": scheduler, "adapters": adapters}
