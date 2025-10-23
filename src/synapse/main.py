#!/usr/bin/env python
import json
import os
from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start
from synapse.crews.plot_crew.plot_crew import PlotCrew
from synapse.crews.briefing_crew.briefing_crew import BriefingCrew
from synapse.crews.crime_crew.crime_crew import CrimeCrew
from synapse.crews.solution_crew.solution_crew import SolutionCrew
from synapse.crews.narrative_crew.narrative_crew import NarrativeCrew
from synapse.utils.json_cleaner import JSONCleaner
from synapse.utils import JSONExtractor
import json
from typing import Optional
from synapse.utils.region_generator import RegionGenerator

class Settings(BaseModel):
    location: str
    crimeType: str
    region: Optional[str] = None

class States(BaseModel):
    settings: Settings = Field(
        default_factory=lambda: Settings(
            location="",
            crimeType="",
            region="",
        )
    )
    Plot: str = ""
    CrimeInputs: str = ""
    Crime: str = ""
    BriefingInputs: str = ""
    Briefing: str = ""

    Bullseye: str = ""
    ExecutionPlan: str = ""
    CoverupPlan: str = ""
    Solution: str = ""
    Narrative: str = ""

class PlotFlow(Flow[States]):

    @start()
    def Start(self):
        print("Starting Plot Flow")
    @listen(Start)
    def generate_Plot(self):
        print("Generating Plot")
        self.state.settings.region = RegionGenerator.assign_random_region()
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

class CrimeFlow(Flow[States]):

    @start()
    def Start(self):
        print("Starting Crime Flow")
    @listen(Start)
    def extract_crime_inputs(self):
        print("Extracting Crime Inputs")

        with open("Plot.json", "r") as f:
            inputs = json.load(f)
            self.state.CrimeInputs = json.dumps(inputs["bullseyeConcept"])
        print("Crime inputs extracted and saved", self.state.CrimeInputs)

    @listen(extract_crime_inputs)
    def generate_Crime(self):
        print("Generating Crime")
        result = (
            CrimeCrew()
            .crew()
            .kickoff(inputs={"plot": self.state.CrimeInputs})
        )
        print("Crime  generated", result.raw)
        cleaned_crime = JSONCleaner.clean_json_content(result.raw)
        self.state.Crime = cleaned_crime
        print("Crime saved", self.state.Crime)
    @listen(generate_Crime)
    def save_Crime(self):
        print("Saving Crime")
        with open("Coverup_plan.json", "w") as f:
            f.write(self.state.Crime)

class SolutionFlow(Flow[States]):
    @start()
    def Start(self):
        print("Starting Solution Flow")

    @listen(Start)
    def load_json_files(self):
        print("Loading JSON files")
        try:
            # Read Plot.json and store in Bullseye
            with open("Plot.json", "r") as f:
                self.state.Bullseye = f.read()

            # Read Execution_plan.json and store in ExecutionPlan
            with open("Execution_plan.json", "r") as f:
                self.state.ExecutionPlan = f.read()

            # Read Coverup_plan.json and store in CoverupPlan
            with open("Coverup_plan.json", "r") as f:
                self.state.CoverupPlan = f.read()

            print("JSON files loaded successfully")
        except FileNotFoundError as e:
            print(f"Error loading JSON files: {e}")
        except Exception as e:
            print(f"Unexpected error loading JSON files: {e}")

    @listen(load_json_files)
    def generate_Solution(self):
        print("Generating Solution")
        result = (
            SolutionCrew()
            .crew()
            .kickoff(inputs={"Bullseye": self.state.Bullseye, "ExecutionPlan": self.state.ExecutionPlan, "CoverupPlan": self.state.CoverupPlan})
        )
        print("Solution generated", result.raw)
        cleaned_solution = JSONCleaner.clean_json_content(result.raw)
        self.state.Solution = cleaned_solution
        print("Solution saved", self.state.Solution)
    @listen(generate_Solution)
    def save_Solution(self):
        print("Saving Solution")
        with open("Solution.json", "w") as f:
            f.write(self.state.Solution)

class NarrativeFlow(Flow[States]):
    @start()
    def Start(self):
        print("Starting Narrative Flow")
    @listen(Start)
    def load_json_files(self):
        print("Loading JSON files")
        # Read Plot.json and store in Bullseye
        with open("Plot.json", "r") as f:
            self.state.Bullseye = f.read()

        # Read Execution_plan.json and store in ExecutionPlan
        with open("Execution_plan.json", "r") as f:
            self.state.ExecutionPlan = f.read()

        # Read Coverup_plan.json and store in CoverupPlan
        with open("Coverup_plan.json", "r") as f:
            self.state.CoverupPlan = f.read()

        # Read Solution.json and store in Solution
        with open("Solution.json", "r") as f:
            self.state.Solution = f.read()
        print("JSON files loaded successfully")
    @listen(load_json_files)
    def generate_Narrative(self):
        print("Generating Narrative")
        result = (
            NarrativeCrew()
            .crew()
            .kickoff(inputs={"Bullseye": self.state.Bullseye, "ExecutionPlan": self.state.ExecutionPlan, "CoverupPlan": self.state.CoverupPlan,"solution": self.state.Solution})
        )
        print("Narrative generated", result.raw)
        cleaned_narrative = JSONCleaner.clean_json_content(result.raw)
        self.state.Narrative = cleaned_narrative
        print("Narrative saved", self.state.Narrative)
    @listen(generate_Narrative)
    def save_Narrative(self):
        print("Saving Narrative")
        with open("Narrative.json", "w") as f:
            f.write(self.state.Narrative)

def kickoff():
    # plot_flow = PlotFlow()
    # plot_flow.kickoff()

    # crime_flow = CrimeFlow()
    # crime_flow.kickoff()

    # solution_flow = SolutionFlow()
    # solution_flow.kickoff()

    narrative_flow = NarrativeFlow()
    narrative_flow.kickoff()

    # briefing_flow = BriefingFlow()
    # briefing_flow.kickoff()


def plot():
    Plot_flow = PlotFlow()
    Plot_flow.plot()


if __name__ == "__main__":
    kickoff()
