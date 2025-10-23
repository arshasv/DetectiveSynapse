from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from typing import List
from synapse.utils.json_cleaner import JSONCleaner
from synapse.utils import JSONExtractor
from synapse.utils.llm import llm
from synapse.utils.llm import gemini_creative
from pathlib import Path

class Tool(BaseModel):
    toolName: str
    purpose: str

class CrimeLocation(BaseModel):
    locationType: str
    specificArea: str

class CrimeEvent(BaseModel):
    timeStamp: str
    event: str

class ExecutionPlan(BaseModel):
    executionTitle: str
    methodology: str
    toolsUsed: List[Tool]
    crimeLocation: CrimeLocation
    crimeTimeline: List[CrimeEvent]
class CrimeExecution(BaseModel):
    ExecutionPlan: ExecutionPlan

class MisdirectionPlan(BaseModel):
    target: str
    action: str

class EvidenceManagement(BaseModel):
    obfuscation: str
    disposal: str

class CoverUpPlan(BaseModel):
    primaryAlibi: str
    misdirectionPlan: MisdirectionPlan
    evidenceManagement: EvidenceManagement

class CrimeCoverUP(BaseModel):
    coverUpPlan: CoverUpPlan


@CrewBase
class CrimeCrew:
    """CrimeCrew crew"""

    agents: List[Agent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def Criminal_master_mind_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['Criminal_master_mind_agent'],
            llm=gemini_creative()
        )

    @task
    def Crime_execution_design(self) -> Task:
        def save_to_json(result):
            with open("Execution_plan.json", "w") as f:
                f.write(result.raw)
            print("Crime execution plan saved to crime_execution.json")

        return Task(
            config=self.tasks_config['Crime_execution_design_task'],
            output_json=CrimeExecution,
            callback=save_to_json
        )

    @task
    def Crime_coverup_plan(self) -> Task:
        return Task(
            config=self.tasks_config['Crime_coverup_plan_task'],
            output_json=CrimeCoverUP,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrimeCrew crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


