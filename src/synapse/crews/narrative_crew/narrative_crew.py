from pydantic import BaseModel
from typing import List, Optional
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from synapse.utils.llm import gemini_creative
from synapse.utils.save_json import SaveJson


class SuspectDossier(BaseModel):
    characterID: str
    name: str
    gender:str
    roleInStory: str
    biography: str
    statedAlibi: str
    alibiFlaw: str
    trueAction: str
    connectionToCase: str
    initialStatementToPolice: str

class SuspectDossiersOutput(BaseModel):
    suspectDossiers: List[SuspectDossier]

class Clue(BaseModel):
    clueID: str
    clueTitle: str
    clueType: str
    discoveryMethod: str
    discoveryLocation: str
    description: str
    relevance: str
    difficulty: str

class ClueManifest(BaseModel):
    clueManifest: List[Clue]

class PrePostCrimeEvent(BaseModel):
    timestamp: str
    character: str
    action: str
    location: str
    relatedClueID: Optional[str] = None

class CrimeExecutionEvent(BaseModel):
    timestamp: str
    perspective: str
    event: str
    location: str

class MasterTimeline(BaseModel):
    preCrime: List[PrePostCrimeEvent]
    crimeExecution: List[CrimeExecutionEvent]
    postCrime: List[PrePostCrimeEvent]


@CrewBase
class NarrativeCrew():
    """NarrativeCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def Narrative_weaver_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['Narrative_weaver_agent'],
            llm=gemini_creative()
        )

    @task
    def Suspect_dossiers(self) -> Task:
        return Task(
            config=self.tasks_config['Suspect_dossiers_task'],
            output_json=SuspectDossiersOutput,
            callback=lambda result: SaveJson.save_json(result, "Suspect_dossiers.json")
        )

    @task
    def Clue_manifest(self) -> Task:

        return Task(
            config=self.tasks_config['Clue_manifest_task'],
            output_json=ClueManifest,
            depends_on=[self.Suspect_dossiers],
            callback=lambda result: SaveJson.save_json(result, "Clue_manifest.json")
        )

    @task
    def Master_timeline(self) -> Task:

        return Task(
            config=self.tasks_config['Master_timeline_task'],
            output_json=MasterTimeline,
            depends_on=[self.Suspect_dossiers, self.Clue_manifest],
            callback=lambda result: SaveJson.save_json(result, "Master_timeline.json")
        )

    @task
    def Final_case_file(self) -> Task:

        return Task(
            config=self.tasks_config['Final_case_file_task'],
            depends_on=[self.Suspect_dossiers, self.Clue_manifest, self.Master_timeline]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the NarrativeCrew crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )