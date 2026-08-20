from app_core import DailyPipeline, Scheduler
from node_adapters import NodeAdapters


def run_once(config, storage, http, source, llm, state, history, delivery):
    adapters = NodeAdapters(storage, http)
    pipeline = DailyPipeline(adapters.storage, source, llm)
    scheduler = Scheduler(state, history, pipeline, delivery.send_digest)
    return scheduler.run(config["date"])


if __name__ == "__main__":
    raise SystemExit("fixture composition requires injected adapters")
