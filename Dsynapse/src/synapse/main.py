#!/usr/bin/env python
from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start
from synapse.crews.plot_crew.plot_crew import PlotCrew
from synapse.crews.briefing_crew.briefing_crew import BriefingCrew
from synapse.utils.json_cleaner import JSONCleaner
from synapse.utils import JSONExtractor


class Settings(BaseModel):
    location: str
    crimeType: str
    region: str

class States(BaseModel):
    settings: Settings = Field(
        default_factory=lambda: Settings(
            location="",
            crimeType="",
            region="",
        )
    )
    Plot: str = ""
    BriefingInputs: str = ""
    Briefing: str = ""

    


class PlotFlow(Flow[States]):

    @start()
    def Start(self):
        print("Starting Plot Flow")
    
    @listen(Start)
    def generate_Plot(self):
        print("Generating Plot")
        inputs = self.state.settings.model_dump_json()
        result = (
            PlotCrew()
            .crew()
            .kickoff(inputs={"Settings": inputs})
        )

        print("Plot generated", result.raw)
        cleaned_plot = JSONCleaner.clean_json_content(result.raw)
        self.state.Plot = cleaned_plot
        print("Plot saved", self.state.Plot)

    @listen(generate_Plot)
    def save_Plot(self):
        print("Saving Plot")
        with open("Plot.json", "w") as f:
            f.write(self.state.Plot)
    


class BriefingFlow(Flow[States]):

    @start()
    def Start(self):
        print("Starting Briefing Flow")
    
    @listen(Start)
    def extract_Briefing_inputs(self):
        print("Extracting Briefing Inputs")
        # Configure which JSON file to read and which keys/path to extract
        file_path = "Plot.json"
        nested_path = ["bullseyeConcept"]
        keys_to_extract = ["victim", "crime"]

        extractor = JSONExtractor(
            file_path=file_path,
            nested_path=nested_path,
        )
        # Delegate error handling and fallback to extractor
        self.state.BriefingInputs = extractor.extract_keys_or_fallback(
            keys=keys_to_extract,
            fallback_json=self.state.Plot,
        )
        print("Briefing inputs extracted and saved", self.state.BriefingInputs)
    
    @listen(extract_Briefing_inputs)
    def generate_Briefing(self):
        print("Generating Briefing")
        result = (
            BriefingCrew()
            .crew()
            .kickoff(inputs={"Plot": self.state.BriefingInputs})
        )

        print("Briefing generated", result.raw)
        cleaned_briefing = JSONCleaner.clean_json_content(result.raw)
        self.state.Briefing = cleaned_briefing
        print("Briefing saved", self.state.Briefing)

def kickoff():
    plot_flow = PlotFlow()
    plot_flow.kickoff()

    briefing_flow = BriefingFlow()
    briefing_flow.kickoff()


def plot():
    Plot_flow = PlotFlow()
    Plot_flow.plot()


if __name__ == "__main__":
    kickoff()
