from dataclasses import dataclass


@dataclass
class Digest:
    date: str
    report_path: str


class DailyPipeline:
    def __init__(self, storage, source, llm):
        self.storage = storage
        self.source = source
        self.llm = llm

    def run_for_date(self, date):
        papers = self.source.list_for_date(date)
        selected = self.llm.filter(papers)
        report_path = f"vault/daily/{date}.md"
        self.storage.write(report_path, self.llm.summarize(selected))
        index = self.storage.read_json("vault/papers.json")
        for paper in selected:
            entry = index[paper["id"]]
            entry["dailyReports"] = [report_path]
            entry["summary"] = {"result": paper["result"]}
        self.storage.write_json("vault/papers.json", index)
        return Digest(date=date, report_path=report_path)


class Scheduler:
    def __init__(self, state, history, pipeline, on_completed):
        self.state = state
        self.history = history
        self.pipeline = pipeline
        self.on_completed = on_completed

    def run(self, date):
        self.state.set(date, "running")
        digest = self.pipeline.run_for_date(date)
        self.state.set(date, "completed")
        self.history.append({"date": date, "status": "completed"})
        self.on_completed(digest)
        return digest


class ReadingIndex:
    """status and priority are user-owned; dailyReports and summary are generated."""

    def set_status(self, storage, paper_id, status):
        index = storage.read_json("vault/papers.json")
        index[paper_id]["status"] = status
        storage.write_json("vault/papers.json", index)
